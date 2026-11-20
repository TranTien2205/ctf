# Buffered output — flush logs

A solver that prints the flag then exits may lose the line to
buffered stdout — flush (or write unbuffered) before exit so the
transcript actually records it.
