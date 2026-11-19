# Edge cases — the odd shapes

| Shape | Handling |
|---|---|
| buffer at frame edge (adjacent to canary) | the smallest overwrite trips it — leak first |
| a struct field, not a bare buffer | overflow crosses field boundaries |
| recursion into the vulnerable func | each call's frame is smashable |
| the input is parsed before the copy | the parsed form is what smashes |
| two reads into adjacent buffers | the overflow crosses into the second |
| a signed char index | negative index writes below the buffer |
| vfork/clone shares the stack | unusual frame sharing |
| signal-handler frame on the stack | an alt smashing surface |
