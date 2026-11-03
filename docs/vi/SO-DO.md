# argus — Sơ đồ hệ thống

Các sơ đồ dưới đây viết bằng Mermaid, GitHub tự dựng hình khi mở file này. Bản
tiếng Anh cùng bộ sơ đồ nằm ở `docs/DIAGRAMS.md`; mô tả kiến trúc đầy đủ ở
`ARCHITECTURE.md`, và bản mô tả tiếng Việt ở `docs/vi/TONG-QUAN.md`.

Mỗi sơ đồ kèm một đoạn giải thích **điều mà sơ đồ không vẽ được**: lý do một mũi
tên tồn tại, hoặc thất bại mà nó ngăn.

---

## 1. Toàn cảnh: bốn mặt phẳng và một đường đi

Đúng theo sơ đồ `người dùng → LLM → MCP → tool`, nhưng có thêm hai cổng mà sơ đồ
gốc không nói tới: cổng **trước khi** chạy lệnh, và cổng **trước khi** ghi nhận
phát hiện.

```mermaid
flowchart TD
    U["Người vận hành<br/>prompt · skill · workflow"]

    subgraph RUNTIME["Mặt phẳng harness — argus/runtime"]
        LLM["LLM<br/>một vòng lặp, một profile cho mỗi model"]
        CTX["Hợp đồng phiên + bản tóm ledger<br/>+ hành động kế tiếp do controller tính"]
    end

    subgraph BROKER["Mặt phẳng tool — argus/broker · 57 tool · 10 server"]
        GATE{"Cổng<br/>phạm vi · mức rủi ro<br/>giả thuyết · ngân sách"}
        EXEC["exec: chỉ argv, không shell<br/>process group riêng · timeout · chặn output"]
    end

    TOOLS["nmap · httpx · ffuf · nuclei · nikto · sqlmap<br/>playwright · script theo từng CVE"]

    subgraph LEDGER["Mặt phẳng điều khiển — argus/ledger"]
        EV["Bằng chứng<br/>đã che bí mật, đã giới hạn độ dài"]
        MATRIX{"Ma trận chứng minh<br/>21 lớp"}
        FIND["Phát hiện<br/>confirmed / candidate"]
        REF[("Log từ chối")]
    end

    REPORT["Báo cáo<br/>đã chứng minh · ứng viên · chưa chứng minh"]

    U --> LLM
    CTX --> LLM
    LLM -->|"MCP tools/call"| GATE
    GATE -->|"từ chối"| REF
    GATE -->|"cho phép"| EXEC
    EXEC --> TOOLS
    TOOLS -->|"quan sát"| EV
    EV --> MATRIX
    MATRIX -->|"proven"| FIND
    MATRIX -->|"supported: nêu tên kiểm tra còn thiếu"| FIND
    MATRIX -->|"unproven: không ghi"| REF
    EV --> CTX
    FIND --> REPORT
    REF --> REPORT

    style GATE fill:#fde68a,stroke:#b45309,color:#000
    style MATRIX fill:#fde68a,stroke:#b45309,color:#000
    style REF fill:#fecaca,stroke:#b91c1c,color:#000
    style FIND fill:#bbf7d0,stroke:#15803d,color:#000
```

**Mũi tên quan trọng nhất là `EV --> CTX`.** Quyết định kế tiếp của mô hình được
tính từ ledger trên đĩa, không phải từ bản tự tóm tắt của chính nó. Đó là lý do
một phiên có thể bị ngắt giữa dòng rồi tiếp tục bằng **một mô hình khác**, và
engagement vẫn ở đúng chỗ nó đang đứng.

---

## 2. Một lệnh đi qua cổng: từng bước

```mermaid
sequenceDiagram
    autonumber
    participant M as LLM
    participant B as broker Server.call
    participant H as hooks, đường ghi duy nhất
    participant T as tool thật, ví dụ sqlmap
    participant L as ledger

    M->>B: tools/call proof.exec_marker
    B->>B: kiểm lược đồ tham số
    B->>H: pre_probe — phạm vi, tier, giả thuyết, ngân sách

    alt Bị từ chối
        H-->>L: ghi vào log từ chối
        H-->>B: out-of-scope / tier-not-enabled /<br/>class-mismatch / budget-spent
        B-->>M: ok=false + lý do, KHÔNG tiêu probe
        Note over M,B: Từ chối là một quyết định.<br/>Gọi lại y nguyên không bao giờ là câu trả lời.
    else Được phép
        H-->>B: cho phép + ngân sách còn lại
        B->>T: argv (không shell), timeout
        T-->>B: stdout/stderr đã giới hạn
        B->>H: post_probe(bằng chứng)
        H->>L: che bí mật, ghi nguyên tử, tính vào ngân sách
        H-->>B: probe_id + evidence_id
        B-->>M: summary trước, rồi dữ liệu, rồi "next"
    end
```

