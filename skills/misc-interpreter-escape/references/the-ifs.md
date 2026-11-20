# $IFS — the bash separator

`${IFS}` is the field separator — `cat${IFS}flag` runs `cat flag`
without a space or the letters together — a word never typed is
never blocked.

## The separator

${IFS} splits without a space — a word-free command.
