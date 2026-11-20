# The delimiter — space, tab, comma, quoted

Combined format has quoted strings containing spaces — a naive
awk '{print $N}' splits inside the quotes. Verify the delimiter;
IIS is space, JSON needs parsing, syslog is fixed-width-ish.
