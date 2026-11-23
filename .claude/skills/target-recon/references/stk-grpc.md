# Stack playbook: grpc

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

gRPC service: HTTP/2 with application/grpc content
type, binary frames, trailers-only responses, grpc-status
trailer.

Recon checks:
- grpc-web proxy presence (envoy text frames) -> browser bridge
- Reflection service -> service/method list without .proto
- h2c cleartext upgrade -> downgrade surface
- Method not found vs unimplemented codes -> method probing
- grpcurl -plaintext host:port list -> reflection check

Predicts: routes to nonweb/protocol depth; authz on service
methods, injection through message fields, reflection abuse.
## Pivot

Signal harvested -> out-*; route named -> that skill.
