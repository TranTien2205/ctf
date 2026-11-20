# The terminator inside data

If the terminator string can appear inside question data (`> ` in a
math prompt), anchor the until() scan to line-start or use the
captured prompt prefix — a mid-line terminator splits the question.
