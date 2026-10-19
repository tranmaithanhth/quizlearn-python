"""Import reviewed bilingual TOEIC CSV into topic-based QuizLearn study sets.

Steps:
    python scripts/build_toeic_bilingual.py
    python scripts/import_toeic_bilingual.py

This uses NEW deck titles, never overwrites old cards or learning progress.
"""
import csv
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database.database import Database
from database.schema import create_tables
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_set_repository import StudySetRepository
from services.study_set_service import StudySetService

SOURCE = ROOT / "data_import" / "toeic_2000_bilingual.csv"
DB_PATH = ROOT / "data" / "quizlet.db"
FIELDS = ("topic", "term", "meaning_vi", "part_of_speech", "example_en", "example_vi")


def read_validated_cards():
    if not SOURCE.is_file():
        raise SystemExit(
            "Chưa có bộ từ song ngữ. Chạy trước: python scripts/build_toeic_bilingual.py"
        )
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        data = list(csv.DictReader(handle))
    if len(data) != 2000:
        raise SystemExit(f"Số từ không hợp lệ: {len(data)} (cần 2000).")
    seen = set()
    groups = OrderedDict()
    for row in data:
        if any(not (row.get(col) or "").strip() for col in FIELDS):
            raise SystemExit(f"Thiếu dữ liệu ở thẻ {row.get('term')!r}; không nhập.")
        word = row["term"].strip()
        if word.casefold() in seen:
            raise SystemExit(f"Từ trùng: {word}.")
        seen.add(word.casefold())
        groups.setdefault(row["topic"], []).append(row)
    return groups


def main():
    groups = read_validated_cards()  # check entire file BEFORE writing database
    db = Database(DB_PATH)
    create_tables(db)
    set_repo = StudySetRepository(db)
    card_repo = FlashcardRepository(db)
    service = StudySetService(set_repo, card_repo)
    existing = {
        item.title.strip().casefold()
        for item in service.get_all_study_sets()
    }
    inserted = 0
    for topic, rows in groups.items():
        # Stable deck names for safe re-runs.
        title = f"TOEIC Song Ngữ - {topic}"
        if title.casefold() in existing:
            print(f"Đã tồn tại, bỏ qua: {title}")
            continue
        cards = []
        for row in rows:
            definition = (
                f"Nghĩa: {row['meaning_vi'].strip()}\n"
                f"Từ loại: {row['part_of_speech'].strip()}\n\n"
                f"Ví dụ: {row['example_en'].strip()}\n"
                f"Dịch: {row['example_vi'].strip()}"
            )
            cards.append((row["term"].strip(), definition))
        result = service.create_study_set_with_flashcards(
            title=title,
            description=(
                f"{topic} · {len(cards)} thẻ · TOEIC Part 5/6/7. "
                "Bản dịch và ví dụ tạo tự động cần được rà soát khi học."
            ),
            cards=cards,
        )
        inserted += len(cards)
        existing.add(title.casefold())
        print(f"Đã tạo: {result.title} ({len(cards)} thẻ)")
    print(f"Hoàn thành. Đã thêm {inserted} thẻ mới, giữ nguyên dữ liệu cũ.")


if __name__ == "__main__":
    main()
