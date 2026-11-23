# Stack playbook: aspnet

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ASP.NET fingerprints: X-AspNet-Version, .AspNet.*
cookies, __VIEWSTATE fields, .aspx/.ashx extensions, IIS
Server header.

Recon checks:
- __VIEWSTATE presence -> deserialization class if MAC key
  known/guessable
- /elmah.axd -> error log = session/param mining
- /swagger or /api -> WebAPI surface
- Yellow Screen of Death -> stack + source-path leak
- Telerik/UI handler paths in JS -> rce class candidates
- Windows-integrated auth 401 Negotiate -> auth posture

Predicts: deserialization (ViewState), infodisclosure (elmah,
YSoD), sqli (SqlCommand interpolation), file-upload handlers.
## Pivot

Signal harvested -> out-*; route named -> that skill.
