# Phạm vi — ctf-v2 giữ gì, cắt gì, xây gì

Đo trên cây mã ngày tạo nhánh. **70/73 chain card thuộc category `web`**, nên
phần lõi vốn đã đúng đề tài; thứ "thừa" là các nhánh phụ bám vào sau.

## GIỮ — đây là đóng góp khoa học, không phải tiện ích

| Thành phần | Dòng | Vai trò trong nghiên cứu |
|---|---|---|
| `tools/decide.py` | 599 | **Control plane**: ngân sách 5 probe / 15 phút mỗi lớp lỗi, 25 probe / 45 phút mỗi mục tiêu, thang leo thang 6 nấc. Đây là biến độc lập của H1. |
| `tools/hooks.py` | 311 | **Verification gate**: `post-probe --verdict confirms` bắt buộc `--response` và kiểm `evidence` là chuỗi con của response thật. Biến độc lập của H2. |
| `tools/chain_match.py` | 770 | **Retrieval** kinh nghiệm đã giải. Biến độc lập của H3. |
| `tools/classify.py` | 540 | Phân lớp lỗ hổng từ tín hiệu, có trọng số theo độ hiếm. |
| `tools/subagent_fanout.py` | 1068 | Điều phối đa agent theo họ lỗi. |
| `tools/state.py` | 206 | Sổ giả thuyết — nguồn dữ liệu cho mọi phép đo. |
| `tools/web/*` | 12 file | Primitive đo đạc web, mỗi cái tự emit đúng shape mà gate cần. |
| `knowledge/bug-classes.json` | 32 lớp | Taxonomy. |
| `knowledge/chains/` | 73 card (70 web) | **Ground truth**: chuỗi khai thác đã kiểm chứng. |
| `solved/` | 60 writeup | Ancestry bằng chứng cho từng card. |
| `knowledge/attempts/` | 5 kill map | **Negative ground truth** — hiếm và quý: lớp đã đo chết kèm phép đo. |
| `challenges/` | 134 handout | Nguồn tạo bộ dữ liệu. |

## GIỮ — hạ tầng đo lường (chính là "metric" GĐ2 thầy yêu cầu)

`tools/system_eval.py` (123), `observation_eval.py` (89),
`chain_match_eval.py` (315), `holdout_eval.py` (209), `evaluate.py` (36).

`holdout_eval.py` đáng chú ý nhất: nó đã cho một **kết quả âm được đo đạc** —
`transfer_rate` của truy hồi card sang bài chưa gặp là **0.0**, còn
`correct_peer_named_rate` là **0.188**. Một negative result đo được là tài sản
của paper, không phải thất bại.

## CẮT khỏi phạm vi nghiên cứu (vẫn để nguyên trong `ctf-v4`, không xoá)

| Thành phần | Số lượng | Vì sao ngoài phạm vi |
|---|---|---|
| `tools/ad/` | 9 file | Attack-defense là bài toán **phòng thủ + SLA**, khác hẳn "đánh giá lỗ hổng". |
| `tools/forensics/` | 8 file | DFIR — điều tra artifact, không phải kiểm thử web. |
| `tools/crypto/`, `tools/pwnstatic/` | 19 file | Ngoài "Web". |
| agent `ctf-{crypto,pwn,rev,osint,misc}-*` | 20 agent | Ngoài "Web". |
| agent `ctf-dfir-*`, `ad-*` | 13 agent | Ngoài "Web". |
| skill ngoài web | 26 skill | Ngoài "Web". |

**Cách cắt: bằng cấu hình, không bằng `rm`.** Nghiên cứu cần tái lập được; xoá
file làm hỏng lịch sử và làm gate đỏ. Thay vào đó khai báo một *profile* chỉ
nạp phần web, và báo cáo rõ phần nào bị loại khỏi thực nghiệm.

## XÂY MỚI — đây là việc thật của GĐ 2–3

1. **Bộ dữ liệu chuẩn có ground truth.** `challenges/` là handout thật nhưng
   không phải benchmark: không nhãn thống nhất, không tái lập bằng một lệnh.
   Cần một bộ mục tiêu dựng được bằng Docker, mỗi mục tiêu có nhãn
   `(lớp lỗ hổng, vị trí, bằng chứng tối thiểu)`.
2. **Baseline không-LLM**: scanner tự động (ZAP/Nuclei/sqlmap…) chạy trên cùng
   bộ dữ liệu — để trả lời "agent có hơn scanner không".
3. **Baseline LLM trần**: một ReAct agent *không* có control plane, *không* có
   verification gate — để cô lập đóng góp.
4. **Harness đo**: chạy N lần, ghi probe, thời gian, token, verdict, và
   **đối chiếu từng verdict với ground truth** để ra TP/FP/FN.
5. **Bộ đếm chi phí**: token và thời gian mỗi mục tiêu — hiện chưa đo.
