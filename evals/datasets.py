"""Eval ground-truth datasets. Labels are authored by hand (the human anchor for quality).

Honest caveat: these are synthetic labels, so they measure consistency against our stated
intent, not absolute truth. Real deployment would label on the agency's actual outcomes.
"""

from __future__ import annotations

from pydantic import BaseModel

AGENCY_VOICE = (
    "Warm, confident, editorial. Lead with the brand's moment, not the roster. Concrete and "
    "specific over superlatives. Short paragraphs. Never salesy or fawning."
)

BRIEF_BEAUTY = (
    "Beauty and fragrance brands planning sustainability-led experiential launches this season."
)
BRIEF_SPORT = "Sportswear and performance brands activating youth culture at live events."


class QualificationCase(BaseModel):
    id: str
    brief: str
    brand_name: str
    brand_industry: str
    brand_pillars: list[str]
    expected_fit: bool


QUALIFICATION_CASES: list[QualificationCase] = [
    QualificationCase(
        id="q1",
        brief=BRIEF_BEAUTY,
        brand_name="L'Oréal",
        brand_industry="beauty",
        brand_pillars=["sustainability (L'Oréal for the Future)", "inclusive beauty"],
        expected_fit=True,
    ),
    QualificationCase(
        id="q2",
        brief=BRIEF_BEAUTY,
        brand_name="Veja",
        brand_industry="footwear",
        brand_pillars=["sustainability", "supply-chain transparency"],
        expected_fit=False,
    ),
    QualificationCase(
        id="q3",
        brief=BRIEF_BEAUTY,
        brand_name="Patagonia",
        brand_industry="apparel",
        brand_pillars=["environmental activism", "circularity"],
        expected_fit=False,
    ),
    QualificationCase(
        id="q4",
        brief=BRIEF_SPORT,
        brand_name="Nike",
        brand_industry="sportswear",
        brand_pillars=["elite performance", "youth culture"],
        expected_fit=True,
    ),
    QualificationCase(
        id="q5",
        brief=BRIEF_SPORT,
        brand_name="On",
        brand_industry="sportswear",
        brand_pillars=["sustainable performance", "movement culture"],
        expected_fit=True,
    ),
    QualificationCase(
        id="q6",
        brief=BRIEF_SPORT,
        brand_name="Diptyque",
        brand_industry="fragrance",
        brand_pillars=["Parisian heritage", "artisanal scent"],
        expected_fit=False,
    ),
]


class ProofInput(BaseModel):
    work_id: str
    title: str
    relevance: str


class PitchCase(BaseModel):
    id: str
    brand_name: str
    brand_industry: str
    brand_pillars: list[str]
    contact_name: str
    contact_title: str
    talent_name: str
    talent_category: str
    talent_angle: str
    proof_points: list[ProofInput]
    experiential: list[str]


PITCH_CASES: list[PitchCase] = [
    PitchCase(
        id="p1_grounded",
        brand_name="L'Oréal",
        brand_industry="beauty",
        brand_pillars=["sustainability", "inclusive beauty"],
        contact_name="Jun Bauer",
        contact_title="VP, Marketing",
        talent_name="Ander Khan",
        talent_category="perfumer",
        talent_angle="A restorative perfumer exploring cultural identity and diaspora.",
        proof_points=[
            ProofInput(
                work_id="t09-w08",
                title="Diaspora scent installation, Milan",
                relevance="Used fragrance to map cultural identity and displacement.",
            ),
            ProofInput(
                work_id="t09-w01",
                title="Restorative scent launch, Copenhagen",
                relevance="A slow, mindful launch centred on wellness.",
            ),
        ],
        experiential=["A zero-waste rooftop set for a champagne house that booked."],
    ),
    PitchCase(
        id="p2_grounded",
        brand_name="Nike",
        brand_industry="sportswear",
        brand_pillars=["youth culture", "inclusive sport"],
        contact_name="Sora Tan",
        contact_title="Brand Partnerships Lead",
        talent_name="Léa Mercier",
        talent_category="DJ/producer",
        talent_angle="An after-dark DJ blending heritage instruments with club culture.",
        proof_points=[
            ProofInput(
                work_id="t00-w03",
                title="After-dark festival set, Berlin",
                relevance="High-energy youth-culture moment on a major stage.",
            ),
        ],
        experiential=["A youth-culture activation for a sneaker brand that got a meeting."],
    ),
    PitchCase(
        id="p3_affinity_only",
        brand_name="Aesop",
        brand_industry="beauty",
        brand_pillars=["considered design", "arts patronage"],
        contact_name="Noor Haddad",
        contact_title="Head of Communications",
        talent_name="Mei Park",
        talent_category="ceramicist",
        talent_angle="A ceramicist working in heritage craft and slow, considered design.",
        proof_points=[],  # no proof -> must frame on affinity, no fabricated citations
        experiential=[],
    ),
]


class CalibrationCase(BaseModel):
    """Hand-labeled pitches to validate the judge agrees with human judgment."""

    id: str
    subject: str
    body: str
    allowed_proof: list[ProofInput]
    expected_pass: bool


_ANDER_PROOF = ProofInput(
    work_id="t09-w08",
    title="Diaspora scent installation, Milan",
    relevance="Used fragrance to map cultural identity and displacement.",
)


CALIBRATION_CASES: list[CalibrationCase] = [
    CalibrationCase(
        id="cal_good",
        expected_pass=True,
        allowed_proof=[_ANDER_PROOF],
        subject="A scent moment for Diptyque's heritage story",
        body=(
            "Hi Noor — Diptyque's Parisian heritage and your arts collaborations point to a clear "
            "appetite for craft. Ander Khan, a perfumer we represent, recently created an "
            "installation in Milan that used scent to map cultural identity. For an upcoming "
            "moment, a small experiential collaboration could bring that sensibility to your "
            "audience. Worth a short conversation?"
        ),
    ),
    CalibrationCase(
        id="cal_generic",
        expected_pass=False,
        allowed_proof=[],
        subject="Partnership opportunity",
        body=(
            "Hello, we are a leading talent agency with amazing artists. We would love to work "
            "with your incredible brand on an exciting project. Our talent is the best in the "
            "industry and your brand is amazing. Please let us know if you are interested!"
        ),
    ),
    CalibrationCase(
        id="cal_fabricated",
        expected_pass=False,
        allowed_proof=[_ANDER_PROOF],
        subject="Léa Mercier x your brand",
        body=(
            "Hi — Léa Mercier, who we represent, recently headlined the Chanel No.5 global launch "
            "and produced the soundtrack for Nike's Olympic campaign. She'd be perfect for you. "
            "Let's talk."
        ),
    ),
]
