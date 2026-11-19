# The newline in the input — the trailing byte


fgets keeps \n; gets strips it; read doesn't add it — the compare's
expected may include or exclude the newline — a classic off-by-one
fail.
