"""
Survey findings and data card content for study conditions.

COMMON_IDENTITY_DATA_CARD
  Text shown to participants in the common_identity condition after the
  exhausted majority concept has been introduced. Replace with the exact
  survey citation when final data is available.
"""

# Placeholder — replace with actual survey citation and wording when available
COMMON_IDENTITY_DATA_CARD = (
    "In a recent national survey, most Americans — across party lines — "
    "said they feel exhausted with political division and don't feel "
    "represented by the most extreme voices."
)

"""
Survey findings for the misperception_correction condition.

Fill in actual values from the source document when available.
Each entry corresponds to one quiz question, in order.

Fields:
  id                    — question key used in session signals ("q1"–"q8")
  label                 — short description of the action (party-neutral, for display)
  survey_average        — mean response on 1–4 scale (1=Never … 4=Definitely); float or None
  pct_never_probably_not — percentage of opposing-party voters who said "never" or
                           "probably not" (0–100); float or None

Scale reference:
  1 = Never
  2 = Probably not
  3 = Probably
  4 = Definitely
"""

QUIZ_QUESTIONS: list[dict] = [
    {
        "id": "q1",
        "label": "Banning FAR-LEFT group rallies in the state capital",
        "survey_average": 2.0,
        "pct_never_probably_not": None,
    },
    {
        "id": "q2",
        "label": "Prosecuting journalists who accuse opposing-party politicians of misconduct",
        "survey_average": 3.0,
        "pct_never_probably_not": None,
    },
    {
        "id": "q3",
        "label": "Reinterpreting the Constitution to block the other party's policies",
        "survey_average": 3.0,
        "pct_never_probably_not": None,
    },
    {
        "id": "q4",
        "label": "Using violence to block major laws passed by the other party",
        "survey_average": 3.0,
        "pct_never_probably_not": None,
    },
    {
        "id": "q5",
        "label": "Reducing voting stations in areas that lean toward the other party",
        "survey_average": 3.0,
        "pct_never_probably_not": None,
    },
    {
        "id": "q6",
        "label": "Ignoring court rulings issued by the other party's judges",
        "survey_average": 3.0,
        "pct_never_probably_not": None,
    },
    {
        "id": "q7",
        "label": "Not accepting the results of a presidential election they lost",
        "survey_average": 3.0,
        "pct_never_probably_not": None,
    },
    {
        "id": "q8",
        "label": "Laws making it easier for their party (and harder for the other party) to win elections",
        "survey_average": 3.0,
        "pct_never_probably_not": None,
    },
]
