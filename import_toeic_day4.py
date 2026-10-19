"""
Import TOEIC 700-800 - Day 4 vocabulary into quizlearn-python.

Usage:
    1. Copy this file into the root folder of quizlearn-python
       (same folder as main.py).
    2. Close the Quizlet Python app if it is running.
    3. Run:
           python import_toeic_day4.py
    4. Reopen the app. A new Study Set named
       "TOEIC 700-800 - Day 4" will appear.

The script will NOT create a duplicate Study Set if the same title
already exists.
"""

from pathlib import Path

from database.database import Database
from database.schema import create_tables
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_set_repository import StudySetRepository
from services.study_set_service import StudySetService


TITLE = "TOEIC 700-800 - Day 4"
DESCRIPTION = (
    "25 từ vựng TOEIC mức 700-800 - Ngày 4. "
    "Mỗi flashcard gồm nghĩa tiếng Việt, collocation và ví dụ."
)

CARDS = [
    ("adjacent", "liền kề, sát bên\nCollocation: adjacent to\nExample: The employee parking area is adjacent to Building C."),
    ("ample", "dồi dào, đủ nhiều\nCollocation: ample space/time/opportunity\nExample: The conference room provides ample space for 120 participants."),
    ("applicable", "có thể áp dụng, phù hợp để áp dụng\nCollocation: applicable to\nExample: The revised policy is applicable to all full-time employees."),
    ("authorize", "cho phép, phê duyệt, ủy quyền\nCollocation: authorize payment/purchase/access\nExample: Only department managers may authorize large purchases."),
    ("commence", "bắt đầu, khởi đầu\nCollocation: commence operations/work/construction\nExample: Construction is scheduled to commence in early October."),
    ("compile", "tổng hợp, biên soạn\nCollocation: compile a report/data/list\nExample: The analyst compiled the quarterly sales report."),
    ("conform to", "phù hợp với, tuân theo\nCollocation: conform to standards/regulations/specifications\nExample: All products must conform to international safety standards."),
    ("designate", "chỉ định, xác định cho một mục đích\nCollocation: designated area/representative/space\nExample: Additional parking spaces have been designated for visitors."),
    ("dispose of", "xử lý, loại bỏ, vứt bỏ\nCollocation: dispose of waste/materials/equipment\nExample: Employees must dispose of hazardous materials properly."),
    ("durable", "bền, lâu hỏng\nCollocation: durable materials/products/equipment\nExample: The manufacturer uses durable materials in its products."),
    ("exceed", "vượt quá, vượt mức\nCollocation: exceed expectations/limits/requirements\nExample: Sales exceeded expectations during the first quarter."),
    ("feasible", "khả thi, có thể thực hiện được\nCollocation: feasible solution/plan/option\nExample: The engineering team is evaluating whether the proposal is feasible."),
    ("fluctuate", "dao động, lên xuống\nCollocation: prices/costs/demand fluctuate\nExample: Raw material prices tend to fluctuate throughout the year."),
    ("forthcoming", "sắp tới, sắp diễn ra\nCollocation: forthcoming event/meeting/report\nExample: Details about the forthcoming conference will be announced soon."),
    ("inquiry", "yêu cầu thông tin, câu hỏi, thắc mắc\nCollocation: customer inquiry / respond to an inquiry\nExample: Please direct all customer inquiries to the sales department."),
    ("merchandise", "hàng hóa, sản phẩm bán ra\nCollocation: retail merchandise / damaged merchandise\nExample: Employees who handle merchandise must complete the training."),
    ("negotiate", "đàm phán, thương lượng\nCollocation: negotiate a contract/agreement/price\nExample: The company is negotiating a new contract with the supplier."),
    ("obsolete", "lỗi thời, không còn phù hợp sử dụng\nCollocation: obsolete equipment/technology/system\nExample: The factory replaced several obsolete machines last year."),
    ("prohibit", "cấm, không cho phép\nCollocation: prohibit smoking/use/access\nExample: Company policy prohibits smoking on the premises."),
    ("promptly", "nhanh chóng, kịp thời\nCollocation: respond promptly / report promptly\nExample: Employees should report any discrepancies promptly."),
    ("refrain from", "kiềm chế, tránh làm điều gì\nCollocation: refrain from + V-ing\nExample: Visitors are asked to refrain from using mobile phones in this area."),
    ("relevant", "có liên quan, phù hợp với vấn đề\nCollocation: relevant experience/information/documentation\nExample: Applicants should include all relevant work experience."),
    ("renewal", "sự gia hạn, việc làm mới lại\nCollocation: contract renewal / membership renewal\nExample: The client requested a two-year contract renewal."),
    ("specification", "thông số kỹ thuật, yêu cầu chi tiết\nCollocation: product specifications / technical specifications\nExample: Please review the technical specifications before placing an order."),
    ("surplus", "dư thừa, phần dư\nCollocation: surplus inventory/stock/funds\nExample: The retailer discounted surplus inventory at the end of the season."),
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

    for study_set in service.get_all_study_sets():
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
    print(f"Study Set   : {study_set.title}")
    print(f"Study Set ID: {study_set.id}")
    print(f"Flashcards  : {len(CARDS)}")
    print(f"Database    : {database_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
