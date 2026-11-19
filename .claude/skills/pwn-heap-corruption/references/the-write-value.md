# What value the techniques write


| Technique | The written value |
|---|---|
| unsorted-bin attack | a main_arena address (fixed, libc) |
| largebin bk_nextsize | a heap chunk address |
| tcache poison | your chosen pointer (post-leak) |
| house-of-force | the top — then arbitrary via alloc |
| overlap → ptr forge | your controlled bytes |
| FSOP vtable | a vtable-region address |

The write's VALUE differs per technique — pick the technique whose
written value your target needs.
