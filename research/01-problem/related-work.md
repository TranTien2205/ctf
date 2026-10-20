# Khảo sát — 12 ô cần điền

**Quy tắc: không chép abstract.** Mỗi ô hai câu: *họ đo gì* và *họ không đo gì*.
Cột thứ hai là nơi research gap xuất hiện.

> Danh sách dưới đây là **ứng viên cần tự xác minh**, không phải trích dẫn đã
> kiểm chứng. Xác minh bằng `python3 ../../tools/writeup_search.py "<tên>"`,
> Google Scholar, hoặc trang hội nghị. Ghi lại DOI/URL và năm thật.

## A. LLM agent cho pentest / CTF (ứng viên)
| # | Ứng viên | Đo gì | KHÔNG đo gì | Trạng thái |
|---|---|---|---|---|
| 1 | PentestGPT | | | chưa xác minh |
| 2 | Cybench | | | chưa xác minh |
| 3 | NYU CTF Bench | | | chưa xác minh |
| 4 | InterCode-CTF | | | chưa xác minh |
| 5 | AutoPenBench | | | chưa xác minh |
| 6 | HackSynth | | | chưa xác minh |

## B. Kiến trúc agent & ràng buộc hành vi (ứng viên)
| # | Ứng viên | Đo gì | KHÔNG đo gì | Trạng thái |
|---|---|---|---|---|
| 7 | ReAct | | | chưa xác minh |
| 8 | Reflexion | | | chưa xác minh |
| 9 | SWE-bench (phương pháp benchmark agent) | | | chưa xác minh |

## C. Đánh giá công cụ dò quét web truyền thống (ứng viên)
| # | Ứng viên | Đo gì | KHÔNG đo gì | Trạng thái |
|---|---|---|---|---|
| 10 | OWASP Benchmark | | | chưa xác minh |
| 11 | So sánh DAST (ZAP/Nuclei/…) | | | chưa xác minh |
| 12 | Khảo sát false positive trong SAST/DAST | | | chưa xác minh |

## Câu hỏi phải trả lời được sau khi điền xong
1. Có ai đã đo **hành động lãng phí** của agent chưa? Nếu có, bằng chỉ số nào?
2. Có ai **cưỡng chế bằng mã** rằng bằng chứng phải là chuỗi con của phản hồi
   thật chưa, hay tất cả đều dùng LLM chấm LLM?
3. Benchmark nào có **nhãn âm** (lớp đã loại trừ kèm phép đo), không chỉ nhãn dương?
