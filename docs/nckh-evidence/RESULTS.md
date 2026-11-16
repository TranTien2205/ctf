# Kết luận và số liệu kiểm thử — argus

Ngày: 2026-11-16 · Máy tấn công: Kali 192.168.223.216 · Mục tiêu: Ubuntu
22.04.4 LTS tại 192.168.223.221 (máy ảo riêng, Python 3.10.12)

---

## 1. Đã kiểm thử những gì

Bốn ứng dụng mục tiêu trên **một máy riêng biệt**, tấn công qua mạng LAN:

| Ứng dụng | Cổng | Nguồn | Vai trò trong đánh giá |
|---|---|---|---|
| argus-lab (`vulnapp.py`) | 8777 | tự viết | 29 lớp lỗ hổng + nhóm đối chứng, dùng cho CI |
| OWASP Juice Shop | 3000 | bên thứ ba | 118 challenge, có scoreboard máy đọc được |
| bWAPP | 8080 | bên thứ ba | ~100 lỗ hổng PHP/MySQL, cần đăng nhập |
| DVWA | 8081 | bên thứ ba | 10+ lớp × 3 mức, cần đăng nhập |

Ba app bên thứ ba chạy bằng Docker, khởi tạo DB và đăng nhập xong
(`bee/bug`, `admin/password`), điều khiển bằng `~/argus-lab/targets.sh`.

---

## 2. Số liệu đo được

### 2.1 Kết quả theo lớp lỗ hổng

Một lần đo nhất quán, sau khi đã sửa hết các lỗi ở mục 4:

| Ứng dụng | Lớp | Request | Kết quả | Ceiling | Bằng chứng được trích |
|---|---|---:|---|---|---|
| argus-lab | sqli | 15 | **proven** | proven | `$s3cr3t-admin-pw` |
| argus-lab | rce | 3 | **proven** | proven | `uid=1000(lab)` |
| DVWA | sqli | 15 | **proven** | proven | `5f4dcc3b5aa765d61d8327deb882cf99` |
| DVWA | rce | 3 | **proven** | proven | `uid=33(www-data)` |
| DVWA | xss | 1 | candidate | candidate | (đúng ceiling — không có browser) |
| bWAPP | sqli | 20 | **proven** | proven | `6885858486f31043e5839c735d99457f045affd0` |
| bWAPP | rce | 3 | **proven** | proven | `uid=33(www-data)` |
| Juice Shop | sqli | 14 | candidate | proven | chỉ error-based, chưa trích được bảng |

**7/8 ca đạt ceiling của lớp; 74 request toàn bộ.**

Về các bằng chứng trên: `5f4dcc3b5aa765d61d8327deb882cf99` là MD5 của
`password` — mật khẩu băm của `admin` trong bảng `users` của DVWA.
`6885858486f31043e5839c735d99457f045affd0` là SHA1 mật khẩu của `bee` trong
bảng `users` của bWAPP. `uid=33(www-data)` là danh tính tiến trình web
server **trên máy mục tiêu**, kèm nonce của probe. Nói cách khác: cả hai
tiêu chí của thầy đều có bằng chứng là dữ liệu thật lấy từ máy khác.

Trước khi sửa, cùng phép đo này cho **6/8** và các quote là `DOCTYPE`,
`127.0.0.1:` — tức kết luận đúng nhưng bằng chứng vô nghĩa. Mức cải thiện
đo được: 6/8 → 7/8, và bằng chứng từ vô nghĩa thành dữ liệu thật.

Một kết quả phụ đáng ghi, vì nó cho thấy cổng chứng minh vẫn đang từ chối
đúng chỗ: trên bWAPP, quote `bee` và `@MME_IT` (đều là giá trị **thật** lấy
từ bảng `users`) bị chấm `candidate`, vì bWAPP in `Welcome bee` ở thanh
điều hướng và `@MME_IT` ở footer — chúng có trong baseline nên không phân
biệt được "đọc được dữ liệu" với "trang vẫn luôn hiện thế". Chỉ hash mật
khẩu là duy nhất cho lần đọc đó, và đó là thứ được chấm `proven`.

### 2.2 Bộ kiểm thử tự động của hệ thống

| Hạng mục | Số liệu |
|---|---|
| `python -m pytest tests/ -q` | 745 test |
| `python selftest.py` | 160/160 |
| CI | 11 job: 2 hệ điều hành × 5 bản Python + 1 job wheel |
| Mã nguồn | 21.663 dòng package, 16.090 dòng test |
| Lịch sử | 498 commit |

