# NativeAOT / ReadyToRun — the boundary

NativeAOT compiles .NET to native ahead-of-time — NO IL inside;
it's native code (rev-native-check). ReadyToRun embeds both IL +
native — the IL is still readable.

## The discriminate

A managed-looking binary with no real metadata → AOT → native
class.
