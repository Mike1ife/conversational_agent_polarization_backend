from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from app.agent.conversation_logger import log_turn
from app.agent.phases import StageController
from app.agent.prompts import OBSERVE_PROMPT, THINK_PROMPT, build_system_prompt
from app.config import settings
from app.agent.state import Stage, SessionState, StateManager
from app.agent.strategies import get_strategy
from app.llm.base import LLMProvider, Message

logger = logging.getLogger(__name__)


class AgentPipeline:
    """Core agent pipeline implementing plan-execute-observe loop."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.state_manager = StateManager()
        self.stage_controller = StageController(llm)

    async def _observe(self, state: SessionState, user_message: str) -> None:
        """Analyze user message and update condition-specific signals."""
        prompt = OBSERVE_PROMPT.format(
            condition=state.strategy,
            stage=state.stage.value,
            stage_turn_count=state.stage_turn_count,
            signals=json.dumps(state.signals),
            user_message=user_message,
        )

        try:
            response = await self.llm.complete(
                messages=[Message(role="user", content=prompt)],
                temperature=0.1,
                max_tokens=512,
            )
            extracted = json.loads(
                response.strip().strip("```json").strip("```")
            )

            # Merge extracted signals into state (only update non-null/non-false values)
            for key, value in extracted.items():
                if value not in (None,):
                    # For booleans: only update if transitioning false→true or setting a value
                    if isinstance(value, bool):
                        if value:
                            state.signals[key] = value
                    elif isinstance(value, int):
                        # Take the max for count fields
                        state.signals[key] = max(state.signals.get(key, 0), value)
                    else:
                        state.signals[key] = value

            # Sync political_party from signals to dedicated state field
            if state.signals.get("political_party") and state.political_party is None:
                state.political_party = state.signals["political_party"]

            state.metadata["last_observation"] = extracted

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Observation extraction failed: %s", e)

    async def _think(self, state: SessionState, user_message: str) -> str:
        """Internal reasoning step — LLM plans its approach before responding."""
        prompt = THINK_PROMPT.format(
            condition=state.strategy,
            stage=state.stage.value,
            stage_turn_count=state.stage_turn_count,
            signals=json.dumps(state.signals),
            user_message=user_message,
        )
        try:
            reasoning = await self.llm.complete(
                messages=[Message(role="user", content=prompt)],
                temperature=0.3,
                max_tokens=300,
            )
            logger.debug("Think output: %s", reasoning)
            return reasoning.strip()
        except Exception as e:
            logger.warning("Think step failed: %s", e)
            return ""

    async def _post_observe(self, state: SessionState, assistant_response: str) -> None:
        """Update state after the agent generates a response."""
        state.memory.append({
            "turn": state.turn_count,
            "stage": state.stage.value,
        })

    # Sentinel yielded during blocking pipeline work to signal keep-alive
    KEEP_ALIVE = object()

    def resolve_session_id(self, messages: list[dict], strategy_name: str, session_id: str | None = None) -> str:
        """Return the session ID that process_turn will use, without side effects."""
        if session_id is not None:
            return session_id
        return self.state_manager._compute_session_id(messages, strategy_name)

    async def process_turn(
        self,
        messages: list[dict],
        strategy_name: str,
        session_id: str | None = None,
    ) -> AsyncIterator[str | object]:
        """Process a single conversation turn through the pipeline.

        Yields tokens for streaming response.
        Yields AgentPipeline.KEEP_ALIVE during blocking work so callers
        can send SSE keep-alive comments to prevent connection timeouts.
        """
        # Get or create session state
        state = self.state_manager.get_or_create(
            messages=messages,
            strategy=strategy_name,
            session_id=session_id,
        )

        # Increment stage turn count
        state.stage_turn_count += 1

        # Extract the latest user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg["content"]
                break

        if not user_message:
            yield "Before we get started, could you tell us your political affiliation? Do you identify more with the Republican Party or the Democratic Party?"
            return

        # --- OBSERVE + STAGE EVALUATION ---
        if state.turn_count >= 1:
            import asyncio
            if state.stage == Stage.INTAKE:
                # Observe must complete first so political_party signal is set
                # before evaluate_transition checks it.
                await self._observe(state, user_message)
                stage = await self.stage_controller.evaluate_transition(state, user_message)
            else:
                observe_task = asyncio.create_task(self._observe(state, user_message))
                stage_task = asyncio.create_task(
                    self.stage_controller.evaluate_transition(state, user_message)
                )
                done = asyncio.Event()

                async def _wait_and_signal():
                    await asyncio.gather(observe_task, stage_task)
                    done.set()

                waiter = asyncio.create_task(_wait_and_signal())
                while not done.is_set():
                    try:
                        await asyncio.wait_for(done.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        yield self.KEEP_ALIVE
                await waiter  # propagate exceptions
                stage = stage_task.result()

            # Record how many messages to exclude from LLM history for the intake stage.
            # Computed here (not in _observe) because `messages` is in scope and handles
            # both agent-initiated (extra leading assistant message) and user-initiated flows.
            # +1 accounts for the current response (STAGE_1 opening) not yet in messages.
            if state.political_party and "intake_message_cutoff" not in state.metadata:
                state.metadata["intake_message_cutoff"] = (
                    len([m for m in messages if m["role"] in ("user", "assistant")]) + 1
                )
        else:
            stage = state.stage

        logger.info(
            "Session %s: condition=%s, stage=%s, stage_turn=%d, total_turn=%d",
            state.session_id, state.strategy, stage.value,
            state.stage_turn_count, state.turn_count,
        )

        # Get the fixed strategy/condition for this session
        strategy = get_strategy(state.strategy)

        # --- THINK (optional) ---
        import asyncio
        think_context = ""

        if settings.enable_think and state.turn_count >= 1:
            think_task = asyncio.create_task(self._think(state, user_message))
            done_event = asyncio.Event()

            async def _wait_think():
                await think_task
                done_event.set()

            waiter = asyncio.create_task(_wait_think())
            while not done_event.is_set():
                try:
                    await asyncio.wait_for(done_event.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    yield self.KEEP_ALIVE
            await waiter

            if think_task.done():
                think_context = think_task.result()

        # Build the system prompt
        system_prompt = build_system_prompt(stage, strategy, state)
        if think_context:
            system_prompt += f"\n\n## Internal Reasoning (not visible to user):\n{think_context}"

        # --- EXECUTE ---
        llm_messages = [
            Message(role=msg["role"], content=msg["content"])
            for msg in messages
            if msg["role"] in ("user", "assistant")
        ]

        # Strip the intake exchange from LLM history — the party affiliation is
        # already injected into the system prompt via build_system_prompt.
        intake_cutoff = state.metadata.get("intake_message_cutoff", 0)
        if intake_cutoff:
            llm_messages = llm_messages[intake_cutoff:]

        full_response = []
        async for token in self.llm.stream(
            messages=llm_messages,
            system=system_prompt,
        ):
            full_response.append(token)
            yield token

        # --- POST-OBSERVE ---
        assistant_response = "".join(full_response)
        await self._post_observe(state, assistant_response)
        log_turn(settings.conversations_dir, state, system_prompt, llm_messages, assistant_response)