Hai điều sơ đồ không nói ra:

- **`summary` đứng trước.** Mô hình đọc những dòng đầu của một kết quả tool đáng
  tin cậy hơn nhiều so với những dòng cuối.
- **Từ chối không tiêu probe.** Một lần bị từ chối không phải là một quan sát;
  nếu nó vẫn trừ ngân sách thì mô hình bị trừng phạt vì đã thử đúng cách.

---

## 3. Một mức chấm được quyết định thế nào

Đây là trung tâm của hệ thống. Ba cơ chế, và **cả ba đều sinh ra từ một lỗi đã
đo được**, không phải từ giả định.

```mermaid
flowchart TD
    E["Các bản ghi bằng chứng"] --> V{"Kiểm tra VETO<br/>có đạt?"}
    V -->|"không — ví dụ payload phá hoại"| U1["unproven<br/>bằng chứng bị loại bỏ"]
    V -->|"đạt"| F{"Kiểm tra FLOOR<br/>có đạt?"}
    F -->|"không — ví dụ chỉ có control"| U2["unproven<br/>không thuộc về lớp này"]
    F -->|"đạt"| R{"Mọi kiểm tra<br/>BẮT BUỘC đạt?"}
    R -->|"đạt hết"| P["proven<br/>được báo cáo là phát hiện"]
    R -->|"đạt một phần"| S["supported<br/>ghi là ỨNG VIÊN,<br/>nêu tên kiểm tra còn thiếu"]
    R -->|"không đạt cái nào"| U3["unproven<br/>không ghi"]

    style P fill:#bbf7d0,stroke:#15803d,color:#000
    style S fill:#fde68a,stroke:#b45309,color:#000
    style U1 fill:#fecaca,stroke:#b91c1c,color:#000
    style U2 fill:#fecaca,stroke:#b91c1c,color:#000
    style U3 fill:#fecaca,stroke:#b91c1c,color:#000
```

| Cơ chế | Lỗi thật đã tái hiện được |
|---|---|
| **veto** | `"proof command stayed benign"` đạt *tầm thường* khi không có lệnh nào chạy. Là kiểm tra bắt buộc, nó khiến **bất kỳ** bản ghi nào dưới một giả thuyết `rce` cũng ghi được thành ứng viên critical. Là veto, nó làm đúng việc nó được viết ra để làm: một payload phá hoại loại bỏ bằng chứng. |
| **floor** | Một tập bản ghi **chỉ có control** được chấm `supported`: "mọi đích redirect đều nằm trong origin" trở thành "tiến triển một phần tới một open redirect". |
| **required** | `rce` cần: lệnh **được khai báo**, nonce trong **output**, và dòng identity. Trước khi sửa, một tham số chỉ *phản chiếu* token của probe đã thoả mãn "nonce đã được echo", và lớp được chấm `proven` với **không có gì được thực thi** — hai reviewer độc lập tái hiện được end-to-end. |

`supported` là mức làm hệ thống hữu dụng chứ không chỉ khắt khe: nó ghi lại điều
có thật, nêu tên **đúng một** kiểm tra còn thiếu, và biến một đoạn phỏng đoán
thành một việc hai phút cho phiên sau.

---

## 4. Vòng đời một giả thuyết

```mermaid
stateDiagram-v2
    [*] --> open: ledger.open_hypothesis — một lớp, một điểm vào, một phản chứng

    open --> open: probe, tối đa 6 lần cho một lớp
    open --> falsified: ledger.falsify — BẮT BUỘC có evidence_id
    open --> parked: ledger.park — hết ngân sách, hoặc đổi hướng
    open --> confirmed: bằng chứng đạt yêu cầu chứng minh

    parked --> open: ledger.revive — có bằng chứng mới liên quan
    confirmed --> candidate: ledger.cross_verify — mô hình khác họ KHÔNG đồng ý

    falsified --> [*]
    candidate --> [*]
    confirmed --> [*]

    note right of parked
        Park, không delete.
        Một hướng trông sai thường là
        một hướng chưa làm xong.
    end note

    note right of falsified
        Đóng bằng một QUAN SÁT.
        Lịch trình gấp, ý tưởng hay hơn,
        hay chỉ đạo của người vận hành
        là lý do để park, không phải để đóng.
    end note
```

