# Call depth — chains inside calls


A called function's own returns are controlled by YOUR stack — a
function that returns re-enters the chain at the next qword — the
calls nest, the chain continues.
