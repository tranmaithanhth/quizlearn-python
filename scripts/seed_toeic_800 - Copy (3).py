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


TITLE = 'TOEIC 800 Vocabulary small 4'
DESCRIPTION = '40 từ vựng TOEIC trung-cao cấp cho công việc và giao tiếp.'

CARDS = [
    ('amenity', 'tiện nghi'),
    ('boarding', 'việc lên máy bay'),
    ('cancellation', 'sự hủy'),
    ('destination', 'điểm đến'),
    ('fare', 'giá vé'),
    ('itinerary', 'lịch trình chuyến đi'),
    ('luggage', 'hành lý'),
    ('occupancy', 'tỷ lệ sử dụng phòng'),
    ('reservation', 'đặt chỗ'),
    ('shuttle', 'xe đưa đón'),
    ('departure', 'khởi hành'),
    ('arrival', 'đến nơi'),
    ('delay', 'sự trì hoãn'),
    ('check-in', 'thủ tục nhận phòng; làm thủ tục'),
    ('vacancy', 'phòng trống; vị trí trống'),
    ('hospitality', 'dịch vụ khách sạn'),
    ('reception', 'quầy lễ tân; sự tiếp đón'),
    ('route', 'tuyến đường'),
    ('transfer', 'chuyển; trung chuyển'),
    ('assemble', 'lắp ráp'),
    ('component', 'linh kiện'),
    ('defective', 'bị lỗi'),
    ('durable', 'bền'),
    ('equipment', 'thiết bị'),
    ('facility', 'cơ sở; nhà xưởng'),
    ('inspection', 'kiểm tra'),
    ('maintenance', 'bảo trì'),
    ('manufacture', 'sản xuất'),
    ('operate', 'vận hành'),
    ('output', 'sản lượng'),
    ('productivity', 'năng suất'),
    ('quality', 'chất lượng'),
    ('renovate', 'cải tạo'),
    ('repair', 'sửa chữa'),
    ('specification', 'thông số kỹ thuật'),
    ('warehouse', 'nhà kho'),
    ('malfunction', 'sự trục trặc'),
    ('installation', 'lắp đặt'),
    ('upgrade', 'nâng cấp'),
    ('access', 'truy cập'),
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
