# Bộ TOEIC 2.000 từ — bản xây dựng lại

## Mục tiêu

* 2.000 mục từ duy nhất, ưu tiên từ vựng công sở, kinh doanh, vận chuyển, khách sạn và các tình huống trong TOEIC Reading Part 5/6/7.
* Mỗi thẻ có **nghĩa tiếng Việt, từ loại, ví dụ tiếng Anh và dịch ví dụ sang tiếng Việt**.
* Chia thành các bộ theo chủ đề, giữ nguyên bộ cũ và lịch ôn cũ.
* Kiểm tra đầy đủ 2.000 mục trước khi nhập vào cơ sở dữ liệu.

## Cách chạy trên Windows

Mở CMD tại thư mục gốc dự án:

```bat
git pull origin main
python scripts/build_toeic_bilingual.py
python scripts/import_toeic_bilingual.py
python main.py
```

**Chú ý:** bước build cần kết nối Internet. Quá trình dịch khoảng 1.800 nghĩa từ và 2.000 ví dụ có thể mất khá lâu; kết quả dịch được lưu đệm, có thể chạy lại sau khi bị gián đoạn. Trình dịch dùng endpoint công khai *không chính thức* của Google Translate, có thể từ chối truy cập hoặc thay đổi. Nếu dịch thất bại, chương trình **không tạo file hoàn chỉnh giả** và **không thay đổi dữ liệu học**. Thay vì bỏ qua lỗi, hãy chạy lại khi kết nối ổn định.

Khi hoàn thành, bạn sẽ thấy:

* `data_import/toeic_2000_bilingual.csv` — toàn bộ nghĩa, ví dụ, dịch, từ loại và chủ đề.
* Các bộ mới trong QuizLearn, bắt đầu bằng `TOEIC Song Ngữ -`.

## Ví dụ cấu trúc một thẻ

**Mặt trước:** `invoice`

**Mặt sau:**
- Nghĩa: hóa đơn
- Từ loại: noun
- Ví dụ: Please pay the invoice within thirty days.
- Dịch: Vui lòng thanh toán hóa đơn trong vòng ba mươi ngày.

## Về độ chính xác của dữ liệu

* 200 nghĩa tiếng Việt ban đầu được giữ từ danh sách hiện có.
* 1.800 nghĩa còn lại được dịch tự động từ định nghĩa tiếng Anh.
* Ví dụ ưu tiên câu biên soạn riêng cho các thuật ngữ công việc cốt lõi, sau đó mới dùng ví dụ sẵn có trong dữ liệu nguồn. Một số từ thiếu ví dụ phù hợp sẽ nhận câu mẫu tự động — những câu này cần rà soát thủ công trước khi dùng làm tài liệu chuẩn.
* **Đây chưa phải bộ biên soạn sư phạm được thẩm định toàn bộ 2.000 mục**. Các từ bổ trợ không nên được coi đều là từ trọng tâm TOEIC. Công cụ phân nhóm giúp lọc học theo chủ đề, nhưng không thay thế việc tuyển chọn/hiệu đính chuyên môn.
* Các nghĩa tự động có thể chưa đúng với ngữ cảnh TOEIC; hãy chỉnh lại thẻ khi gặp lỗi.

## Nguồn và bản quyền

Phần dữ liệu tiếng Anh mở rộng được tham khảo từ [ciwga/Oxford3000_Vocab](https://github.com/ciwga/Oxford3000_Vocab), dự án công bố MIT License, © 2024 Mustafa D. Tài liệu này ghi nhận nguồn cùng điều kiện lưu thông báo bản quyền của MIT License; mã nguồn và dữ liệu dẫn xuất cần duy trì thông báo bản quyền/giấy phép liên quan khi phân phối.

## Vì sao không ghi đè bộ cũ?

Các bộ đã được học có lịch ôn lưu trong `study_progress`. Nếu thay nội dung tại cùng ID mà không có quy trình di chuyển tiến độ, lịch học có thể trở nên sai lệch. Do đó, bộ song ngữ nhập vào dưới tên **mới**, không cập nhật hay xóa các bộ trước.
