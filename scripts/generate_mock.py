"""Deterministic mock-data generator (seeded RNG, no API key).

Writes data/mock/*.json — a realistic fictional talent agency. Re-running produces identical
output. This is a DEV TOOL; the application never imports it. Real agencies provide their own
files in the same schema (see data/README.md).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models.domain import (  # noqa: E402
    AgencyDataset,
    AgencyProfile,
    Brand,
    Contact,
    PastPitch,
    RoleType,
    Talent,
    TalentWork,
)

SEED = 42
# Assumed solo-agency roster size for the demo seed. Not an app constraint: the agent ranks
# whatever roster is loaded (see the README "Roster-size assumption").
N_TALENTS = 50
OUT = ROOT / "data" / "mock"

# Shared theme vocabulary so talents, works, brands, and pitches connect semantically.
# theme -> (adjective, descriptive phrase, tags)
THEMES: dict[str, tuple[str, str, list[str]]] = {
    "sustainability": (
        "zero-waste",
        "circular materials and low-impact production",
        ["sustainability", "zero-waste", "eco"],
    ),
    "heritage craft": (
        "heritage",
        "traditional craft reinterpreted for today",
        ["heritage", "craft", "artisanal"],
    ),
    "inclusivity": (
        "inclusive",
        "representation and inclusive casting",
        ["inclusivity", "diversity", "representation"],
    ),
    "wellness": ("restorative", "wellness, slowness and care", ["wellness", "mindful", "slow"]),
    "nightlife": ("after-dark", "club culture and the dancefloor", ["nightlife", "club", "music"]),
    "digital art": (
        "generative",
        "generative and digital-first work",
        ["digital", "generative", "new-media"],
    ),
    "slow fashion": (
        "slow-made",
        "considered, slow fashion",
        ["slow-fashion", "considered", "quality"],
    ),
    "circular design": ("circular", "circular design and reuse", ["circular", "reuse", "upcycle"]),
    "community": (
        "community-led",
        "grassroots community building",
        ["community", "grassroots", "local"],
    ),
    "experimental sound": (
        "experimental",
        "genre-blurring, experimental sound",
        ["experimental", "avant-garde", "sound"],
    ),
    "quiet luxury": ("couture", "quiet luxury and craftsmanship", ["luxury", "premium", "refined"]),
    "youth culture": ("gen-z", "youth culture and subculture", ["youth", "genz", "subculture"]),
    "movement": ("kinetic", "movement, sport and the body", ["sport", "movement", "performance"]),
    "provenance": (
        "seasonal",
        "seasonal produce and provenance",
        ["food", "seasonal", "provenance"],
    ),
    "cultural heritage": (
        "diaspora",
        "cultural identity and diaspora",
        ["culture", "identity", "diaspora"],
    ),
}

CATEGORIES: dict[str, list[str]] = {
    "DJ/producer": ["live set", "residency", "festival headline", "sound installation", "remix"],
    "visual artist": ["exhibition", "mural", "installation", "gallery show", "commission"],
    "chef": ["pop-up dinner", "tasting menu", "collab dinner", "supper club", "cookbook"],
    "photographer": ["editorial shoot", "campaign", "exhibition", "photo book", "portrait series"],
    "fashion designer": ["runway show", "capsule collection", "collab", "pop-up", "lookbook"],
    "choreographer": ["performance", "choreography", "residency", "workshop", "dance film"],
    "illustrator": ["mural", "campaign", "picture book", "collab", "exhibition"],
    "ceramicist": ["collection", "gallery show", "collab", "workshop", "commission"],
    "filmmaker": ["short film", "documentary", "music video", "brand film", "installation"],
    "perfumer": ["scent launch", "bespoke commission", "workshop", "collab", "installation"],
    "florist": ["installation", "event styling", "collab", "workshop", "editorial"],
    "model/creator": ["campaign", "magazine cover", "collab", "ambassadorship", "content series"],
}

PLACES = [
    "Lyon",
    "Paris",
    "Seoul",
    "Lisbon",
    "Berlin",
    "Milan",
    "Copenhagen",
    "Marseille",
    "Kyoto",
    "London",
    "Mexico City",
    "Cape Town",
    "Amsterdam",
    "Tokyo",
]

FIRST = [
    "Léa",
    "Mateo",
    "Amara",
    "Jun",
    "Noor",
    "Sacha",
    "Yara",
    "Diego",
    "Mei",
    "Ousmane",
    "Inès",
    "Tariq",
    "Sora",
    "Camille",
    "Kofi",
    "Lucia",
    "Hana",
    "Émile",
    "Priya",
    "Bo",
    "Salima",
    "Nikolai",
    "Aïcha",
    "Thiago",
    "Wen",
    "Esme",
    "Rami",
    "Freya",
    "Dao",
    "Marco",
    "Zaid",
    "Lila",
    "Kenji",
    "Bianca",
    "Omar",
    "Suki",
    "Théo",
    "Nadia",
    "Ravi",
    "Cleo",
    "Anouk",
    "Dimitri",
    "Fatou",
    "Hugo",
    "Mina",
    "Pablo",
    "Yuki",
    "Sienna",
    "Ander",
    "Talia",
]
LAST = [
    "Mercier",
    "Okafor",
    "Park",
    "Haddad",
    "Rossi",
    "Nakamura",
    "Dubois",
    "Mensah",
    "Costa",
    "Petrova",
    "Diallo",
    "Laurent",
    "Kim",
    "Moreau",
    "Silva",
    "Ferrari",
    "Tan",
    "Bauer",
    "Lefebvre",
    "Adeyemi",
    "Vargas",
    "Choi",
    "Bianchi",
    "Novak",
    "Olsen",
    "Ben Ali",
    "Wong",
    "Garnier",
    "Iqbal",
    "Santos",
    "Reyes",
    "Lindqvist",
    "Achebe",
    "Marchetti",
    "Yamamoto",
    "Bouchard",
    "Khan",
    "Fontaine",
    "Eriksson",
    "Da Silva",
]

BRANDS: list[tuple[str, str, list[str]]] = [
    (
        "L'Oréal",
        "beauty",
        ["sustainability (L'Oréal for the Future)", "inclusive beauty", "science-led innovation"],
    ),
    ("Aesop", "beauty", ["considered design", "sensory retail", "arts patronage"]),
    ("Veja", "footwear", ["sustainability", "supply-chain transparency", "fair-trade materials"]),
    ("Patagonia", "apparel", ["environmental activism", "circularity", "repair over replace"]),
    ("Glossier", "beauty", ["community-led beauty", "inclusivity", "digital-native brand"]),
    ("Hermès", "luxury", ["heritage craftsmanship", "quiet luxury", "artisanal savoir-faire"]),
    ("Nike", "sportswear", ["elite performance", "youth culture", "inclusive sport"]),
    ("On", "sportswear", ["Swiss engineering", "sustainable performance", "movement culture"]),
    ("Spotify", "music tech", ["music culture", "creator economy", "global discovery"]),
    ("Airbnb", "travel", ["belonging anywhere", "local community", "design-led travel"]),
    ("Diptyque", "fragrance", ["Parisian heritage", "artisanal scent", "arts collaboration"]),
    ("Moncler", "luxury fashion", ["alpine heritage", "art collaborations", "craftsmanship"]),
    ("Telfar", "fashion", ["accessibility", "community", "inclusive luxury"]),
    ("Rimowa", "travel goods", ["German engineering", "durability", "heritage design"]),
    ("Ruinart", "champagne", ["maison heritage", "art de vivre", "sustainability"]),
]

TITLES: dict[RoleType, list[str]] = {
    RoleType.CMO: ["Chief Marketing Officer", "VP, Marketing"],
    RoleType.BRAND_MANAGER: ["Brand Manager", "Senior Brand Manager"],
    RoleType.PARTNERSHIPS: [
        "Head of Partnerships",
        "Brand Partnerships Lead",
        "Partnerships Manager",
    ],
    RoleType.COMMS_PR: ["Head of Communications", "PR Director", "Communications Manager"],
    RoleType.EVENTS: ["Head of Events", "Events & Experiences Lead"],
}


def _theme_for_brand(rng: random.Random, pillars: list[str]) -> str:
    """Map a brand to a shared theme key for coherent seed pitches."""
    text = " ".join(pillars).lower()
    for key in THEMES:
        if any(tag in text for tag in THEMES[key][2]) or key.split()[0] in text:
            return key
    return rng.choice(list(THEMES))


def generate() -> AgencyDataset:
    rng = random.Random(SEED)

    agency = AgencyProfile(
        id="agency",
        name="Atelier Lumiere",
        tagline="A boutique talent agency placing artists, makers and performers with the world's brands.",
        brand_voice=(
            "Warm, confident, editorial. Lead with the brand's moment, not our roster. "
            "Concrete and specific over superlatives. Short paragraphs. Never salesy or fawning."
        ),
    )

    names = [f"{f} {ln}" for f in FIRST for ln in LAST]
    rng.shuffle(names)
    theme_keys = list(THEMES)
    categories = list(CATEGORIES)

    talents: list[Talent] = []
    for i in range(N_TALENTS):
        name = names[i]
        category = rng.choice(categories)
        t_themes = rng.sample(theme_keys, k=rng.choice([2, 3]))
        primary = t_themes[0]
        place = rng.choice(PLACES)

        tags = sorted({tag for th in t_themes for tag in THEMES[th][2]} | {category.split("/")[0]})
        interests = [THEMES[th][1].split(",")[0] for th in t_themes]
        values = sorted({THEMES[th][2][0] for th in t_themes})
        angle = (
            f"Known as a {THEMES[primary][0]} {category}; "
            f"{THEMES[t_themes[-1]][1]} runs through the work."
        )
        bio = (
            f"{name} is a {place}-based {category} whose practice centres on "
            f"{THEMES[primary][1]}. {angle}"
        )

        works: list[TalentWork] = []
        for j in range(rng.randint(12, 20)):
            th = primary if rng.random() < 0.55 else rng.choice(t_themes)
            kind = rng.choice(CATEGORIES[category])
            adj, phrase, th_tags = THEMES[th]
            wplace = rng.choice(PLACES)
            year = rng.randint(2017, 2025)
            works.append(
                TalentWork(
                    id=f"t{i:02d}-w{j:02d}",
                    title=f"{adj.capitalize()} {kind} in {wplace}",
                    year=year,
                    kind=kind,
                    description=(
                        f"A {kind} exploring {phrase}. Created in {wplace} ({year}), "
                        f"it leaned into {adj} aesthetics and {THEMES[th][2][1]}."
                    ),
                    tags=th_tags,
                )
            )

        talents.append(
            Talent(
                id=f"t{i:02d}",
                name=name,
                category=category,
                bio=bio,
                interests=interests,
                values=values,
                angle=angle,
                tags=tags,
                works=works,
            )
        )

    brands: list[Brand] = []
    contacts: list[Contact] = []
    cidx = 0
    for i, (bname, industry, pillars) in enumerate(BRANDS):
        bid = f"b{i:02d}"
        brands.append(Brand(id=bid, name=bname, industry=industry, pillars=pillars))
        for _ in range(rng.choice([1, 2])):
            role = rng.choice(list(TITLES))
            cname = names[N_TALENTS + cidx]
            first, last = cname.split(" ", 1)
            contacts.append(
                Contact(
                    id=f"c{cidx:03d}",
                    brand_id=bid,
                    name=cname,
                    title=rng.choice(TITLES[role]),
                    role_type=role,
                    email=f"{first.lower()}.{last.lower().replace(' ', '')}@example.com",
                )
            )
            cidx += 1

    outcomes = ["booked", "meeting", "replied", "ignored"]
    seed_pitches: list[PastPitch] = []
    for i in range(30):
        bname, industry, pillars = rng.choice(BRANDS)
        theme = _theme_for_brand(rng, pillars)
        adj, phrase, _ = THEMES[theme]
        talent = rng.choice(talents)
        outcome = rng.choices(outcomes, weights=[2, 2, 3, 3])[0]
        seed_pitches.append(
            PastPitch(
                id=f"p{i:02d}",
                brand_name=bname,
                brand_industry=industry,
                talent_name=talent.name,
                angle=f"{adj} — {phrase}",
                subject=f"A {adj} moment for {bname} — {talent.name}",
                body=(
                    f"Hi — I saw {bname} leaning into {pillars[0]}. {talent.name}, a {talent.category} "
                    f"we represent, works at exactly that intersection: {phrase}. "
                    f"For an upcoming moment I'd propose a collaboration that brings {adj} energy to "
                    f"your audience. Open to sharing a short deck?"
                ),
                outcome=outcome,
            )
        )

    return AgencyDataset(
        agency=agency,
        talents=talents,
        brands=brands,
        contacts=contacts,
        seed_pitches=seed_pitches,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ds = generate()
    files = {
        "agency.json": ds.agency.model_dump(),
        "talents.json": [t.model_dump() for t in ds.talents],
        "brands.json": [b.model_dump() for b in ds.brands],
        "contacts.json": [c.model_dump(mode="json") for c in ds.contacts],
        "seed_pitches.json": [p.model_dump(mode="json") for p in ds.seed_pitches],
    }
    for fname, payload in files.items():
        (OUT / fname).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(
        f"Wrote {len(ds.talents)} talents, {sum(len(t.works) for t in ds.talents)} works, "
        f"{len(ds.brands)} brands, {len(ds.contacts)} contacts, "
        f"{len(ds.seed_pitches)} seed pitches to {OUT.relative_to(ROOT)}/"
    )


if __name__ == "__main__":
    main()
