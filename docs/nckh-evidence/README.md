# Hồ sơ số liệu NCKH — 2026-11-16

Thư mục này giữ **toàn bộ số liệu và bằng chứng** của lần đo ngày 2026-11-16, để
dùng trực tiếp khi viết báo cáo. Mọi con số trong đây đều lấy từ một lần đo nhất
quán, không phải ước lượng.

## Nên mở cái nào trước

| File | Dùng để làm gì |
|---|---|
| **`presentation.html`** | Trang trình bày trực quan, **tương tác được** — mở thẳng bằng trình duyệt, không cần máy chủ. Mục 02 cho bấm vào từng chuỗi bằng chứng để thấy khối `proof` thật mà cổng ghi ra và kết luận thay đổi theo; mục 03 có nút chuyển số liệu trước/sau khi sửa lỗi. Dành cho cả người hướng dẫn. |
| **`RESULTS.md`** | Báo cáo đầy đủ: đã kiểm thử gì, số liệu, kết luận, lỗi đã sửa, phương hướng. |
| `results.json` / `results.txt` | Số liệu thô của bảng kết quả (8 ca đo). |
| `recording/argus-remote-exploit.cast` | Bản ghi phiên khai thác tự động, phát lại bằng `asciinema play`. `.log` là bản văn bản thuần cùng nội dung. |

## Môi trường đo

Máy tấn công Kali `192.168.223.216`; mục tiêu Ubuntu 22.04.4 LTS tại
`192.168.223.221` (máy ảo riêng, Python 3.10.12). Bốn ứng dụng mục tiêu:

| Ứng dụng | Cổng | Nguồn |
|---|---|---|
| argus-lab (`argus/lab/vulnapp.py`) | 8777 | tự viết, 29 lớp lỗ hổng + nhóm đối chứng |
| OWASP Juice Shop | 3000 | bên thứ ba, 118 challenge có scoreboard |
| bWAPP | 8080 | bên thứ ba, cần đăng nhập `bee/bug` |
| DVWA | 8081 | bên thứ ba, cần đăng nhập `admin/password` |

Phạm vi và uỷ quyền: `AUTHORIZATION.txt`.

## Hồ sơ niêm phong — kiểm tra lại được

`sealed-sessions/` giữ bốn hồ sơ phiên hoàn chỉnh. Mỗi hồ sơ có transcript băm chuỗi,
findings kèm khối `proof` liệt kê từng điều kiện, và báo cáo ở ba định dạng.
Kiểm tra lại bất kỳ hồ sơ nào:

```bash
python -m argus verify docs/nckh-evidence/sealed-sessions/dvwa
```

Lệnh này đi lại cả chuỗi băm **và chấm lại từng finding**: nếu ai sửa một byte
trong transcript, hoặc tự nâng `grade` trong `findings.json`, nó báo `TAMPERED`.

Cả bốn hồ sơ ở đây đã được **tạo lại** sau khi các lỗi ở mục 4 của `RESULTS.md`
được sửa. Bản tạo trước đó báo `TAMPERED` ngay khi luật siết lại — cụ thể là
`F01 claims grade 'proven' but its cited evidence supports 'candidate'`. Đó
chính là tính chất mà mục 3.4 của báo cáo nêu: bằng chứng cũ không được miễn
trừ khi tiêu chuẩn chặt hơn, và nó áp cả vào hồ sơ của chính dự án. Nếu sau này
cổng chứng minh lại siết thêm, các hồ sơ này cũng phải tạo lại chứ không sửa tay.

| Hồ sơ | Nội dung |
|---|---|
| `sealed-sessions/argus-lab/` | 6 finding / 64 request, chế độ một agent |
| `sealed-sessions/argus-lab-team/` | 6 finding / 74 request, chế độ lead + worker |
| `sealed-sessions/dvwa/` | SQLi và command injection trên DVWA, cả hai `proven` |
| `sealed-sessions/bwapp/` | SQLi và command injection trên bWAPP, cả hai `proven` |

## Script đo — chạy lại được

`tools/` giữ đúng các script đã dùng, không phải bản viết lại:

- `measure_all.py` — sinh bảng 8 ca đo trong `results.json`
- `evidence_thirdparty.py` — sinh hồ sơ niêm phong cho DVWA và bWAPP
- `thirdparty_probes.py` — chạy probe trên cả ba app bên thứ ba và in kết quả
- `demo.sh` + `show_proof.py` — kịch bản đã dùng để quay bản ghi

Các script này **chỉ định endpoint bằng tay** — đó là việc mà LLM sẽ làm khi
đường LLM được mở. Nói cách khác chúng đo tầng công cụ và cổng chứng minh, không
phải năng lực tự đánh giá.

## Điều cần nói rõ khi dùng số liệu này

Mọi hồ sơ trong đây đều ghi `model: scripted-demo` hoặc `model: probe-driver`:
**thứ tự công cụ do script quyết định, chưa phải do LLM**. Mọi request HTTP,
mọi payload và mọi byte bằng chứng là thật — chỉ tầng quyết định là script.
Nguyên nhân đã đo được: đường LLM trả về lỗi API
*"Third-party apps now draw from your extra usage"* với `llm_calls: 0`.
`RESULTS.md` mục 3.5 nói chi tiết.
