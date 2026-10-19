"""Import 2,000 vocabulary entries as four 500-card study sets.

Usage (from repository root):
    python scripts/import_toeic_2000.py

The existing database and other sets are preserved. Re-running the script
skips a deck if it already exists, avoiding duplicate cards.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database.database import Database
from database.schema import create_tables
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_set_repository import StudySetRepository
from services.study_set_service import StudySetService

SOURCE = ROOT / "data_import" / "toeic_2000.csv"
DB_PATH = ROOT / "data" / "quizlet.db"
DECK_SIZE = 500


def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        entries = list(csv.DictReader(handle))
    if len(entries) != 2000:
        raise ValueError(f"Expected 2000 entries, found {len(entries)}")
    words = [item["term"].strip().casefold() for item in entries]
    if len(set(words)) != len(words):
        raise ValueError("Vocabulary source contains duplicate terms.")

    db = Database(DB_PATH)
    create_tables(db)
    set_repo = StudySetRepository(db)
    card_repo = FlashcardRepository(db)
    service = StudySetService(set_repo, card_repo)
    existing = {s.title.strip().casefold() for s in service.get_all_study_sets()}

    for offset in range(0, len(entries), DECK_SIZE):
        part = offset // DECK_SIZE + 1
        title = f"TOEIC 2000 - Part {part:02d} ({offset+1}-{offset+DECK_SIZE})"
        if title.casefold() in existing:
            print(f"Skipped existing set: {title}")
            continue
        cards = []
        for entry in entries[offset:offset + DECK_SIZE]:
            meaning = entry["definition"].strip()
            pos = entry["part_of_speech"].strip()
            example = entry["example"].strip()
            # The app stores two fields per card. Put learning context on
            # separate lines on the back; avoid claiming English is Vietnamese.
            details = [meaning]
            if pos:
                details.append(f"POS: {pos}")
            if example:
                details.append(f"Example: {example}")
            cards.append((entry["term"].strip(), "\n".join(details)))
        created = service.create_study_set_with_flashcards(
            title=title,
            description=(
                "500 entries. The first 200 entries have Vietnamese meanings; "
                "the remaining entries currently have English definitions. "
                "Oxford3000_Vocab source: ciwga/Oxford3000_Vocab (MIT)."
            ),
            cards=cards,
        )
        print(f"Created {created.title}: {len(cards)} cards")
    print("Import complete. Open QuizLearn and choose a TOEIC 2000 deck.")


if __name__ == "__main__":
    main()
