# Redirect recon: ssoflow

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SSO-flow capture: a 302 to an identity provider
(oauth/authorize, saml/sso, accounts.google.*, okta) =
the auth topology: which IdP, which client_id, redirect_uri
verbatim. OAuth params visible in the hop = oauth class
surface - record the full Location verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
