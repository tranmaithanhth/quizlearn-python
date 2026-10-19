from pathlib import Path
from database.database import Database
from database.schema import create_tables
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_set_repository import StudySetRepository
from services.study_set_service import StudySetService

TITLE = "TOEIC 750-850 - Day 8"
DESCRIPTION = "30 từ và cụm từ TOEIC Reading mức 750-850 - Ngày 8. Mỗi flashcard gồm nghĩa tiếng Việt, collocation và ví dụ."
CARDS = [('accrue', 'tích lũy, phát sinh dần\nCollocation: accrue interest/benefits\nExample: Employees accrue additional benefits after five years of service.'), ('adequate', 'đầy đủ, thích hợp\nCollocation: adequate funding/resources\nExample: The project cannot begin until adequate funding is secured.'), ('affiliated', 'có liên kết, trực thuộc\nCollocation: affiliated company/organization\nExample: The hotel offers discounts to employees of affiliated companies.'), ('aggregate', 'tổng hợp; tổng số\nCollocation: aggregate data/cost\nExample: The report presents aggregate sales data from all regional offices.'), ('allocate', 'phân bổ\nCollocation: allocate funds/resources\nExample: The board allocated additional funds to the research department.'), ('arbitrary', 'tùy tiện\nCollocation: arbitrary decision/limit\nExample: The committee rejected the arbitrary change to the selection criteria.'), ('capacity', 'công suất, khả năng chứa\nCollocation: production capacity\nExample: The factory is currently operating at full production capacity.'), ('complimentary', 'miễn phí, tặng kèm\nCollocation: complimentary service/breakfast\nExample: Guests receive complimentary coffee and tea during the conference.'), ('consecutive', 'liên tiếp\nCollocation: consecutive days/months\nExample: Sales increased for three consecutive months.'), ('consensus', 'sự đồng thuận\nCollocation: reach a consensus\nExample: The committee reached a consensus after several hours of discussion.'), ('constitute', 'cấu thành\nCollocation: constitute a violation/risk\nExample: Repeated failure to follow the policy may constitute a violation.'), ('deteriorate', 'xấu đi, xuống cấp\nCollocation: conditions/quality deteriorate\nExample: The condition of the equipment has deteriorated significantly.'), ('discretion', "quyền tự quyết\nCollocation: at the manager's discretion\nExample: Refunds after the deadline are issued at the manager's discretion."), ('eligible', 'đủ điều kiện\nCollocation: eligible for reimbursement/benefits\nExample: Full-time employees are eligible for travel reimbursement.'), ('enclose', 'đính kèm\nCollocation: enclose a document/receipt\nExample: Please enclose a copy of the receipt with your application.'), ('exempt', 'được miễn\nCollocation: exempt from a fee/tax\nExample: Senior members are exempt from the annual registration fee.'), ('implication', 'hệ quả, ý nghĩa kéo theo\nCollocation: financial/legal implications\nExample: The committee discussed the financial implications of the proposal.'), ('incidental', 'phát sinh phụ\nCollocation: incidental expenses/costs\nExample: Employees may claim reasonable incidental expenses during business trips.'), ('incentive', 'ưu đãi, động lực\nCollocation: financial incentive\nExample: The company introduced a financial incentive to improve productivity.'), ('inclusive', 'bao gồm, đã gồm trong giá\nCollocation: inclusive of tax/fees\nExample: The conference fee is inclusive of lunch and course materials.'), ('inventory', 'hàng tồn kho\nCollocation: inventory levels/management\nExample: The retailer checks inventory levels at the end of each week.'), ('mandatory', 'bắt buộc\nCollocation: mandatory training/requirement\nExample: Safety training is mandatory for all factory employees.'), ('negligible', 'không đáng kể\nCollocation: negligible impact/cost\nExample: The repair had a negligible effect on production.'), ('provisional', 'tạm thời, sơ bộ\nCollocation: provisional schedule/date\nExample: A provisional schedule will be distributed before the final program is confirmed.'), ('recur', 'tái diễn\nCollocation: problem/error recur\nExample: The technician replaced the component to prevent the problem from recurring.'), ('restrict', 'hạn chế\nCollocation: restrict access/use\nExample: The company will restrict access to confidential records.'), ('subsidize', 'trợ cấp, hỗ trợ chi phí\nCollocation: subsidize transportation/training\nExample: The company subsidizes public transportation costs for employees.'), ('substantial', 'đáng kể, lớn\nCollocation: substantial increase/reduction\nExample: The company reported a substantial increase in quarterly revenue.'), ('tentative', 'dự kiến, chưa chính thức\nCollocation: tentative date/schedule\nExample: The tentative opening date is November 15.'), ('unanimous', 'nhất trí hoàn toàn\nCollocation: unanimous decision/approval\nExample: The board made a unanimous decision to approve the merger.')]

def main():
    base_dir = Path(__file__).resolve().parent
    database_path = base_dir / "data" / "quizlet.db"
    database_path.parent.mkdir(parents=True, exist_ok=True)

    database = Database(database_path)
    create_tables(database)

    study_set_repository = StudySetRepository(database)
    flashcard_repository = FlashcardRepository(database)
    service = StudySetService(study_set_repository, flashcard_repository)

    for study_set in service.get_all_study_sets():
        if study_set.title.strip().lower() == TITLE.lower():
            print(f'[SKIP] Study Set "{TITLE}" already exists.')
            return

    study_set = service.create_study_set_with_flashcards(
        title=TITLE,
        description=DESCRIPTION,
        cards=CARDS,
    )

    print("IMPORT SUCCESSFUL")
    print(f"Study Set: {study_set.title}")
    print(f"Flashcards: {len(CARDS)}")
    print(f"Database: {database_path}")

if __name__ == "__main__":
    main()
