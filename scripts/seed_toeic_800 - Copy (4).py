from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.database import Database
from database.schema import create_tables
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_set_repository import StudySetRepository
from services.study_set_service import StudySetService


TITLE = 'TOEIC 800 Vocabulary small 5'
DESCRIPTION = '40 từ vựng TOEIC trung-cao cấp cho công việc và giao tiếp.'

CARDS = [
    ('attachment', 'tệp đính kèm'),
    ('compatible', 'tương thích'),
    ('database', 'cơ sở dữ liệu'),
    ('device', 'thiết bị'),
    ('install', 'cài đặt'),
    ('network', 'mạng'),
    ('password', 'mật khẩu'),
    ('retrieve', 'truy xuất'),
    ('software', 'phần mềm'),
    ('storage', 'lưu trữ'),
    ('update', 'cập nhật'),
    ('backup', 'bản sao lưu'),
    ('security', 'bảo mật'),
    ('technical', 'kỹ thuật'),
    ('wireless', 'không dây'),
    ('efficient', 'hiệu quả'),
    ('innovative', 'đổi mới'),
    ('reliable', 'đáng tin cậy'),
    ('automate', 'tự động hóa'),
    ('accomplish', 'hoàn thành'),
    ('accurate', 'chính xác'),
    ('adequate', 'đầy đủ; thích hợp'),
    ('anticipate', 'dự đoán'),
    ('approximately', 'xấp xỉ'),
    ('consecutive', 'liên tiếp'),
    ('considerable', 'đáng kể'),
    ('decline', 'giảm; từ chối'),
    ('demonstrate', 'chứng minh; trình bày'),
    ('distribute', 'phân phối'),
    ('estimate', 'ước tính'),
    ('exceed', 'vượt quá'),
    ('expand', 'mở rộng'),
    ('fluctuate', 'dao động'),
    ('improve', 'cải thiện'),
    ('maintain', 'duy trì'),
    ('obtain', 'đạt được'),
    ('permit', 'cho phép; giấy phép'),
    ('recommend', 'khuyến nghị'),
    ('resolve', 'giải quyết'),
]


def main() -> None:
    database = Database(BASE_DIR / 'data' / 'quizlet.db')
    create_tables(database)

    study_set_repository = StudySetRepository(database)
    flashcard_repository = FlashcardRepository(database)
    service = StudySetService(
        study_set_repository,
        flashcard_repository,
    )

    existing = [
        study_set
        for study_set in service.get_all_study_sets()
        if study_set.title.strip().casefold() == TITLE.casefold()
    ]

    if existing:
        print(f'Study Set "{TITLE}" đã tồn tại. Không tạo bản trùng.')
        return

    study_set = service.create_study_set_with_flashcards(
        title=TITLE,
        description=DESCRIPTION,
        cards=CARDS,
    )

    print(
        f'Đã tạo "{study_set.title}" với {len(CARDS)} flashcards '
        f'(Study Set ID: {study_set.id}).'
    )


if __name__ == '__main__':
    main()