### 2.3 Ground truth độc lập từ Juice Shop

`GET /api/Challenges` — **118 challenge, 1 đã giải**: *"Error Handling —
Provoke an error that is neither very gracefully nor consistently handled"*
(Security Misconfiguration, độ khó 1/6). Trước khi chạy: 0.

Đây là số liệu do **chính ứng dụng mục tiêu** cấp, không phải do argus tự
khai — loại bằng chứng mà một cổng chứng minh tự chấm không thể tự tạo ra.
Con số 1/118 cũng nói thẳng giới hạn: endpoint được chỉ định bằng tay, nên
chỉ chạm tới một phần rất nhỏ.

---

## 3. Kết luận

**3.1. Hai tiêu chí bắt buộc đã đạt trên ứng dụng của bên thứ ba.** RCE
chứng minh bằng output `id` (`uid=33(www-data)` từ DVWA và bWAPP,
`uid=1000(lab)` từ máy mục tiêu); SQLi chứng minh bằng dữ liệu thật
(`5f4dcc3b5aa765d61d8327deb882cf99` — mật khẩu băm MD5 trong bảng `users`
của DVWA). Trước đây cả hai chỉ chứng minh được trên lab tự viết, qua
loopback.

**3.2. Cổng chứng minh làm đúng việc từ chối.** XSS trên DVWA dừng ở
`candidate` vì không có browser nào thực thi nó — hệ thống từ chối tự nâng
cấp kết luận. Đây là hành vi mong muốn, không phải thiếu sót.

**3.3. Mục tiêu bên thứ ba tìm ra lỗi mà lab tự viết không tìm được.**
Trong vài phút sau khi cài, bWAPP làm lộ hai false positive thật trong cổng
chứng minh (mục 4). Lý do: lab tự viết không có khung trang dùng chung và
không hiện version engine — mà cổng cần **cả hai** mới bị lừa. Lab do cùng
người viết công cụ nên thừa hưởng đúng điểm mù của người đó.

**3.4. Bằng chứng cũ không được miễn trừ khi luật siết lại.** Hai session
tạo trước khi sửa, sau khi sửa bị `argus verify` báo `TAMPERED: F01 claims
grade 'proven' but its cited evidence supports 'candidate'`. Tính chất này
đáng nêu trong báo cáo: hệ thống tự bắt lại phán quyết sai của chính nó.

**3.5. Chưa chứng minh được tiêu chí `user → LLM → MCP → tool` đầu-cuối.**
Mọi lần chạy đều do script điều khiển. Đường LLM đã thử thật trên mục tiêu
mới và nhận lỗi API: *"Third-party apps now draw from your extra usage"* —
`llm_calls: 0`. Đây là giới hạn tài khoản, đã đo được, không phải lỗi mã.

---

## 4. Lỗi và hạn chế đã phát hiện — và đã sửa

Mỗi lỗi dưới đây đều được tái hiện trên mục tiêu thật trước khi sửa, và sau
khi sửa đều **trồng lại lỗi** để chắc rằng test bắt được.

### 4.1 Cổng chứng minh chấm `proven` trên khung trang (bWAPP)

Quote `<!DOCTYPE html>` làm lớp `sqli` ra `proven`:
`data store fingerprinted | 5.5.9-1ubuntu in r1` (banner MySQL thật, cùng
endpoint, không phải echo), `the query named its target | users in r12`,
`rows returned | quoted from r12`. Trong khi dòng duy nhất r12 có mà
baseline không có là *"Error: The used SELECT statements have a different
number of columns"* — **UNION đã thất bại**.

Nguyên nhân: không check nào hỏi *bytes được trích có phải là dữ liệu*, và
khung trang có trong mọi response.

Sửa: lớp `sqli` bắt buộc có **control** — một exchange cùng endpoint, đã
được trả lời, request không chứa tên bảng, và body **không** chứa bytes
được trích. Check có tên riêng: *"the rows are not what the page serves
anyway"*.

Giá phải trả: `docs/sample-session` phải tạo lại (F01 giờ nêu thêm baseline
`r1`), và 7 test cũ phải thêm baseline — chúng trung thực hơn, vì
`probe_sqli` luôn gửi baseline đầu tiên trong mọi lần chạy thật.

