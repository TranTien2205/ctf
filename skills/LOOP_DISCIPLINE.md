# LOOP_DISCIPLINE — kỷ luật vòng lặp giải bài

File dùng chung, được mọi skill triage tham chiếu. Mục tiêu: **không cắm chết một
hướng**. Đây là thứ phân biệt "route giỏi" với "giải được".

## 1. Đơn vị công việc = 1 lớp giả thuyết (không phải 1 probe)

Gom probe theo **cơ chế**, không theo biến thể. Ví dụ MCCRAB3: "lách rule bằng
header trick" là MỘT lớp — dù bạn thử 20 biến thể (dup, tab, >127, split-value…)
tất cả vẫn là một lớp. Hết ngân sách lớp → **đổi tầng**, không thử biến thể thứ 21.

Ngân sách mặc định mỗi lớp: **≤ 5 probe** hoặc **≤ 15 phút**. Chạm mốc mà chưa có
**tín hiệu mới** → dừng lớp, ghi "falsified", leo thang.

## 2. Decisive-test-first

Trước khi thử N biến thể, hỏi: *"Có MỘT test nào giết hoặc xác nhận cả lớp không?"*
- Muốn biết proxy có forward byte gốc? → 1 echo-backend test, không cần 20 payload.
- Muốn biết compare là eq hay contains? → đọc 1 hàm decompile, không brute.

Ưu tiên test quyết định. Biến thể chỉ dùng khi test quyết định bất khả thi.

## 3. Escalation ladder (khi một lớp chết)

Leo theo thứ tự, KHÔNG quay lại tầng đã đóng nếu không có bằng chứng mới:

1. **Re-read đề + artifact** — bỏ sót hint/field/route nào? (rule dùng `contains`
   hay `eq`? path/method regex unanchored?)
2. **Đổi tầng cơ chế** — parser → state machine → auth/session → response-side →
   framing → logic app. Liệt kê các tầng CÒN LẠI trước khi đâm sâu tầng hiện tại.
3. **Reverse phần quyết định** — nếu là bài rev/binary, đọc HÀM quan trọng nhất
   bằng decompiler. Đừng để lại đúng đoạn khả nghi nhất "chưa đọc". (Xem rev-triage.)
4. **Kéo tri thức ngoài** — bài LIVE hay CŨ? Được dùng writeup/source không? Bài
   ít solve = có người tìm ra bug bạn chưa thấy → `tools/writeup_search.py`.
5. **Skip, quay lại sau** — trong contest tính giờ, một bài không đáng > time-box.

## 4. Chống độc thoại / flailing

Dấu hiệu đang quẫy (STOP ngay khi thấy): chuỗi "wait wait", đặt >2 giả thuyết mới
trong một lượt mà không test, lặp lại ý đã bác bỏ, tăng độ phức tạp payload mà
không tăng thông tin.

Thay bằng: ghi **hypothesis-ledger** có cấu trúc qua `tools/state.py`
(`--probe`/`--result`/`--close`), mỗi mục = giả thuyết + test quyết định + kết quả
+ tầng kế tiếp. Ledger DẪN quyết định, không phải log cuối buổi.

## 5. Bằng chứng, không niềm tin

- "Đã reverse xong" chỉ đúng khi hàm quyết định đã đọc, không phải "đọc phần lớn".
- Nghi đọc nhầm (hex/offset)? → verify bằng công cụ (decompiler/replica), đừng suy diễn.
- Flag là giả thuyết đến khi verify từ target/artifact.

## 6. Offline replica khi có thể

Bài có binary/service + input? Dựng replica cục bộ (như lab MCCRAB3) để fuzz không
giới hạn thời gian và loại biến nhiễu (LB, instance chết). Test ở replica → chỉ bắn
live payload đã xác nhận.
