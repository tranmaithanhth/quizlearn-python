"""Import TOEIC 700-800 - Day 5 vocabulary into quizlearn-python."""
from pathlib import Path
from database.database import Database
from database.schema import create_tables
from repositories.flashcard_repository import FlashcardRepository
from repositories.study_set_repository import StudySetRepository
from services.study_set_service import StudySetService

TITLE = "TOEIC 700-800 - Day 5"
DESCRIPTION = "30 từ và cụm từ TOEIC mức 700-800 - Ngày 5. Mỗi flashcard gồm nghĩa tiếng Việt, collocation và ví dụ."
CARDS = [('acquisition', 'sự mua lại; sự thu nhận\nCollocation: business acquisition / acquisition cost\nExample: The company completed the acquisition of a smaller competitor.'), ('amend', 'sửa đổi, bổ sung\nCollocation: amend a contract/agreement/policy\nExample: The parties agreed to amend the contract before signing it.'), ('anticipate', 'dự đoán, mong đợi\nCollocation: anticipate demand/problems/changes\nExample: The retailer increased inventory in anticipation of higher demand.'), ('assess', 'đánh giá\nCollocation: assess performance/risk/damage\nExample: The manager will assess employee performance at the end of the month.'), ('attain', 'đạt được\nCollocation: attain a goal/target/standard\nExample: The sales team attained its quarterly target ahead of schedule.'), ('attribute A to B', 'cho rằng A là do B\nCollocation: attribute success to / attribute the increase to\nExample: The company attributed the increase in sales to its new marketing campaign.'), ('benchmark', 'tiêu chuẩn tham chiếu, chuẩn so sánh\nCollocation: industry benchmark / performance benchmark\nExample: The company uses customer satisfaction as a key performance benchmark.'), ('comply with', "tuân thủ\nCollocation: comply with regulations/rules/standards\nExample: All suppliers must comply with the company's safety standards."), ('consolidate', 'hợp nhất, gộp lại\nCollocation: consolidate operations/offices/accounts\nExample: The company plans to consolidate several regional offices.'), ('contingency', 'tình huống dự phòng; phương án dự phòng\nCollocation: contingency plan/fund\nExample: The team prepared a contingency plan for possible delivery delays.'), ('delegate', 'giao phó, ủy quyền\nCollocation: delegate responsibility/tasks/authority\nExample: Managers should delegate routine tasks to qualified staff members.'), ('discontinue', 'ngừng sản xuất, ngừng cung cấp\nCollocation: discontinue a product/service/production\nExample: The manufacturer will discontinue the older model next year.'), ('endorse', 'chứng thực, tán thành, ủng hộ\nCollocation: endorse a proposal/product\nExample: The board endorsed the proposal after reviewing the financial report.'), ('enroll', 'đăng ký tham gia\nCollocation: enroll in a course/program\nExample: Employees may enroll in the training program through the company portal.'), ('entail', 'kéo theo, đòi hỏi\nCollocation: entail additional costs/risks\nExample: Relocating the office would entail significant additional costs.'), ('evaluate', 'đánh giá, xem xét\nCollocation: evaluate performance/options/results\nExample: The committee will evaluate all proposals before making a decision.'), ('exempt', 'được miễn\nCollocation: be exempt from a fee/tax/requirement\nExample: Some applicants are exempt from the registration fee.'), ('forecast', 'dự báo; bản dự báo\nCollocation: sales forecast / forecast demand\nExample: The latest sales forecast predicts stronger demand next quarter.'), ('inaugurate', 'khai trương, chính thức đưa vào hoạt động\nCollocation: inaugurate a facility/branch/building\nExample: The company will inaugurate its new distribution center in November.'), ('incur', 'phát sinh, chịu chi phí hoặc nghĩa vụ\nCollocation: incur costs/expenses/charges/losses\nExample: Customers who cancel late may incur an additional charge.'), ('liable', 'chịu trách nhiệm pháp lý\nCollocation: be liable for damages/costs\nExample: The supplier may be liable for any damage caused during shipment.'), ('offset', 'bù đắp, cân bằng\nCollocation: offset costs/losses/emissions\nExample: Higher online sales helped offset losses at several retail stores.'), ('overdue', 'quá hạn\nCollocation: overdue payment/invoice/balance\nExample: A late fee will be charged on overdue payments.'), ('provision', 'điều khoản; sự cung cấp\nCollocation: contract provision / provision of services\nExample: The contract contains a provision regarding early termination.'), ('rectify', 'khắc phục, sửa chữa lỗi\nCollocation: rectify an error/problem/discrepancy\nExample: The accounting department quickly rectified the billing error.'), ('replenish', 'bổ sung lại, làm đầy lại\nCollocation: replenish inventory/stock/supplies\nExample: The retailer needs to replenish its inventory before the holiday season.'), ('retrieve', 'lấy lại, truy xuất\nCollocation: retrieve data/files/information\nExample: Users can retrieve archived documents through the new system.'), ('stipulate', 'quy định rõ, nêu rõ điều kiện\nCollocation: stipulate that / contract stipulates\nExample: The contract stipulates that payment must be made within thirty days.'), ('terminate', "chấm dứt\nCollocation: terminate a contract/agreement/employment\nExample: Either party may terminate the agreement with thirty days' notice."), ('verify', 'xác minh, kiểm tra tính chính xác\nCollocation: verify information/identity/details\nExample: Please verify all information before submitting the form.')]

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
            print(f'[SKIP] Study Set "{TITLE}" already exists (ID={study_set.id}). No duplicate was created.')
            return
    study_set = service.create_study_set_with_flashcards(
        title=TITLE, description=DESCRIPTION, cards=CARDS
    )
    print("=" * 60)
    print("IMPORT SUCCESSFUL")
    print(f"Study Set   : {study_set.title}")
    print(f"Study Set ID: {study_set.id}")
    print(f"Flashcards  : {len(CARDS)}")
    print(f"Database    : {database_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()