### 4.2 Cổng chấm `proven` trên một từ trong câu báo lỗi (bWAPP)

Lỗ thứ hai, lọt qua cả bản sửa 4.1: quote `statements` — một từ của chính
câu lỗi — vắng trong baseline nên qua được control.

Sửa: bytes **nằm trong** câu báo thất bại của DBMS thì không phải rows
(`DBMS_FAILED_RE`). Luật này hẹp có chủ đích: tôi đã thử luật rộng hơn
(kiểm tra lỗi trên toàn body) và nó **loại oan** dump thật của DVWA, vì
footer DVWA có chữ "Disabled" vì lý do không liên quan.

### 4.3 Finding `rce` trích bytes vô nghĩa

Đo trên bốn mục tiêu: quote tốt nhất mà hệ thống tự chọn là `DOCTYPE` trên
DVWA và bWAPP, `127.0.0.1:` trên lab — **vô nghĩa ở 3/3 ca**, dù việc thực
thi lệnh là thật mỗi lần. Mọi check của lớp đều nói về *exchange*; excerpt
chỉ cần là bytes thật từ một response nào đó.

Sửa: thêm check bắt buộc *"the quoted bytes are the command output"* —
excerpt phải chứa dòng identity. Sau khi sửa, quote là `uid=1000(lab)`,
`uid=33(www-data)`, `uid=33(www-data)`.

Một hồi quy do chính bản sửa này gây ra, đã phát hiện và xử lý: thêm tên
check vào `required` làm `_witness` **chọn witness khác**, khiến ca "ghép
rce từ hai exchange" tụt từ `unproven` xuống `candidate`. Check về excerpt
là thuộc tính của *trích dẫn*, không phải của *exchange*, nên nó được giữ
trong `spec.required` (để gate kết luận) nhưng loại khỏi tuple dùng để
chọn witness.

### 4.4 `probe_sqli` không nhận ngữ cảnh LIKE

bWAPP inject vào `WHERE title LIKE '%$title%'`. Probe thử ngữ cảnh *quoted*
(`1'`) và *numeric* (`1`), cả hai đều không tạo được ranh giới câu lệnh, nên
dò cột dừng ở 0 và phần extract lặng lẽ lấy số cột mà người gọi nêu (2) để
dựng UNION cho một SELECT 7 cột.

Đo được cách đúng: `iron%' ORDER BY 9-- -` → `Unknown column '9' in 'order
clause'` (dò cột chạy, chặn ở 7); `iron%' UNION SELECT
1,login,password,4,5,6,7 FROM users-- -` → `<td>bee</td>`.

Sửa: thêm họ ngữ cảnh thứ ba — **wildcard** (`argus%'`) — thử sau hai họ cũ,
và họ nào *liệt kê được cột* thì thắng; prefix của phần extract dùng đúng họ
đó. Việc dò cột giờ tự chạy khi có yêu cầu extract, vì phần extract cần số
cột đó (trước đây là opt-in nên mặc định không có).

### 4.4b Tín hiệu lỗi của probe bị đánh bại bởi một trang *nhắc đến* database

Nhưng wildcard một mình chưa đủ, và nguyên nhân sâu hơn nằm ở chỗ khác.
`SQL_ERRORS` nhận ra "engine tự xưng tên" — điều một trang lỗi làm, và cũng
là điều chrome của bWAPP làm: trang search của nó có chữ `SQLite`. Nên
`ORDER BY 1` bị tính là **thất bại** trên một response **giống baseline từng
byte** (similarity 1.000), vòng dò dừng ở n=1, `columns` trả về 0, và phần
extract lặng lẽ lùi về 2 cột người gọi nêu để dựng UNION cho SELECT 7 cột.

Sửa: tín hiệu thất bại là **vi phân so với baseline**, không phải giá trị
tuyệt đối — một pattern lỗi mà *baseline cũng khớp* thì không thể là bằng
chứng thất bại của request này. Đây đúng là họ lỗi của mục 4.1 và 4.2, chỉ
ở tầng probe thay vì tầng cổng chứng minh.

Sau ba bản sửa này: dò ra 7 cột, extract trả về hash SHA1 mật khẩu của `bee`,
và lớp `sqli` của bWAPP đạt `proven`. Đo được: 6/8 → **7/8** ca đạt ceiling.

### 4.5 Hạn chế còn lại, không sửa trong phiên này

- **XSS dừng ở `candidate`** — không có browser trong gói. Đã ghi là cap có
  lý do, không phải lỗi.
