# The alignment math — worked example


The landing leaves rsp at S (whatever it was). Each chain entry
advances rsp by 8. At the call's `call`-push, rsp must satisfy the
callee's expectation (entry ≡ 0 mod 16 before the call instruction,
so inside the function rsp ≡ 8).

## The count

If your entries-to-the-call number is even/odd relative to the
needed alignment: pad with a bare ret.
