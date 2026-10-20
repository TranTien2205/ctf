# Đề cương — AI Agent tự động đánh giá lỗ hổng Web

## 1. Bài toán

Kiểm thử bảo mật ứng dụng web hiện vẫn tốn người: scanner tự động (ZAP, Nuclei,
sqlmap…) phát hiện tốt các mẫu đã biết nhưng không **chuỗi** được nhiều bước, còn
chuyên gia thì chuỗi được nhưng không mở rộng quy mô. LLM agent hứa hẹn lấp
khoảng giữa: đọc mã, đặt giả thuyết, gửi probe, đọc phản hồi, đổi hướng.

## 2. Vấn đề thật sự khi dùng LLM agent (quan sát đo được)

Trong quá trình vận hành bộ `ctf-v2` trên các mục tiêu web thật, ba hỏng hóc
lặp lại và **đều không phải lỗi của mô hình ngôn ngữ nói chung, mà là lỗi của
kiến trúc không có lớp kiểm chứng**:

1. **Agent không dừng đúng lúc.** Nó sinh biến thể payload trong cùng một lớp
   lỗi hàng trăm lần vì tự đánh giá là "đang tiến triển".
2. **Agent khẳng định điều nó chưa đo.** Nó trích một "đoạn phản hồi nguyên văn"
   nghe hợp lý nhưng không có trong byte thật. Trước khi `post-probe` bắt buộc
   tham số `--response` và kiểm `evidence` là chuỗi con, cổng xác minh chỉ kiểm
   **hình dạng** của lời khẳng định chứ không kiểm **tính đúng**.
3. **Agent bỏ qua tri thức đã có.** Có bài đã được giải và lưu card trong kho,
   agent vẫn đánh lại từ đầu vì đọc sai output của công cụ truy hồi.

## 3. Research gap

Phần lớn công trình về LLM agent cho pentest/CTF báo cáo **tỉ lệ giải được**
trên một benchmark. Rất ít công trình đo:

- bao nhiêu **hành động bị lãng phí** trước khi tới kết luận,
- bao nhiêu **kết luận là dương tính giả do mô hình bịa bằng chứng**,
- và liệu một **lớp điều khiển tất định bên ngoài mô hình** có cải thiện được
  hai con số đó mà không giảm tỉ lệ phát hiện hay không.

Khoảng trống này quan trọng với kiểm thử bảo mật hơn là với coding agent: một
báo cáo lỗ hổng sai gây tốn kém trực tiếp, và một lỗ hổng bị bỏ sót cũng vậy.

## 4. Giả thuyết

- **H1 (biên hành động).** Bộ điều khiển tất định áp ngân sách probe/thời gian
  theo từng lớp lỗi và một thang leo thang cố định sẽ **giảm số hành động lãng
  phí** so với agent ReAct không ràng buộc, ở mức phát hiện bằng hoặc tốt hơn.
- **H2 (xác minh bằng chứng).** Bắt buộc trích dẫn phải là **chuỗi con của
  phản hồi đã bắt được** sẽ **loại bỏ một lớp dương tính giả đo được** mà
  pipeline dùng LLM-làm-giám-khảo không loại được.
- **H3 (truy hồi kinh nghiệm).** Truy hồi chuỗi khai thác đã kiểm chứng cải
  thiện độ chính xác của probe đầu tiên. *Kết quả sơ bộ đã đo là âm ở mức
  card: `holdout_eval` cho `transfer_rate = 0.0`, `correct_peer_named_rate =
  0.188`.* Giả thuyết cần phát biểu lại ở mức **họ cơ chế** thay vì mức card.

## 5. Đóng góp dự kiến

1. **Kiến trúc tách lớp**: agent đề xuất — máy xác minh — bộ điều khiển quyết
   định bước kế tiếp, với ranh giới được cưỡng chế bằng mã chứ bằng lời nhắc.
2. **Giao thức đo** phân biệt rõ *đo được* và *suy đoán*, gồm cả kiểm chuỗi con
   cho mọi bằng chứng.
3. **Bộ dữ liệu web có nhãn** kèm **kill map** (lớp đã đo chết + phép đo đã
   loại nó) — dạng nhãn âm hiếm thấy trong các benchmark hiện có.
4. **Ablation** tách riêng đóng góp của ba thành phần: control plane, gate xác
   minh, truy hồi.

## 6. Phạm vi và giới hạn

- Chỉ **ứng dụng web**; không AD, không DFIR, không pwn/crypto/rev (xem `../SCOPE.md`).
- Chỉ mục tiêu **được phép**: lab tự dựng, CTF, môi trường có uỷ quyền.
- Không đóng góp về huấn luyện mô hình; mô hình được coi là hộp đen thay thế được.

## 7. Việc còn thiếu để hoàn thành GĐ1

- [ ] Điền 8–12 tài liệu vào `related-work.md`, mỗi mục ghi rõ *họ đo gì* và
      *họ KHÔNG đo gì* — cột thứ hai mới là chỗ gap nằm.
- [ ] Chốt một phát biểu H3 mới ở mức họ cơ chế.
- [ ] Viết gọn còn 3–5 trang theo mẫu của GVHD.
