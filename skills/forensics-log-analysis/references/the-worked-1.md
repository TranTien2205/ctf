# Worked — the attacking IP

1. log_summary.py summary → top IP is 10x the rest.
2. field --regex for its paths → a GET /flag? or an exploit request.
3. window around the hit → the full request + response.

## Notes

- The top-IP alone isn't the answer — its PATHS are; distribute
  them for the exploit request.
- The window shows whether the odd request returned 200 (worked)
  or 4xx (tried-and-failed).
- Record the IP, the count, and the verbatim exploit-request line.
