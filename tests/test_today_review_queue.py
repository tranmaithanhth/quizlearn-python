import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from database.database import Database
from database.schema import create_tables
from models.flashcard import Flashcard
from models.study_progress import STATUS_MASTERED
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_progress_repository import StudyProgressRepository
from repositories.study_set_repository import StudySetRepository
from services.study_progress_service import StudyProgressService
from services.study_set_service import StudySetService


class TodayReviewQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        db = Database(Path(self.temp.name) / "quiz.db")
        create_tables(db)
        self.set_repo = StudySetRepository(db)
        self.card_repo = FlashcardRepository(db)
        self.progress_repo = StudyProgressRepository(db)
        self.service = StudyProgressService(
            self.progress_repo, self.card_repo, self.set_repo
        )
        self.study_set = StudySetService(self.set_repo, self.card_repo).create_study_set(
            "Daily TOEIC", ""
        )

    def tearDown(self):
        self.temp.cleanup()

    def card(self, term):
        return self.card_repo.create(
            Flashcard(id=None, set_id=self.study_set.id, term=term, definition="meaning")
        )

    def test_due_cards_precede_new_and_future_cards_stay_out(self):
        now = datetime(2026, 10, 19, 12, 0, 0)
        due = self.card("overdue")
        future = self.card("not due")
        first_new = self.card("new one")
        self.card("new two")
        p = self.service.get_or_create_for_flashcard(due.id)
        p.review_count = 2
        p.status = STATUS_MASTERED
        p.next_review = now - timedelta(days=1)
        self.progress_repo.update(p)
        p = self.service.get_or_create_for_flashcard(future.id)
        p.review_count = 2
        p.next_review = now + timedelta(days=1)
        self.progress_repo.update(p)

        queue = self.service.build_today_queue(
            self.study_set.id, new_limit=1, review_limit=5, now=now
        )
        self.assertEqual([c.id for c in queue], [due.id, first_new.id])
        # MASTERED does not mean excluded from reviews forever.
        summary = self.progress_repo.get_summary_by_set_id(self.study_set.id)
        self.assertGreaterEqual(summary["due"], 1)

    def test_new_card_limit(self):
        for number in range(30):
            self.card("term " + str(number))
        queue = self.service.build_today_queue(
            self.study_set.id, new_limit=15, review_limit=100
        )
        self.assertEqual(len(queue), 15)

    def test_negative_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.build_today_queue(self.study_set.id, new_limit=-1)


if __name__ == "__main__":
    unittest.main()