Khi ngân sách của một lớp cạn, hệ thống **không dừng**. Nó leo một cái thang
chiến lược — dùng lại chuỗi đã biết → phân loại lại bề mặt → nghiên cứu công
nghệ của mục tiêu → mở rộng bề mặt → quét song song nhiều agent → chuyển cho
người — và chỉ ra lệnh viết báo cáo khi mọi bậc đã dùng hết.

---

## 5. Bộ điều phối: nhiều mô hình làm một người kiểm thử

```mermaid
flowchart LR
    OBJ["Mục tiêu"] --> PLAN

    subgraph PLAN["planner — chạy MỘT lần"]
        P1["Mô hình mạnh nhất<br/>đọc ledger, viết task, DỪNG"]
        P2{"Kiểm tra kế hoạch"}
        P1 --> P2
        P2 -->|"ngoài phạm vi"| X1["loại task"]
        P2 -->|"lớp bị từ chối"| X2["loại task"]
        P2 -->|"chu trình phụ thuộc"| X3["loại kế hoạch"]
    end

    P2 -->|"hợp lệ"| ART[("plan.json + tasks/<br/>tạo tác trên đĩa")]
    ART --> ROUTE

    subgraph ROUTE["router"]
        R1["loại task → vai trò → ứng viên"]
        R2["Hai quy tắc không thương lượng"]
        R1 --> R2
    end

    ROUTE --> SCHED["scheduler<br/>hàng đợi sẵn sàng + số slot cố định<br/>lấp slot trống NGAY"]
    SCHED --> H1["harness của ta<br/>kiểm soát chặt nhất"]
    SCHED --> H2["claude code<br/>vòng lặp của nó"]
    SCHED --> H3["opencode<br/>tập credential khác"]

    H1 --> BUS
    H2 --> BUS
    H3 --> BUS
    BUS[("Ngữ cảnh chia sẻ trên đĩa<br/>decisions.json · brief · report · ledger")]
    BUS --> VER["verify<br/>mô hình KHÁC HỌ đọc bằng chứng,<br/>không đọc lập luận"]
    VER --> OUT["Báo cáo"]

    style R2 fill:#fde68a,stroke:#b45309,color:#000
    style BUS fill:#dbeafe,stroke:#1d4ed8,color:#000
```

**Hai quy tắc không thương lượng trong router:**

1. **Review phải khác họ mô hình.** Hai mô hình đồng ý vì cùng một tiên kiến thì
   không phải một phép kiểm tra.
2. **Việc bề rộng giao cho mô hình rẻ nhất đủ năng lực; việc phán đoán thì
   không.** Một kế hoạch do mô hình rẻ nhất lập là một khoản tiết kiệm giả: nó
   là tạo tác duy nhất định hình toàn bộ phần còn lại của engagement.

**Và điều không có ở đây:** không thành phần nào "hiểu toàn bộ công việc". Thay
vào đó là kế hoạch trên đĩa, kho quyết định mà agent nào cũng đọc được, và ledger
mà mọi lần gọi tool đều ghi vào. Nhờ vậy một agent vào ở task thứ chín biết tám
task trước đã xác lập điều gì mà không cần từng có mặt trong cuộc hội thoại.

---

## 6. Định tuyến thực tế trên máy này

Đo bằng `argus fleet` với chính sách mặc định `balanced`:

```mermaid
flowchart LR
    subgraph JUDGE["Việc phán đoán — giữ nguyên năng lực"]
        PL["plan"] --> OPUS["claude-opus-5-5<br/>qua Claude Code"]
        RV["review"] --> DS["deepseek-v4-pro<br/>qua opencode-go<br/>KHÁC HỌ với Claude"]
        RP["report"] --> SON["claude-sonnet-5-5"]
    end

    subgraph EXEC["Việc thực thi"]
        PB["probe · exploit · prove"] --> SON2["claude-sonnet-5-5<br/>harness của ta"]
    end

    subgraph BREADTH["Việc bề rộng — mô hình rẻ nhất đủ năng lực"]
        RC["recon · triage"] --> FLASH["deepseek-flash"]
        RS["research<br/>đọc bundle lớn, advisory"] --> GEM["gemini-3.5-flash<br/>ngữ cảnh 1M"]
    end

    style OPUS fill:#fde68a,stroke:#b45309,color:#000
    style DS fill:#ddd6fe,stroke:#6d28d9,color:#000
    style FLASH fill:#bbf7d0,stroke:#15803d,color:#000
    style GEM fill:#bbf7d0,stroke:#15803d,color:#000
```

