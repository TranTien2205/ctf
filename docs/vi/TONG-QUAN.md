# argus — Tổng quan hệ thống (bản tiếng Việt)

Tài liệu này là bản mô tả hệ thống dùng cho báo cáo nghiên cứu. Mã nguồn, chú
thích trong mã và các tài liệu kỹ thuật (`README.md`, `ARCHITECTURE.md`,
`EVIDENCE_POLICY.md`, `ROADMAP.md`) được viết bằng tiếng Anh một cách có chủ đích:
đó là mặt phẳng điều khiển mà các mô hình đọc, và việc giữ nó thống nhất một ngôn
ngữ làm giảm sai lệch khi mô hình diễn giải quy tắc.

## 1. Vấn đề

Một tác nhân (agent) dùng mô hình ngôn ngữ lớn để kiểm thử xâm nhập thất bại theo
bốn cách khác nhau, và cả bốn đều không phải lỗi của mô hình:

1. **Chạm vào mục tiêu không được phép.** Mô hình bịa ra một hostname, và lệnh đó
   vẫn được thực thi.
2. **Báo cáo lỗ hổng chưa từng chứng minh.** Một nhãn của scanner, một mã
   template, một timeout, một payload được phản chiếu — tất cả đều bị đọc thành
   bằng chứng.
3. **Tiêu tốn cả buổi vào các biến thể payload.** Một giả thuyết đã chết vẫn được
   thử lại dưới hình dạng khác.
4. **Mất mạch khi phiên làm việc dài.** Ngữ cảnh bị nén, bị reset, hoặc chuyển
   sang mô hình khác, và những gì đã đo được biến mất.

Hệ thống này tách thành bốn mặt phẳng, mỗi mặt phẳng làm cho **một** trong bốn
thất bại trên trở thành bất khả thi về mặt cấu trúc, chứ không chỉ là ít xảy ra.

## 2. Mô hình triển khai

Đúng theo sơ đồ `người dùng → LLM → MCP → tool/script`, nhưng có thêm hai lớp
kiểm soát mà sơ đồ gốc không nói tới: cổng *trước khi* chạy lệnh, và cổng *trước
khi* ghi nhận phát hiện.

```
người dùng  ──prompt / skill / workflow──▶  LLM
                                             │  được xem: hợp đồng phiên, bản tóm
                                             │  ngữ cảnh từ ledger, hành động kế
                                             │  tiếp do bộ điều khiển tính ra
                                             ▼
                                       MCP tools/call
                                             ▼
                                 ┌───────────────────────┐
                                 │  broker (tầng tool)   │  phạm vi · mức rủi ro ·
                                 └───────────┬───────────┘  giả thuyết · ngân sách
                                             │  chỉ argv — không có shell
                     ┌───────────────────────▼────────────────────────┐
                     │ nmap · ffuf · nuclei · nikto · sqlmap · curl   │
                     │ playwright · script theo từng CVE             │
                     └───────────────────────┬────────────────────────┘
                                             │  quan sát, đã giới hạn & che bí mật
                                 ┌───────────▼───────────┐
                                 │  ledger (tầng điều    │  bằng chứng được chấm
                                 │  khiển)               │  theo ma trận chứng minh
                                 └───────────┬───────────┘
                                             ▼
                      báo cáo: đã chứng minh · ứng viên · chưa chứng minh
```

Vòng lặp khép lại ở chữ *quan sát*: quyết định kế tiếp của mô hình được tính từ
ledger, không phải từ bản tự tóm tắt của chính nó. Đây là điểm khác biệt giữa một
phiên có thể dừng và tiếp tục bằng mô hình khác, và một phiên không thể.

## 3. Nguyên tắc trung tâm: bằng chứng, không phải lời khẳng định

Mỗi lớp lỗ hổng có một **yêu cầu chứng minh**, và `hooks.py` — con đường ghi duy
nhất — từ chối mọi thứ không đạt yêu cầu đó.

