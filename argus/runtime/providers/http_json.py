"""One JSON POST, with retries on the failures that are worth retrying."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

RETRYABLE = {408, 409, 429, 500, 502, 503, 504, 529}


def post(url: str, headers: dict, payload: dict, timeout: int = 180,
         retries: int = 2) -> tuple[int, dict, str]:
    body = json.dumps(payload).encode()
    last = (0, {}, "no attempt made")
    for attempt in range(max(1, retries + 1)):
        request = urllib.request.Request(url, data=body, method="POST",
                                         headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8", "replace")
                return response.status, json.loads(raw) if raw.strip() else {}, ""
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8", "replace") if hasattr(error, "read") else ""
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"raw": raw[:2000]}
            last = (error.code, parsed, f"HTTP {error.code}: {raw[:500]}")
            if error.code not in RETRYABLE:
                return last
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last = (0, {}, f"transport: {error}")
        except json.JSONDecodeError as error:
            return 0, {}, f"the provider did not return JSON: {error}"
        time.sleep(min(2 ** attempt, 8))
    return last
