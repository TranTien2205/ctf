# Object-slot writes — vtables and handlers


C++ objects carry vtable pointers on the stack/heap — %n into a vtable
slot redirects virtual calls; handler tables similarly.

## Steps

1. Find a vtable/handler pointer reachable by the write.
2. Write a fake-vtable address or a direct function.
3. The next virtual/indirect call redirects.

## Falsifier

No vtable/handler reachable or called after the write.
