#!/bin/bash
# Recorded evidence run: argus against a lab target on a SEPARATE machine.
# Narration in Vietnamese for the supervisor; all tool output is verbatim.
set -u
CM=/tmp/.acm223
T=lab@192.168.223.221
B=http://192.168.223.221:8777
OUT="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
say()  { printf '\n\033[1;36m== %s\033[0m\n' "$*"; sleep 1.2; }
note() { printf '\033[0;33m   %s\033[0m\n' "$*"; sleep 0.6; }
run()  { printf '\033[1;32m$ %s\033[0m\n' "$*"; sleep 0.7; eval "$*"; sleep 1.0; }

say "1/7  HAI MAY RIENG BIET - may tan cong va may muc tieu"
note "May tan cong (Kali) - argus chay o day:"
run "hostname && ip -4 addr show eth0 | grep -oP 'inet \K[0-9.]+' | head -1"
note "May muc tieu (Ubuntu) - mot may ao khac, truy cap qua SSH:"
run "ssh -o ControlPath=$CM $T 'hostname; . /etc/os-release; echo \$PRETTY_NAME; hostname -I; python3 -V'"

say "2/7  UNG DUNG MUC TIEU DANG CHAY TREN MAY UBUNTU"
note "Cai tai ~/argus-lab/ tren may muc tieu, bind vao IP LAN cua chinh no:"
run "ssh -o ControlPath=$CM $T 'cat ~/argus-lab/lab.log; echo; ss -ltn | grep 8777'"

say "3/7  PHAM VI VA UY QUYEN"
run "head -12 $HERE/AUTHORIZATION.txt"

say "4/7  ARGUS TU DONG KHAI THAC - toan bo pipeline chay that"
note "Khong ai go payload: probe tu chon payload theo tung lop lo hong,"
note "cong chung minh tu cham bang chung, bao cao tu sinh."
run "cd /home/kali/ctf && timeout 300 python3 -m argus demo --target $B --session-dir $OUT"

S=$(ls -d "$OUT"/*/ 2>/dev/null | head -1)
say "5/7  HAI TIEU CHI BAT BUOC - bang chung lay tu chinh may muc tieu"
note "RCE phai la output cua lenh id; SQLi phai la du lieu that trong bang:"
run "python3 $HERE/show_proof.py ${S}findings.json"
note "uid=1000(lab) la danh tinh cua MAY MUC TIEU, khong phai cua Kali."

say "6/7  BANG CHUNG CHONG SUA - transcript bam chuoi, kiem tra lai duoc"
run "cd /home/kali/ctf && python3 -m argus verify ${S%/}"
note "Sua mot byte trong transcript hoac nang grade trong findings.json -> verify bao loi."

say "7/7  DIEU CHUA LAM DUOC - noi ro de khong gay hieu nham"
note "Quyet dinh trong lan chay nay do SCRIPT dieu khien (model: scripted-demo),"
note "chua phai do LLM tu quyet. Ly do da do duoc, khong phong doan:"
run "cd /home/kali/ctf && timeout 100 python3 -m argus run $B --allow-private --goal probe --max-turns 1 --session-dir $OUT/llm-attempt 2>&1 | grep -o '\"message\":\"[^\"]*\"' | head -1"
note "Moi request HTTP, moi byte bang chung o tren deu la that."
note "Chi tang quyet dinh la script - can nap han muc tai khoan de mo."
printf '\n\033[1;36m== HET ==\033[0m\n'
