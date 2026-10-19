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


TITLE = 'TOEIC 800 Vocabulary small 3'
DESCRIPTION = '40 từ vựng TOEIC trung-cao cấp cho công việc và giao tiếp.'

CARDS = [
    ('bargain', 'món hời; mặc cả'),
    ('catalog', 'danh mục'),
    ('complimentary', 'miễn phí'),
    ('consumer', 'người tiêu dùng'),
    ('discount', 'giảm giá'),
    ('inventory', 'hàng tồn kho'),
    ('merchandise', 'hàng hóa'),
    ('outlet', 'cửa hàng; điểm bán'),
    ('purchase', 'mua; việc mua hàng'),
    ('refund', 'hoàn tiền'),
    ('retailer', 'nhà bán lẻ'),
    ('shipment', 'lô hàng'),
    ('stock', 'hàng tồn; cổ phiếu'),
    ('supplier', 'nhà cung cấp'),
    ('warranty', 'bảo hành'),
    ('wholesale', 'bán buôn'),
    ('receipt', 'biên lai'),
    ('availability', 'tình trạng có sẵn'),
    ('substitute', 'thay thế'),
    ('advertise', 'quảng cáo'),
    ('campaign', 'chiến dịch'),
    ('client', 'khách hàng'),
    ('competitor', 'đối thủ'),
    ('demographic', 'nhóm nhân khẩu'),
    ('endorse', 'chứng thực; ủng hộ'),
    ('launch', 'ra mắt'),
    ('marketplace', 'thị trường'),
    ('publicity', 'sự quảng bá'),
    ('survey', 'khảo sát'),
    ('target', 'nhắm mục tiêu'),
    ('trend', 'xu hướng'),
    ('brand', 'thương hiệu'),
    ('brochure', 'tờ giới thiệu'),
    ('circulation', 'lượng phát hành'),
    ('feedback', 'phản hồi'),
    ('loyalty', 'lòng trung thành'),
    ('promotion', 'khuyến mãi'),
    ('prospective', 'tiềm năng'),
    ('sponsor', 'nhà tài trợ; tài trợ'),
    ('accommodation', 'chỗ ở'),
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
