# objdump — the alternate disasm


objdump is present — a quick disasm without r2's session:

    objdump -d -M intel ./chal | grep -B5 -A15 'strcmp'
