import unittest

from scripts.build_toeic_bilingual import (
    SPECIAL_EXAMPLES,
    TOPICS,
    example_for,
    pos_for,
    topic_for,
)


class TOEICBilingualBuilderTests(unittest.TestCase):
    def test_business_topics(self):
        cases = {
            "applicant": "Tuyển dụng và nhân sự",
            "contract": "Hợp đồng và pháp lý",
            "invoice": "Kế toán và tài chính",
            "shipment": "Vận chuyển và kho vận",
            "reservation": "Khách sạn và du lịch",
            "agenda": "Họp và thông báo công việc",
        }
        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(topic_for(word), expected)

    def test_topic_names_are_unique(self):
        names = [name for name, _ in TOPICS]
        self.assertEqual(len(names), len(set(names)))

    def test_curated_example_contains_target_word(self):
        for word, sample in SPECIAL_EXAMPLES.items():
            with self.subTest(word=word):
                self.assertIn(word.lower(), sample.lower())

    def test_existing_english_sentence_is_kept(self):
        sentence = "The receptionist confirmed the reservation."
        self.assertEqual(
            example_for("reservation", sentence, "noun", "Hotel"), 
            SPECIAL_EXAMPLES["reservation"],
        )

    def test_part_of_speech_present(self):
        self.assertEqual(pos_for("applicant", ""), "noun")
        self.assertEqual(pos_for("comply", ""), "verb")
        self.assertEqual(pos_for("reliable", ""), "adjective")


if __name__ == "__main__":
    unittest.main()