Các trường `strengths` trong `argus/runtime/profiles/models.json` là **giả thuyết
định tuyến, chưa phải kết quả đo**. Sửa một giả thuyết là sửa một dòng JSON, và
`argus metrics` là cách một phép đo phản biện lại nó. Nói thẳng điều này quan
trọng hơn là có một bảng trông thuyết phục.

---

## 7. Sáu kiểu từ chối

```mermaid
flowchart TD
    C["Một lần gọi tool"] --> S{"Mục tiêu có<br/>trong phạm vi?"}
    S -->|"không"| R1["out-of-scope<br/>phạm vi rỗng cho phép KHÔNG GÌ CẢ,<br/>luật từ chối thắng luật cho phép"]
    S -->|"có"| T{"Mức rủi ro của tool<br/>đã được bật?"}
    T -->|"không"| R2["tier-not-enabled<br/>intrusive không mở được<br/>nếu thiếu ghi chú uỷ quyền"]
    T -->|"có"| HY{"Có nêu tên<br/>giả thuyết?"}
    HY -->|"không / sai lớp"| R3["class-mismatch<br/>một probe không nêu giả thuyết<br/>không thể phản chứng điều gì"]
    HY -->|"đúng"| B{"Ngân sách<br/>của lớp còn?"}
    B -->|"hết"| R4["budget-spent<br/>đổi CÂU HỎI,<br/>không phải đổi payload"]
    B -->|"còn"| RUN["lệnh chạy"]
    RUN --> P{"Ghi phát hiện?"}
    P -->|"bằng chứng không đạt"| R5["unproven<br/>không ghi"]
    P -->|"lớp không chứng minh được ở đây"| R6["refused-class<br/>ví dụ DoS: bằng chứng chính là thiệt hại"]
    P -->|"đạt"| OK["ghi nhận"]

    style R1 fill:#fecaca,stroke:#b91c1c,color:#000
    style R2 fill:#fecaca,stroke:#b91c1c,color:#000
    style R3 fill:#fecaca,stroke:#b91c1c,color:#000
    style R4 fill:#fecaca,stroke:#b91c1c,color:#000
    style R5 fill:#fecaca,stroke:#b91c1c,color:#000
    style R6 fill:#fecaca,stroke:#b91c1c,color:#000
    style OK fill:#bbf7d0,stroke:#15803d,color:#000
```

Cả sáu đều được ghi vào `log/refusals.jsonl`, nên `argus metrics` trả lời được
câu "agent đã bao nhiêu lần thử hành động ngoài những gì nó được phép" — đó chính
là con số mà luận điểm số 3 trong `ARCHITECTURE.md` nói tới.

---

## 8. Lượt chạy model thật đã đo được

`deepseek-v4-pro` qua `opencode-go`, do harness điều khiển, chạy vào target cố ý
có lỗi trên loopback. Nhiệm vụ: *"prove or kill command injection in the host
parameter of /ping"*.

```mermaid
sequenceDiagram
    autonumber
    participant M as deepseek-v4-pro
    participant L as ledger
    participant K as ma trận chứng minh
    participant T as target (fixture)

    M->>L: ledger.open_hypothesis (rce)
    L-->>M: hy-38453b6a67 mở
    M->>K: proof.requirement (rce)
    K-->>M: cần lệnh khai báo + nonce trong output + dòng identity
    Note over M,K: Nó đọc yêu cầu TRƯỚC khi probe.<br/>Đúng kỷ luật mà hợp đồng phiên đòi.
    M->>T: http.probe (baseline)
    T-->>M: 200, 29 byte
    M->>T: proof.exec_marker (id; echo nonce)
    T-->>M: nonce trả về, uid=1000(kali)
    M->>K: chấm điểm
    K-->>M: proven
    M->>L: ledger.record_finding
    L-->>M: fi-18417e082e — confirmed
    M->>L: ledger.read_evidence
    L-->>M: 2 bản ghi — nó tự đọc lại chính mình
```

