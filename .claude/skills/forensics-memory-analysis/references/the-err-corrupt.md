# Error — corrupt/truncated image

Symptom: plugins error on truncated reads. Fix: check file size vs
expected; a partial dump still yields strings — ioc_scan anyway.
