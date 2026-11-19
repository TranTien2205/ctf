# __libc_start_main — the main caller


__libc_start_main calls main — its return slot is where control goes
after main returns; a redirect there fires at program end.

## The slot

On the stack early — usually out of a stack overflow's reach, but a
stack pivot could aim there.
