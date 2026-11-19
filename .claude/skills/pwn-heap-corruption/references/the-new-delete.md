# new/delete — the C++ operators


operator new → malloc; operator delete → free — same heap, same
checks, plus the constructor/destructor call windows.

## The extras

- new runs the ctor AFTER alloc — a ctor writing fields is post-alloc.
- delete runs the dtor BEFORE free — a call window.
- Sized delete (2.34+) may check the size argument.

## Falsifier

None beyond the base heap ones — operator paths share the machinery.
