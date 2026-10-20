# NCKH — Nghiên cứu xây dựng AI Agent tự động đánh giá lỗ hổng Web

Nhánh `NCKH`. Mã nguồn công cụ dùng chung với `ctf-v2`; thư mục này chứa
**phần nghiên cứu**: problem statement, khảo sát, thiết kế thực nghiệm, kết
quả, báo cáo.

## Luận điểm trung tâm

> Một LLM agent **không đáng tin khi tự đánh giá tiến độ và tự xác minh bằng
> chứng của chính nó**. Đóng góp của đề tài không phải là "một agent giỏi hơn",
> mà là **một lớp điều khiển và kiểm chứng tất định nằm NGOÀI mô hình**, làm cho
> việc đánh giá lỗ hổng web bằng agent trở nên *có biên* và *kiểm toán được*.

Đây là chỗ đề tài tách khỏi phần lớn công trình hiện có, vốn đo "giải được bao
nhiêu bài" chứ không đo "bao nhiêu kết luận của agent là bịa".

## Bản đồ 6 giai đoạn (theo yêu cầu của GVHD)

| GĐ | Sản phẩm | Thư mục | Trạng thái |
|---|---|---|---|
| 1 | Đề cương 3–5 trang, 8–12 tài liệu, research gap | `01-problem/` | đang làm |
| 2 | Experimental plan + dataset report | `02-method/` | khung đã có |
| 3 | Baseline chạy được + kết quả | `03-baseline/` | chưa |
| 4 | 1–2 giả thuyết cải tiến + ablation | `04-improve/` | chưa |
| 5 | Prototype + phân tích failure case | `05-system/` | chưa |
| 6 | Báo cáo + tài liệu tái lập + slide/demo | `06-report/` | chưa |

Báo cáo tuần: `weekly/` — mỗi tuần một file theo mẫu `weekly/_TEMPLATE.md`.

## Đọc theo thứ tự

1. `01-problem/problem-statement.md` — bài toán, gap, giả thuyết, đóng góp
2. `SCOPE.md` — phần nào của ctf-v2 giữ, phần nào cắt, phần nào phải xây mới
3. `02-method/experimental-plan.md` — dataset, baseline, metric, giao thức đo
4. `01-problem/related-work.md` — kế hoạch khảo sát, 12 ô cần điền