| Lớp | Phải có gì mới được ghi là phát hiện |
|---|---|
| `rce` và các lớp dẫn tới thực thi mã | kết quả của **đúng một** lệnh vô hại `id; echo <nonce>`, với nonce khớp với lần thử. Không reverse shell, không tải payload, không ghi file, không tạo persistence. |
| `sqli` | định danh DBMS **cộng** tối thiểu một dòng của một bảng **được nêu tên**. Năm dòng là chứng minh; dump toàn bộ là một sự cố. |
| `lfi`, `xxe` | một dấu hiệu từ tệp đã biết hình dạng (`/etc/passwd`, `win.ini`), **kèm** phép đối chứng với đường dẫn không thể tồn tại. |
| `ssti` | kết quả số từ bốn chữ số trở lên, do engine tính ra, và biểu thức gốc **không** xuất hiện trong phản hồi. |
| `ssrf` | một callback về collector do ta kiểm soát, mang theo token của lần thử; hoặc một phản hồi chỉ mạng nội bộ mới tạo ra được. |
| `idor` | hai danh tính, một lần đọc chéo ghi rõ *ai đọc* và *đọc của ai*, **kèm** đối chứng cho thấy danh tính đó không có quyền. |
| `auth-bypass` | token giả mạo được chấp nhận, token cố ý sai bị từ chối, **và** nội dung đặc quyền trong phản hồi. |
| `xss` | một trình duyệt thật đã thực thi payload và báo lại nonce. Phản chiếu **không** phải thực thi. |
| `dos` | bị từ chối ngay từ thiết kế: bằng chứng của lớp này chính là thiệt hại. |

Ba mức chấm: `proven` (đủ điều kiện, được ghi là phát hiện), `supported` (có dấu
hiệu thật nhưng **thiếu một kiểm tra cụ thể được nêu tên** — ghi là *ứng viên*),
`unproven` (không ghi). Mức `supported` là thứ làm hệ thống hữu dụng chứ không chỉ
khắt khe: nó nói chính xác còn thiếu gì, biến một đoạn phỏng đoán thành một việc
hai phút cho phiên sau.

## 4. Bộ điều khiển quyết định bên ngoài mô hình

`argus/ledger/decide.py` có mười quy tắc có thứ tự, fail-closed. Mô hình chọn
**nội dung** của bước kế tiếp; bộ điều khiển chọn **hình dạng** của nó, và nếu mô
hình muốn làm khác thì phải nói ra.

Lý do: khi được đưa một ledger, một mô hình mạnh thường chọn bước hợp lý. Một mô
hình yếu, hoặc một mô hình đã bị trôi ngữ cảnh, lại chạy lại lệnh cũ với payload
mới, hoặc viết một đoạn văn tự tin về điều nó chưa chứng minh. Từ bên ngoài, hai
trường hợp này không phân biệt được — trừ khi bước kế tiếp được tính từ bằng chứng
đã ghi.

Khi ngân sách của một lớp cạn (6 lần thử, hoặc 20 phút hoạt động), hệ thống
**không dừng**. Nó leo một cái thang chiến lược: dùng lại chuỗi đã biết → phân
loại lại bề mặt → nghiên cứu công nghệ của mục tiêu → mở rộng bề mặt → quét song
song bằng nhiều agent → chuyển cho người. Chỉ khi mọi bậc đã dùng hết thì mới ra
lệnh viết báo cáo.

## 5. Bộ điều phối đa mô hình

```
mục tiêu
   ▼
planner    mô hình mạnh nhất, chạy MỘT lần. Đọc ledger, viết danh sách task, dừng.
           Kế hoạch bị kiểm tra trước khi chạy: mục tiêu ngoài phạm vi bị loại,
           lớp lỗ hổng phải có trong ma trận, lớp bị từ chối bị xoá, chu trình
           phụ thuộc bị loại bỏ. `--deterministic` tạo kế hoạch cơ sở không cần
           mô hình nào — đây cũng là điều kiện đối chứng để đo xem planner có
           đáng chi phí hay không.
   ▼
router     loại task → vai trò → ứng viên → (runner, model, mode).
           Hai quy tắc không thương lượng:
             · review phải **khác họ mô hình** với mô hình đã tạo ra phát hiện;
             · việc "bề rộng" giao cho mô hình rẻ nhất đủ năng lực, còn việc
               "phán đoán" (lập kế hoạch, review, viết báo cáo) thì không.
   ▼
scheduler  hàng đợi sẵn sàng + số slot cố định. Một slot trống được lấp **ngay
           lập tức**, không chờ hết đợt. Sau mỗi task hoàn thành, kế hoạch được
           mở rộng từ ledger: một task cho mỗi giả thuyết đang mở.
   ▼
runner     ba cách chạy một task, dùng chung một bản brief:
             · harness của chúng ta (kiểm soát chặt nhất, mọi bước là của ta)
             · claude code — vòng lặp của nó, nhưng tool duy nhất là MCP của ta
             · opencode — tương tự, nhưng dùng tập credential khác
   ▼
verify     một mô hình khác họ đọc **bằng chứng**, không đọc lập luận của mô hình
           đầu. Nếu nó không đồng ý, phát hiện bị hạ xuống mức ứng viên.
```

