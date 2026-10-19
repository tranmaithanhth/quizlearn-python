"""
Import TOEIC 700-800 - Day 3 vocabulary into quizlearn-python.

Usage:
    1. Copy this file into the root folder of quizlearn-python
       (same folder as main.py).
    2. Close the Quizlet Python app if it is running.
    3. Run:
           python import_toeic_day3.py
    4. Reopen the app. A new Study Set named
       "TOEIC 700-800 - Day 3" will appear.

The script will NOT create a duplicate Study Set if the same title
already exists.
"""

from pathlib import Path

from database.database import Database
from database.schema import create_tables
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_set_repository import StudySetRepository
from services.study_set_service import StudySetService


TITLE = "TOEIC 700-800 - Day 3"
DESCRIPTION = (
    "25 từ vựng TOEIC mức 700-800 - Ngày 3. "
    "Mỗi flashcard gồm nghĩa tiếng Việt, collocation và ví dụ."
)

CARDS = [
    (
        "allocate",
        "phân bổ, cấp phát\n"
        "Collocation: allocate funds/resources\n"
        "Example: The company allocated additional funds to the project."
    ),
    (
        "reimburse",
        "hoàn trả, hoàn lại chi phí\n"
        "Collocation: reimburse travel expenses\n"
        "Example: Employees will be reimbursed for approved travel expenses."
    ),
    (
        "eligible",
        "đủ điều kiện, đủ tiêu chuẩn\n"
        "Collocation: be eligible for\n"
        "Example: Full-time employees are eligible for the annual bonus."
    ),
    (
        "mandatory",
        "bắt buộc\n"
        "Collocation: mandatory training\n"
        "Example: Safety training is mandatory for all new employees."
    ),
    (
        "tentative",
        "tạm thời, dự kiến, chưa chính thức\n"
        "Collocation: tentative schedule/date\n"
        "Example: The tentative date for the conference is October 15."
    ),
    (
        "consecutive",
        "liên tiếp\n"
        "Collocation: consecutive years/days\n"
        "Example: Sales have increased for three consecutive years."
    ),
    (
        "facilitate",
        "tạo điều kiện, làm cho thuận lợi hơn\n"
        "Collocation: facilitate communication/process\n"
        "Example: The new system will facilitate communication between departments."
    ),
    (
        "expedite",
        "đẩy nhanh, xúc tiến\n"
        "Collocation: expedite delivery/process/shipment\n"
        "Example: The supplier agreed to expedite the shipment."
    ),
    (
        "retain",
        "giữ lại, duy trì\n"
        "Collocation: retain employees/customers\n"
        "Example: The company introduced incentives to retain experienced employees."
    ),
    (
        "acquire",
        "mua lại; đạt được, có được\n"
        "Collocation: acquire a company/skill/property\n"
        "Example: The firm plans to acquire a smaller competitor."
    ),
    (
        "discrepancy",
        "sự sai lệch, không khớp, mâu thuẫn\n"
        "Collocation: discrepancy in/between\n"
        "Example: The accountant found a discrepancy in the invoice."
    ),
    (
        "deteriorate",
        "xấu đi, suy giảm\n"
        "Collocation: conditions/service deteriorate\n"
        "Example: Road conditions deteriorated because of the severe weather."
    ),
    (
        "implement",
        "triển khai, thực hiện, áp dụng\n"
        "Collocation: implement a policy/system/plan\n"
        "Example: The company will implement a new security policy next month."
    ),
    (
        "undergo",
        "trải qua, chịu sự tác động của\n"
        "Collocation: undergo renovation/inspection/training\n"
        "Example: The office will undergo extensive renovation in October."
    ),
    (
        "adhere to",
        "tuân thủ, làm theo\n"
        "Collocation: adhere to regulations/guidelines/policy\n"
        "Example: All contractors must adhere to safety regulations."
    ),
    (
        "waive",
        "miễn, bãi bỏ, không yêu cầu thanh toán\n"
        "Collocation: waive a fee/requirement\n"
        "Example: The hotel agreed to waive the cancellation fee."
    ),
    (
        "substantial",
        "đáng kể, lớn, quan trọng\n"
        "Collocation: substantial increase/reduction/amount\n"
        "Example: The company reported a substantial increase in revenue."
    ),
    (
        "prospective",
        "tiềm năng, có khả năng trở thành trong tương lai\n"
        "Collocation: prospective clients/customers/employees\n"
        "Example: The sales team met with several prospective clients."
    ),
    (
        "premises",
        "cơ sở, khuôn viên, địa điểm kinh doanh\n"
        "Collocation: on the premises\n"
        "Example: Smoking is prohibited on the company premises."
    ),
    (
        "vicinity",
        "khu vực lân cận, vùng gần đó\n"
        "Collocation: in the vicinity of\n"
        "Example: Several hotels are located in the vicinity of the convention center."
    ),
    (
        "accommodate",
        "chứa, đáp ứng, sắp xếp chỗ cho\n"
        "Collocation: accommodate guests/participants\n"
        "Example: The conference room can accommodate up to 200 participants."
    ),
    (
        "inventory",
        "hàng tồn kho; danh mục hàng hóa\n"
        "Collocation: inventory levels/inventory management\n"
        "Example: The retailer increased its inventory levels before the holiday season."
    ),
    (
        "incentive",
        "sự khuyến khích, động lực, ưu đãi\n"
        "Collocation: financial incentive/tax incentive\n"
        "Example: Employees are offered financial incentives for exceeding their targets."
    ),
    (
        "outage",
        "sự gián đoạn dịch vụ; mất điện\n"
        "Collocation: power/network outage\n"
        "Example: Production stopped temporarily because of a power outage."
    ),
    (
        "compliance",
        "sự tuân thủ\n"
        "Collocation: compliance with regulations/standards\n"
        "Example: The inspection ensures compliance with safety regulations."
    ),
]


def main():
    base_dir = Path(__file__).resolve().parent
    database_path = base_dir / "data" / "quizlet.db"
    database_path.parent.mkdir(parents=True, exist_ok=True)

    database = Database(database_path)
    create_tables(database)

    study_set_repository = StudySetRepository(database)
    flashcard_repository = FlashcardRepository(database)

    service = StudySetService(
        study_set_repository,
        flashcard_repository,
    )

    # Prevent accidental duplicates.
    existing_sets = service.get_all_study_sets()
    for study_set in existing_sets:
        if study_set.title.strip().lower() == TITLE.lower():
            print(
                f'[SKIP] Study Set "{TITLE}" already exists '
                f'(ID={study_set.id}). No duplicate was created.'
            )
            return

    study_set = service.create_study_set_with_flashcards(
        title=TITLE,
        description=DESCRIPTION,
        cards=CARDS,
    )

    print("=" * 60)
    print("IMPORT SUCCESSFUL")
    print("=" * 60)
    print(f"Study Set : {study_set.title}")
    print(f"Study Set ID: {study_set.id}")
    print(f"Flashcards: {len(CARDS)}")
    print(f"Database   : {database_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