| Số đo | Giá trị |
|---|---|
| probe đã tiêu | 2 |
| lần bị từ chối | 0 |
| phát hiện | 1, chấm `proven` |
| token | 54.083 |
| chi phí | 0,017 USD |
| thời gian | 777 giây — **129 giây/bước** |

129 giây/bước là con số đáng giữ: đó là giá của một backend CLI **không trạng
thái**, mỗi bước gửi lại toàn bộ prompt và trả phí khởi động tiến trình. Đường
provider dùng API key sẽ không như vậy — và đường đó **vẫn chưa có lượt chạy
thật nào**.

---

## 9. Bản đồ thành phần trong repo

```mermaid
flowchart TD
    subgraph PKG["argus/ — 6.400 dòng"]
        LED["ledger/<br/>scope · state · proof · hooks<br/>decide · report · lock · identities"]
        BRK["broker/<br/>mcp · exec · httpkit · collector<br/>servers/ ×10"]
        RUN["runtime/<br/>loop · context · prompts<br/>providers/ ×8 · profiles/"]
        ORC["orchestrator/<br/>planner · workflows · router<br/>scheduler · runner · bus · verify · metrics"]
        KNW["knowledge/<br/>playbook · chains"]
        CLI["cli.py"]
    end

    subgraph DATA["Dữ liệu — sửa là sửa JSON, không sửa code"]
        PB["knowledge/playbook.json<br/>21 ladder"]
        MD["profiles/models.json<br/>12 profile"]
        WF["workflows/ ×4"]
        EX["scripts/exploits/<br/>registry + template"]
        SK["skills/ ×18"]
    end

    subgraph TEST["test/ — gate 5 lớp, 1.226 checks"]
        T1["unit 159"]
        T2["consistency 995"]
        T3["harness 12"]
        T4["e2e 60"]
        T5["baselines"]
        FX["fixtures/vulnapp.py<br/>target cố ý lỗi, chỉ loopback"]
    end

    CLI --> ORC --> RUN --> BRK --> LED
    KNW --> LED
    PB --> KNW
    MD --> RUN
    WF --> ORC
    EX --> BRK
    SK --> KNW
    FX --> T4
    LED --> T1
    BRK --> T2

    style LED fill:#fde68a,stroke:#b45309,color:#000
    style DATA fill:#dbeafe,stroke:#1d4ed8,color:#000
    style TEST fill:#dcfce7,stroke:#15803d,color:#000
```

Bốn điểm mở rộng, và **ba trong bốn là file dữ liệu**: thêm một lớp lỗ hổng, một
ladder, một script CVE, một profile model. Chỉ việc thêm một tool MCP mới cần
viết code — và đó là một hàm có decorator. `skills/extending-argus/SKILL.md` ghi
hợp đồng cho cả bốn.

---

## 10. Điều các sơ đồ này không vẽ

Phần trung thực, và nó thuộc về bài trình bày chứ không phải phần phụ lục:

- **3 trong 5 luận điểm nghiên cứu cần model thật và chưa chạy.** Kế hoạch tất
  định so với kế hoạch do model lập; một model mạnh dùng cho mọi việc so với đội
  được định tuyến; review cùng họ so với khác họ. `ARCHITECTURE.md` mục 6 ghi
  từng luận điểm cùng điều kiện đối chứng nó cần.
- **Phần đo offline đã có**, nhưng chủ thể được đo là một **driver viết sẵn**, không
  phải một mô hình. Nó đo điều mà *cổng* làm với một chuỗi hành động cho trước.
  Đường ghi không-gate nhận 4 finding mà bằng chứng không đạt bất kỳ phần nào của
  yêu cầu lớp; đường có gate nhận 0 — và `test/baselines.py` tự nói rằng đó là
  tính chất của cổng, không phải phát hiện về mô hình.
- **Chưa có lượt nào dùng lại một chain card trên target thứ hai**, nên "lần chạy
  thứ hai rẻ hơn lần đầu" vẫn là khẳng định thiết kế.
- **7 lớp còn thiếu depth skill**, có tên trong `skills/INDEX.md`.
- **Fixture là fixture, không phải benchmark**: ground truth chính xác, và không
  nói được gì về khả năng tổng quát hoá.