### Chống trôi ngữ cảnh mà không cần cửa sổ ngữ cảnh lớn hơn

Không có thành phần nào "hiểu toàn bộ công việc" — và đó là điều được thừa nhận
thẳng trong thiết kế. Thay vào đó có ba tạo tác trên đĩa:

- `decisions.json` — tập nhỏ các quyết định mà agent sau không được âm thầm làm
  trái, mỗi quyết định có tác giả, lý do và lịch sử sửa đổi. Nhờ vậy, khi một
  agent muốn phản biện, nó phản biện *với lý do đặt trước mắt*.
- `tasks/<id>/brief.md` và `report.md` — điểm bàn giao. Một task không mô tả được
  thành brief thì chưa phải là task.
- ledger — mọi lần thử, mọi bản ghi bằng chứng, mọi lần bị từ chối.

## 6. Harness riêng cho từng mô hình

Một harness dùng chung cho mọi mô hình phải trả giá hai lần: mô hình mạnh bị kìm
bởi những giới hạn nó không cần, còn mô hình yếu bị trôi vì không có gì nhắc lại
quy tắc đủ thường xuyên. Vì thế vòng lặp là **một đoạn mã duy nhất**, còn khác
biệt nằm trong profile (`argus/runtime/profiles/models.json`):

| Trường | Vì sao khác nhau giữa các mô hình |
|---|---|
| `max_steps` | mô hình giữ được mạch 40 bước khác với mô hình mất mạch ở bước 12 |
| `observation_cap` | đọc được bao nhiêu output của tool trước khi phần đầu rơi khỏi ngữ cảnh |
| `history_chars` | khi nào bắt đầu nén transcript |
| `restate_contract_every` | mô hình tuân thủ chỉ dẫn kém cần nhắc lại quy tắc thường hơn |
| `one_tool_per_step` | một số mô hình gọi song song nhiều tool bị sai thứ tự |
| `tool_dialect` | function calling gốc, hoặc giao thức văn bản cho backend CLI |
| `cost_per_mtok` | là đại lượng router dùng để đánh đổi |

Phần nén ngữ cảnh là điểm đáng chú ý: các kết quả tool cũ được thu lại thành một
dòng (tên tool, tóm tắt, mã bằng chứng), vì bản đầy đủ đã nằm trên đĩa và đọc lại
được bằng `ledger.read_evidence`. **Ledger là bộ nhớ; transcript chỉ là vùng làm
việc ngắn.**

## 7. Những gì hệ thống từ chối làm

- Không thể chạm mục tiêu mà phạm vi không nêu tên. Phạm vi rỗng cho phép **không
  gì cả**; luật từ chối thắng luật cho phép.
- Không có shell. Mọi tool là một danh sách argv.
- Không thể ghi một phát hiện chưa chứng minh được theo yêu cầu của lớp đó.
- Không thể thử lần thứ bảy trên cùng một lớp — phải đổi câu hỏi, không phải đổi
  payload.
- Không kiểm thử từ chối dịch vụ.
- Mức rủi ro `intrusive` không mở được nếu thiếu ghi chú uỷ quyền nêu rõ ai cho
  phép và trong khung thời gian nào.

## 8. Cách chạy

```bash
# mở engagement, khai báo phạm vi và uỷ quyền
./bin/argus open acme-dmz --objective "web foothold" \
    --in-scope 172.31.66.0/24 --out-of-scope 172.31.66.1 \
    --ports 80 443 8080 --tiers passive active intrusive \
    --authorisation "SoW 2026-11-01, 09:00-18:00, ops@acme"
./bin/argus target acme-dmz http://172.31.66.10/

./bin/argus next   acme-dmz          # bộ điều khiển nói bước kế tiếp
./bin/argus agent  acme-dmz --model claude-sonnet-5-5     # một mô hình
./bin/argus plan   acme-dmz          # hoặc: lập kế hoạch rồi chạy cả đội
./bin/argus run    acme-dmz --policy balanced --parallelism 3
./bin/argus verify acme-dmz          # mô hình khác họ đọc lại bằng chứng
./bin/argus report acme-dmz --write
```

