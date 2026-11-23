# Service recon: dockerapi

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Docker API 2375/2376: GET /version = docker
version verbatim; /containers/json lists running containers
= full estate inventory; /images/json the images. Plain HTTP
2375 unauthenticated = complete host control surface later -
recon only records the fact.
## Pivot

Signal harvested -> out-*; route named -> that skill.