- **SSRF dừng ở `candidate`** — không có collector ngoài băng.
- **`disclosure` không có hàng đối chứng** — `probe_disclosure` quét theo
  *origin* chứ không theo path, nên không path nào trên một server phục vụ
  `/.env` ở gốc có thể làm đối chứng.
- **`dos` bị từ chối theo chính sách** của repo.

---

## 5. Phương hướng tiếp theo và biện pháp cải thiện

Xếp theo giá trị cho luận điểm nghiên cứu, không theo độ dễ.

### 5.1 Mở đường LLM — một việc, mở hai khoảng trống

Nạp hạn mức tại `claude.ai/settings/usage`. Đây là việc duy nhất chặn đồng
thời **tiêu chí 1 của thầy** (`user → LLM → MCP → tool` chạy đầu-cuối) và
**chương thực nghiệm** (chưa có trial nào). Driver đã xong và đã thử thật;
lỗi nhận về là lỗi tài khoản, không phải lỗi mã.

Khi mở được, chạy ngay:

```bash
python3 -m argus run http://192.168.223.221:3000 --allow-private \
    --goal "map the surface and confirm real vulnerabilities" --max-turns 40
```

rồi đọc `GET /api/Challenges` để lấy số challenge Juice Shop **tự xác nhận**
đã giải. Đó là cặp số liệu mạnh nhất mà đề tài có thể có.

### 5.2 Đo đúng cách: ground truth thay vì tự khai

Hiện mọi finding đều do argus tự chấm. Ba cách bổ sung đối chứng độc lập:

1. **Juice Shop scoreboard** — có sẵn, máy đọc được, 118 challenge.
2. **bWAPP và DVWA có danh mục lỗ hổng tường minh** (mỗi trang một lỗi), nên
   tính được **recall** với mẫu số thật thay vì mẫu số tự định nghĩa.
3. **So sánh với công cụ sẵn có** (`sqlmap`, `nuclei` — đã cài trên Kali và
   argus đã có `run_external`): cùng mục tiêu, cùng thời lượng, so số lỗ
   hổng tìm được **và** số báo sai. Luận điểm của đề tài là *cổng chứng
   minh giảm báo sai*, nên con số đáng giá nhất là false positive của argus
   so với của sqlmap/nuclei trên cùng mục tiêu.

Đề xuất thiết kế thí nghiệm: 4 mục tiêu × 3 cấu hình (argus đơn, argus team,
sqlmap/nuclei) × 5 lần, báo trung vị — khớp với `docs/EXPERIMENTS.md` đã có.

### 5.3 Cải thiện probe để recall không bị chặn bởi kỹ thuật

Mục 4.4 cho thấy một dạng lỗi chung: probe đoán ngữ cảnh injection, và đoán
sai thì lớp lỗ hổng *không thể* chứng minh dù mục tiêu có lỗi thật. Các bước
tiếp theo cùng loại:

- Thêm ngữ cảnh **ORDER BY / trong dấu ngoặc / JSON body** cho `probe_sqli`
  (wildcard vừa thêm là ca đầu).
- `probe_cmdi` hiện chỉ gửi `id` và `whoami`; năm từ khoá khác
  (`uname/hostname/pwd/ver/cat`) có trong pattern nhưng không probe nào gửi.
- Lớp `xss` cần một browser để lên `proven`. Playwright MCP đã có trong cấu
  hình nhưng phiên này không kết nối được — nối được là mở cap của lớp này.

### 5.4 Viết báo cáo NCKH

Dùng cổng chứng minh làm đóng góp trung tâm, và lấy mục 3.3 làm luận điểm
phương pháp: *mục tiêu của bên thứ ba tìm ra lỗi mà lab tự viết không tìm
được*. Lịch sử 498 commit và CHANGELOG là tư liệu sẵn cho chương phương
pháp; mục 4 của tài liệu này là chương hạn chế.

### 5.5 Việc vệ sinh, nên làm trước khi nộp

- Tắt mục tiêu khi không dùng: `~/argus-lab/stop.sh` và
  `~/argus-lab/targets.sh stop`. Bốn app cố ý có lỗ hổng đang mở trên LAN.
- **Thu hồi GitHub PAT** đã dán trong phiên làm việc, tại
  `github.com/settings/tokens`.
- Xoá PAT cũ dạng văn bản thuần trong `~/.git-credentials`.
