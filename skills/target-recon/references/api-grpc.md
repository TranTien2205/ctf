# API recon: grpc

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

gRPC recon on HTTP/2: content-type application/grpc
confirms it. grpcurl -plaintext <host:port> list - reflection
returns the service list = complete surface. No reflection:
method probing needs .proto knowledge - check for a grpc-web
proxy (envoy) which exposes methods through the JS bundle.
grpc-status trailers in responses are the error oracle.
## Pivot

Signal harvested -> out-*; route named -> that skill.
