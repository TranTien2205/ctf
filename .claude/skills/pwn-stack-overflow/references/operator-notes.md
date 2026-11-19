# Operator notes — the lived experience

- The protections report IS the chain — build nothing before reading it.
- The offset is measured, not remembered — every build shifts it.
- A 'works locally, crashes remotely' is always alignment first.
- The canary is the wall; the leak is the door — look for ANY read that
  shows a stack word.
- Banned bytes in addresses kill silently — check the payload's bytes
  against the read's filter before sending.
- A fork-server's shared canary is the cheat code — byte-brute it.
- Two-stage exploits need a re-trigger; a one-shot needs composition.
- The honest dead-route record saves the next attempt the same walk.
