# Thiết kế thực nghiệm (GĐ2)

## 1. Bộ dữ liệu

**Không dùng `challenges/` làm benchmark.** Đó là handout thật, không nhãn
thống nhất, không dựng lại được bằng một lệnh. Dùng nó làm **nguồn khai thác
tri thức** (73 chain card, 60 writeup, 5 kill map), còn benchmark phải tái lập.

| Lớp | Nguồn | Vì sao |
|---|---|---|
| D1 — lab có nhãn | OWASP Juice Shop, DVWA, WebGoat (Docker) | nhãn công khai, dựng một lệnh |
| D2 — CTF web đã giải tại chỗ | 70 chain card web + handout tương ứng | có ground truth *và* kill map |
| D3 — giữ kín | 10–15 mục tiêu không dùng khi phát triển | chống overfit vào taxonomy |

Mỗi mục tiêu cần một bản ghi nhãn:
`{target_id, dựng_bằng, lớp_lỗ_hổng, vị_trí(file:line hoặc endpoint), bằng_chứng_tối_thiểu, nhãn_âm[]}`

## 2. Baseline

| ID | Hệ thống | Trả lời câu hỏi |
|---|---|---|
| B0 | Scanner tự động (ZAP / Nuclei / sqlmap) | agent có hơn công cụ sẵn có không |
| B1 | LLM agent ReAct trần, cùng bộ công cụ, **không** control plane, **không** gate | cô lập đóng góp kiến trúc |
| B2 | Hệ đầy đủ (control plane + gate + retrieval) | hiệu quả tổng |
| B2−C | B2 bỏ control plane | ablation H1 |
| B2−V | B2 bỏ kiểm chuỗi con của bằng chứng | ablation H2 |
| B2−R | B2 bỏ retrieval | ablation H3 |

## 3. Chỉ số

**Chất lượng phát hiện** — đối chiếu từng verdict với nhãn:
`TP, FP, FN`, precision, recall, F1.
*FP phải tách hai loại*: (a) sai lớp lỗ hổng, (b) **bằng chứng bịa** — loại (b)
là chỉ số riêng của đề tài và là nơi H2 sống chết.

**Hiệu quả** — `hành_động_lãng_phí` = số probe sau probe cuối cùng còn đóng góp
thông tin; `probe_đến_phát_hiện`; `thời_gian_tường`; `token_vào/ra`.

**Tái lập** — chạy `k = 5` lần mỗi cặp (hệ, mục tiêu), báo cáo trung vị và
khoảng, **không** báo cáo lần chạy tốt nhất.

## 4. Giao thức

1. Khoá phiên bản mô hình và nhiệt độ; ghi vào mỗi bản ghi kết quả.
2. Mỗi lần chạy sinh một trace: mọi probe, mọi response byte, mọi verdict.
3. Chấm điểm **tự động** bằng nhãn, không để LLM tự chấm.
4. D3 chỉ chạy **một lần duy nhất**, ở cuối, không tinh chỉnh sau đó.

## 5. Những gì còn thiếu trong mã hiện tại

- [ ] Bộ đếm token/thời gian mỗi mục tiêu — **chưa có**
- [ ] Định dạng nhãn + trình chấm tự động — **chưa có**
- [ ] Runner dựng Docker cho D1 — **chưa có**
- [ ] Công tắc tắt từng thành phần cho ablation (B2−C/−V/−R) — **chưa có**
- [x] Ghi trace probe/verdict — đã có qua `state.py` + `hooks.py`
- [x] Hạ tầng đánh giá offline — đã có 5 evaluator