Chạy toàn bộ kiểm thử (không cần mạng, không cần API key, có target cố ý lỗi chạy
trên loopback):

```bash
bash test/run_all.sh
```

## 9. Kế hoạch đánh giá

Năm luận điểm, mỗi luận điểm kèm phép đo và **điều kiện đối chứng**. Phần dụng cụ
đo đã có sẵn (`log/cost.jsonl`, `log/commands.jsonl`, `log/bus.jsonl`, thư mục
`evidence/`, các mức chấm chứng minh); phần còn thiếu là chạy nhánh đối chứng.

| Luận điểm | Phép đo | Đối chứng |
|---|---|---|
| Cổng chấp nhận bằng chứng làm giảm phát hiện vô căn cứ | tỷ lệ phát hiện bị người review mù loại bỏ | cùng mô hình, cùng mục tiêu, bỏ yêu cầu chứng minh |
| Bộ điều khiển ngoài mô hình làm giảm lần thử vô ích | số lần thử trên mỗi phát hiện được chứng minh; tỷ lệ lặp payload trong cùng một lớp | cùng mô hình, có tool, không có bộ điều khiển |
| Broker giới hạn năng lực loại bỏ hành vi ngoài phạm vi | số lệnh phát ra ngoài phạm vi đã khai báo | một agent được cấp shell |
| Định tuyến theo thế mạnh và chi phí tốt hơn dùng một mô hình mạnh cho mọi việc | chi phí trên mỗi phát hiện được chứng minh, và số phát hiện bị bỏ sót | dùng mô hình mạnh nhất cho tất cả task |
| Review khác họ bắt được lỗi mà review cùng họ bỏ qua | tỷ lệ hạ cấp phát hiện, khác họ so với cùng họ | lượt review thứ hai cùng họ mô hình |

Thứ tự mục tiêu đánh giá, từ rẻ đến đắt: (1) fixture `test/fixtures/vulnapp.py`
với ground truth chính xác; (2) một dải lab nội bộ nhiều host có script tính điểm;
(3) các ứng dụng cố ý lỗi công khai chạy offline bằng Docker; (4) một engagement
có uỷ quyền thật — môi trường duy nhất kiểm tra được những thứ lab không kiểm tra
được: phạm vi có hệ quả thật, người đọc báo cáo thật, và một mục tiêu không ai
cài sẵn lỗ hổng vào.

## 10. Giới hạn cần nói thẳng

- **Định tuyến là heuristic.** Các `strengths` trong `models.json` là *giả thuyết
  định tuyến*, chưa phải kết quả đo.
- **Yêu cầu chứng minh là sàn, không phải trần.** Nó chặn các dương tính giả phổ
  biến, nhưng không chặn được một kết luận sai được xây dựng cẩn thận — đó là việc
  của review khác họ, và review cũng chỉ là một phép kiểm tra, không phải bảo đảm.
- **Collector là cục bộ.** Các lớp blind chứng minh được trong lab hoặc engagement
  nội bộ; với mục tiêu Internet cần một collector bên ngoài do khách hàng đồng ý.
- **`argus/broker/exec.py` không phải sandbox.** Nó chỉ nhận argv, có timeout và
  giới hạn output; tool mà nó chạy vẫn truy cập được filesystem và mạng.
- **Phần đo của năm luận điểm chưa chạy.** `ROADMAP.md` ghi rõ điều này là khoảng
  cách lớn nhất giữa hiện trạng mã nguồn và mục đích của đề tài.

## 11. Chỉ dùng khi được phép

Chỉ kiểm thử trên hệ thống của chính mình, trong lab, trong CTF, hoặc trong một
engagement có uỷ quyền bằng văn bản mà phạm vi đã được khai báo vào hệ thống. Mức
`intrusive` từ chối mở nếu thiếu ghi chú uỷ quyền — không phải vì một ghi chú làm
cho việc kiểm thử trở nên hợp pháp, mà vì một engagement không đưa ra được ghi chú
đó thì không nên đang chạy.
