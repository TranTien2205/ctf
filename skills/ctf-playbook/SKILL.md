---
name: ctf-playbook
description: >
  Top-level jeopardy router. Use at the START of any CTF challenge to classify
  it and route to the category skill, and to manage time across a timed contest.
  Reference card — routes, does not solve.
tags: [ctf, general, triage, strategy, playbook]
environment: [ctf, lab]
---

# CTF Jeopardy — Playbook (router tổng)

## Step 0 — mỗi challenge
1. Phân loại → route sang skill category (bảng dưới). Playbook này KHÔNG tự giải.
2. Ghi state: flag ở đâu, dữ kiện, giả thuyết, next action (dùng `state()` nếu có MCP server).
3. Ước lượng độ khó → time-box.
4. **Writeup-FIRST khi blackbox thuộc platform đã biết** (HTB/HTB-Uni/TFC/VulnHub…):
   sau fingerprint (title, meta author, banner, route shape), chạy
   `python3 tools/writeup_search.py "<fingerprint>" --fresh` và websearch trước khi
   fuzz mù. Bài HTB ~luôn có writeup; bằng chứng 2/2 bài thắng 2026-09 đều đến từ
   writeup (nginxatsu, TornadoService), còn fuzz mù trước đó chỉ đốt thời gian.
   Ghi rõ vào solved card: tự giải hay tái hiện writeup.

## Signal → skill

Hai tầng. **Mở router mỏng trước** — nó thường đã đủ. Chỉ mở depth khi router không đưa
được kỹ thuật khớp: depth dài 150–500 dòng, tốn nhiều ngàn token và dễ đóng hộp tư duy
trên bài mới.

| Thấy | 1. Router mỏng | 2. Depth (chỉ khi thiếu) |
|---|---|---|
| HTTP/source web, endpoint, login | `web-triage/` | `ctf-web`, `web-sqli`/`ssti`/`ssrf`/`xss`/`idor`/`file-upload`/`deserialization`/`auth-session` |
| ELF/binary + input, checksec | `pwn-binary-triage/` | `ctf-pwn`, `pwn-rop` |
| Binary cần đảo ngược logic / packed | `rev-triage/` | `ctf-reverse` |
| Dữ liệu mã hoá, RSA/AES/hash/cipher | `crypto-triage/` | `ctf-crypto` |
| PCAP / memory / disk / stego / log | `forensics-triage/` | `ctf-forensics` |
| AI chatbot/model · IoT firmware/protocol | `ai-iot-triage/` | `ctf-ai-ml` |
| OSINT / người / ảnh / tên miền | `osint-triage/` | `ctf-osint` |
| Jail, encoding, SDR, game VM, lập trình | — | `ctf-misc` |
| Script/PE bị obfuscate, C2 traffic | — | `ctf-malware` |

Không chắc → **đừng đoán, đừng mở nhiều cái**: `python3 solver/recognize.py "<quan sát>"`,
mục SKILL chỉ đúng một cái. Mục PATTERN có thể cho luôn solver deterministic ra đáp án thật.

## Time management (Sơ khảo 8h tính giờ, đội 4 người)
- 30% đầu: quét hết bài DỄ, ăn điểm nhanh trước.
- 50% giữa: bài trung bình + bài khó đã có ý tưởng.
- 20% cuối: verify flag, KHÔNG mở hướng mới.
- Time-box: easy 15-30' · medium 30-60' · hard 60-120'.
- **Stuck >15': re-read đề → có hint bỏ sót? → đổi HẲN hướng → skip, quay lại sau.** Đừng cắm 1 bài.
- Chia category theo thế mạnh; không chụm cùng 1 bài trừ khi bế tắc.

## Flag format
`CTF{} FLAG{} flag{} HTB{} <brand>{}` — xác nhận format của đề trước khi nộp. `references/flag-formats.md`.

## One-liner hay dùng
- base64 `echo X|base64 -d` · hex `echo X|xxd -r -p` · rot13 `tr 'A-Za-z' 'N-ZA-Mn-za-m'`
- url-decode `python3 -c "import urllib.parse;print(urllib.parse.unquote('X'))"`
- cyclic `python3 -c "from pwn import *;print(cyclic(200))"` · offset `cyclic_find(b'aaXX')`
- Thêm: `references/common-tools.md`.

## Escalation ladder (khi bế tắc — ĐỌC KỸ)
Gom probe theo **lớp cơ chế**, không theo biến thể. Ngân sách/lớp: **≤5 probe hoặc ≤15'**.
Hết ngân sách mà không có tín hiệu mới → **leo thang, không thử biến thể tiếp**:
1. Re-read đề+artifact (bỏ sót hint/field? regex unanchored? `contains` vs `eq`?).
2. Đổi TẦNG cơ chế: parser → state machine → auth/session → response-side → framing → logic.
3. Reverse HÀM quyết định (đừng để lại đúng đoạn khả nghi nhất "chưa đọc").
4. Kéo tri thức ngoài: bài live hay cũ? dùng writeup được không? → `tools/writeup_search.py`.
5. Skip, quay lại sau. Chi tiết đầy đủ: `../LOOP_DISCIPLINE.md`.

## Discipline
- Route đúng category rồi để skill đó dẫn — không tự giải ở đây.
- Một giả thuyết → **test quyết định** (giết/xác nhận cả lớp) → "tín hiệu mới?" → không thì leo thang.
- Dấu hiệu quẫy (STOP): "wait wait", >2 giả thuyết mới/lượt không test, lặp ý đã bác bỏ.
- Ghi ledger qua `tools/state.py` (`--probe/--result/--close`) — ledger DẪN quyết định.
- LUẬT GIẢI: nếu BTC cấm AI, hệ thống chỉ để LUYỆN trước, KHÔNG dùng trong lúc thi.
