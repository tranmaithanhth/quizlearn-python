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


TITLE = 'TOEIC 800 Vocabulary small 2'
DESCRIPTION = '40 từ vựng TOEIC trung-cao cấp cho công việc và giao tiếp.'

CARDS = [
    ('attendee', 'người tham dự'),
    ('conference', 'hội nghị'),
    ('convene', 'triệu tập'),
    ('discussion', 'thảo luận'),
    ('minutes', 'biên bản cuộc họp'),
    ('presentation', 'bài thuyết trình'),
    ('proposal', 'đề xuất'),
    ('schedule', 'lịch trình'),
    ('seminar', 'hội thảo'),
    ('venue', 'địa điểm'),
    ('postpone', 'hoãn'),
    ('reschedule', 'đổi lịch'),
    ('adjourn', 'tạm dừng cuộc họp'),
    ('briefing', 'buổi phổ biến thông tin'),
    ('participate', 'tham gia'),
    ('clarify', 'làm rõ'),
    ('consensus', 'sự đồng thuận'),
    ('outline', 'dàn ý; phác thảo'),
    ('prioritize', 'ưu tiên'),
    ('acquire', 'mua lại; đạt được'),
    ('asset', 'tài sản'),
    ('audit', 'kiểm toán'),
    ('balance', 'số dư'),
    ('billing', 'lập hóa đơn'),
    ('capital', 'vốn'),
    ('commission', 'hoa hồng'),
    ('deficit', 'thâm hụt'),
    ('expense', 'chi phí'),
    ('forecast', 'dự báo'),
    ('fund', 'quỹ; cấp vốn'),
    ('invoice', 'hóa đơn'),
    ('liability', 'khoản nợ; trách nhiệm'),
    ('margin', 'biên lợi nhuận'),
    ('overhead', 'chi phí chung'),
    ('payment', 'thanh toán'),
    ('profit', 'lợi nhuận'),
    ('reimburse', 'hoàn tiền'),
    ('revenue', 'doanh thu'),
    ('transaction', 'giao dịch'),
    ('affordable', 'giá phải chăng'),
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
