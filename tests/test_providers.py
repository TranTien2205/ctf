"""The provider layer: the table, the price, and the Anthropic<->OpenAI edge.

Two claims are under test here and both are checkable without a network. The
first is that a non-Anthropic model runs the *same* loop - the adapter's job is
to make `chat(messages, tools, system)` mean the same thing on both wires, so
the tests drive it with recorded wire payloads rather than mocking the loop.
The second is that a cost in a report traces to a line in `models.json` and is
never invented, which is the only reason the number is worth printing.
"""
from __future__ import annotations

import json
import types

import pytest

from argus import models
from argus.llm import LLMError, ClaudeClient, make_client
from argus.providers import (OpenAICompatClient, _anthropic_to_openai,
                             _openai_to_anthropic, _tools_to_openai)


# --- the table --------------------------------------------------------------

def test_every_role_a_model_claims_is_described():
    described = set(models.roles())
    assert described, "models.json describes no roles"
    for key, spec in models.known().items():
        for role in spec.roles:
            assert role in described, (
                f"{key} claims role {role!r} which models.json never "
                "describes, so `argus models` cannot explain it")


def test_every_described_role_has_at_least_one_model():
    for role in models.roles():
        assert models.for_role(role, "cheap") is not None, (
            f"role {role!r} is described but no model serves it, so "
            f"--role {role} would abort a run")


def test_a_priced_model_names_a_credential_variable():
    for key, spec in models.known().items():
        if spec.usd_per_mtok_in == 0 and spec.usd_per_mtok_out == 0:
            continue  # a free/local endpoint may legitimately need no key
        assert spec.api_key_env, (
            f"{key} has a price but names no api_key_env, so the loop would "
            "fail at call time with nothing to tell the operator to set")


def test_prices_are_not_negative():
    for key, spec in models.known().items():
        assert spec.usd_per_mtok_in >= 0 and spec.usd_per_mtok_out >= 0, key


def test_cheap_is_not_more_expensive_than_strong():
    for role in models.roles():
        cheap = models.for_role(role, "cheap")
        strong = models.for_role(role, "strong")
        assert cheap and strong
        cheap_price = cheap.usd_per_mtok_in + cheap.usd_per_mtok_out
        strong_price = strong.usd_per_mtok_in + strong.usd_per_mtok_out
        assert cheap_price <= strong_price, (
            f"role {role}: policy 'cheap' picked {cheap.key} which costs more "
            f"than 'strong' {strong.key}")


def test_for_role_can_exclude_a_family_so_a_judge_is_independent():
    # a judge from the family that produced the finding is not a second
    # opinion, it is the same prior answering twice
    pick = models.for_role("judge", "strong", exclude_family="claude",
                           usable_only=False)
    assert pick is not None
    assert models.family(pick.key) != "claude"


def test_an_unknown_role_resolves_to_nothing_rather_than_a_default():
    assert models.for_role("nonexistent-role") is None


# --- the price --------------------------------------------------------------

def test_cost_is_linear_in_tokens_and_matches_the_table():
    spec = models.get("claude-sonnet-4-5")
    assert spec is not None
    expected = (1_000_000 * spec.usd_per_mtok_in
                + 100_000 * spec.usd_per_mtok_out) / 1e6
    assert spec.cost(1_000_000, 100_000) == pytest.approx(expected)


def test_cache_reads_bill_at_a_tenth_of_input():
    spec = models.get("claude-sonnet-4-5")
    full = spec.cost(1_000_000, 0)
    cached = spec.cost(0, 0, cache_read=1_000_000)
    assert cached == pytest.approx(full * 0.1)


def test_cost_ignores_negative_token_counts():
    spec = models.get("claude-sonnet-4-5")
    assert spec.cost(-5, -5, cache_read=-5) == 0.0


def test_a_free_model_costs_nothing():
    spec = models.get("local")
    assert spec is not None
    assert spec.cost(10**9, 10**9, cache_read=10**9) == 0.0


def test_an_unlisted_model_has_no_price_rather_than_a_guessed_one():
    assert models.get("some-model-nobody-published") is None


# --- translation: Anthropic -> OpenAI --------------------------------------

def test_a_tool_use_turn_becomes_an_openai_tool_call():
    out = _anthropic_to_openai([
        {"role": "user", "content": "probe the login form"},
        {"role": "assistant", "content": [
            {"type": "text", "text": "sending one request"},
            {"type": "tool_use", "id": "tu_1", "name": "http_request",
             "input": {"url": "http://x/login"}},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tu_1",
             "content": [{"type": "text", "text": "HTTP/1.1 200 OK"}]},
        ]},
    ], system="you are a tester")
    assert [m["role"] for m in out] == ["system", "user", "assistant", "tool"]
    call = out[2]["tool_calls"][0]
    assert call["id"] == "tu_1"
    assert call["function"]["name"] == "http_request"
    assert json.loads(call["function"]["arguments"]) == {
        "url": "http://x/login"}
    assert out[3]["tool_call_id"] == "tu_1"
    assert out[3]["content"] == "HTTP/1.1 200 OK"


def test_a_tool_result_precedes_the_user_text_of_the_same_turn():
    # OpenAI requires each tool message to answer the preceding tool_calls;
    # emitting the operator's text first would orphan the result
    out = _anthropic_to_openai([
        {"role": "user", "content": [
            {"type": "text", "text": "keep going"},
            {"type": "tool_result", "tool_use_id": "tu_9", "content": "body"},
        ]},
    ], system="")
    assert [m["role"] for m in out] == ["tool", "user"]


def test_a_block_list_system_prompt_is_flattened():
    out = _anthropic_to_openai(
        [{"role": "user", "content": "hi"}],
        system=[{"type": "text", "text": "rule one"},
                {"type": "text", "text": "rule two"}])
    assert out[0] == {"role": "system", "content": "rule one\n\nrule two"}


def test_an_empty_system_prompt_adds_no_message():
    out = _anthropic_to_openai([{"role": "user", "content": "hi"}], system="")
    assert [m["role"] for m in out] == ["user"]


def test_tool_schemas_move_into_the_function_shape():
    out = _tools_to_openai([{
        "name": "http_request", "description": "send one request",
        "input_schema": {"type": "object",
                         "properties": {"url": {"type": "string"}},
                         "required": ["url"]}}])
    assert out[0]["type"] == "function"
    fn = out[0]["function"]
    assert fn["name"] == "http_request"
    assert fn["parameters"]["required"] == ["url"]


def test_a_tool_with_no_schema_still_declares_an_object():
    out = _tools_to_openai([{"name": "finish"}])
    assert out[0]["function"]["parameters"]["type"] == "object"


# --- translation: OpenAI -> Anthropic --------------------------------------

def test_a_completion_with_a_tool_call_reads_as_tool_use():
    out = _openai_to_anthropic({
        "choices": [{"finish_reason": "tool_calls", "message": {
            "role": "assistant", "content": "about to probe",
            "tool_calls": [{"id": "call_7", "type": "function", "function": {
                "name": "http_request",
                "arguments": '{"url": "http://x/"}'}}]}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20}})
    assert out["stop_reason"] == "tool_use"
    kinds = [b["type"] for b in out["content"]]
    assert kinds == ["text", "tool_use"]
    use = out["content"][1]
    assert (use["id"], use["name"], use["input"]) == (
        "call_7", "http_request", {"url": "http://x/"})


def test_malformed_tool_arguments_survive_as_a_reportable_call():
    # dropping the call silently would make the model's turn vanish; the
    # dispatcher can report bad arguments, which the model can recover from
    out = _openai_to_anthropic({"choices": [{"message": {
        "tool_calls": [{"id": "c1", "function": {
            "name": "http_request", "arguments": "{not json"}}]}}]})
    use = out["content"][0]
    assert use["type"] == "tool_use"
    assert "__unparsed__" in use["input"]


def test_a_length_stop_is_reported_as_max_tokens():
    out = _openai_to_anthropic({"choices": [
        {"finish_reason": "length", "message": {"content": "truncat"}}]})
    assert out["stop_reason"] == "max_tokens"


def test_cached_tokens_are_not_billed_twice():
    # OpenAI's prompt_tokens includes the cached ones; Anthropic's does not.
    # Passing the raw figure through would charge each cached token at full
    # input price AND again at the cache rate.
    out = _openai_to_anthropic({
        "choices": [{"message": {"content": "ok"}}],
        "usage": {"prompt_tokens": 1000, "completion_tokens": 10,
                  "prompt_tokens_details": {"cached_tokens": 900}}})
    usage = out["usage"]
    assert usage["input_tokens"] == 100
    assert usage["cache_read_input_tokens"] == 900
    assert (usage["input_tokens"] + usage["cache_read_input_tokens"]
            == 1000), "the two fields must still account for every token"


def test_cached_tokens_cannot_exceed_the_prompt():
    out = _openai_to_anthropic({
        "choices": [{"message": {"content": "ok"}}],
        "usage": {"prompt_tokens": 10,
                  "prompt_tokens_details": {"cached_tokens": 999}}})
    assert out["usage"]["input_tokens"] == 0
    assert out["usage"]["cache_read_input_tokens"] == 10


def test_an_empty_completion_does_not_crash_the_loop():
    out = _openai_to_anthropic({})
    assert out["content"] == []
    assert out["stop_reason"] == "end_turn"


# --- the client -------------------------------------------------------------

def test_a_credential_is_refused_over_plaintext_http():
    with pytest.raises(LLMError) as exc:
        OpenAICompatClient(api_key="sk-secret",
                           api_base="http://api.example.com/v1/chat/completions",
                           model="gpt-4.1")
    assert "http" in str(exc.value).lower()


def test_a_local_endpoint_may_opt_out_of_that_refusal():
    client = OpenAICompatClient(
        api_key="none", api_base="http://127.0.0.1:11434/v1/chat/completions",
        model="local", allow_insecure_base=True)
    assert client.api_base.startswith("http://127.0.0.1")


def test_a_model_with_no_api_base_is_rejected_at_construction():
    with pytest.raises(LLMError):
        OpenAICompatClient(api_key="k", api_base="", model="gpt-4.1")


def test_chat_without_a_credential_names_the_variable_to_set():
    client = OpenAICompatClient(
        api_key="", api_base="https://api.openai.com/v1/chat/completions",
        model="gpt-4.1")
    with pytest.raises(LLMError) as exc:
        client.chat([{"role": "user", "content": "hi"}], [], "")
    assert "models.json" in str(exc.value)


def _cfg(model: str, **kw):
    base = {"model": model, "api_key": "sk-cfg", "auth_token": "",
            "api_base": "https://api.anthropic.com/v1/messages",
            "llm_max_tokens": 4096}
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_the_factory_sends_each_model_to_its_own_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    assert isinstance(make_client(_cfg("claude-sonnet-4-5")), ClaudeClient)
    assert isinstance(make_client(_cfg("gpt-4.1")), OpenAICompatClient)


def test_an_unknown_model_goes_to_anthropic_not_to_an_error():
    # a name this table does not know is far more likely a new Claude release
    # than a typo for a local server
    assert isinstance(make_client(_cfg("claude-sonnet-9-9")), ClaudeClient)


def test_an_explicit_api_base_wins_over_the_table(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    client = make_client(_cfg(
        "gpt-4.1", api_base="https://gateway.internal/v1/chat/completions"))
    assert client.api_base == "https://gateway.internal/v1/chat/completions"


def test_both_clients_expose_the_counters_the_loop_reports(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    for client in (make_client(_cfg("claude-sonnet-4-5")),
                   make_client(_cfg("gpt-4.1"))):
        for attr in ("calls", "input_tokens", "output_tokens",
                     "cache_read_tokens", "cache_write_tokens"):
            assert hasattr(client, attr), f"{type(client).__name__}.{attr}"
        assert callable(client.chat)


def test_the_two_clients_agree_on_the_chat_signature():
    import inspect
    a = inspect.signature(ClaudeClient.chat).parameters
    b = inspect.signature(OpenAICompatClient.chat).parameters
    assert list(a) == list(b), (
        "the loop calls chat() positionally; a diverging signature would "
        "break only on the provider nobody tested")


# --- the round trip, end to end, with no network ---------------------------

class _FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


class _FakeHttpx:
    """Records the outbound payload and replays a canned completion."""

    def __init__(self, payload):
        self.payload = payload
        self.sent = []

    def Client(self, **_kw):
        outer = self

        class _C:
            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *a):
                return False

            def post(self_inner, url, json=None, headers=None):
                outer.sent.append({"url": url, "json": json,
                                   "headers": headers})
                return _FakeResponse(outer.payload)
        return _C()


def test_a_full_turn_crosses_both_translations(monkeypatch):
    fake = _FakeHttpx({
        "choices": [{"finish_reason": "tool_calls", "message": {
            "content": None,
            "tool_calls": [{"id": "call_1", "function": {
                "name": "http_request",
                "arguments": '{"url": "http://127.0.0.1:8081/"}'}}]}}],
        "usage": {"prompt_tokens": 500, "completion_tokens": 40,
                  "prompt_tokens_details": {"cached_tokens": 400}}})
    monkeypatch.setattr("argus.providers.httpx", fake)
    client = OpenAICompatClient(
        api_key="sk-test",
        api_base="https://api.openai.com/v1/chat/completions",
        model="gpt-4.1")
    out = client.chat(
        messages=[{"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tu_0", "content": "200 OK"}]}],
        tools=[{"name": "http_request", "description": "send one",
                "input_schema": {"type": "object",
                                 "properties": {"url": {"type": "string"}}}}],
        system="you are a tester")

    sent = fake.sent[0]["json"]
    assert sent["model"] == "gpt-4.1"
    assert sent["tools"][0]["function"]["name"] == "http_request"
    assert [m["role"] for m in sent["messages"]] == ["system", "tool"]
    assert fake.sent[0]["headers"]["authorization"] == "Bearer sk-test"

    assert out["stop_reason"] == "tool_use"
    assert out["content"][0]["name"] == "http_request"
    assert client.calls == 1
    assert (client.input_tokens, client.cache_read_tokens) == (100, 400)
    assert client.output_tokens == 40

    spec = models.get("gpt-4.1")
    assert spec.cost(client.input_tokens, client.output_tokens,
                     cache_read=client.cache_read_tokens) == pytest.approx(
        (100 * spec.usd_per_mtok_in + 400 * spec.usd_per_mtok_in * 0.1
         + 40 * spec.usd_per_mtok_out) / 1e6)


def test_a_non_retryable_provider_error_is_raised_not_retried(monkeypatch):
    class _Bad(_FakeHttpx):
        def Client(self, **_kw):
            outer = self

            class _C:
                def __enter__(s):
                    return s

                def __exit__(s, *a):
                    return False

                def post(s, url, json=None, headers=None):
                    outer.sent.append(1)
                    r = _FakeResponse({"error": "bad request"})
                    r.status_code = 400
                    return r
            return _C()

    fake = _Bad({})
    monkeypatch.setattr("argus.providers.httpx", fake)
    client = OpenAICompatClient(
        api_key="k", api_base="https://api.openai.com/v1/chat/completions",
        model="gpt-4.1")
    with pytest.raises(LLMError):
        client.chat([{"role": "user", "content": "hi"}], [], "")
    assert len(fake.sent) == 1, "a 400 is the operator's bug, not a blip"


# --- the cost that reaches summary.json ------------------------------------

def test_the_loop_reports_a_price_only_when_the_table_has_one():
    from argus.loop import AgentLoop

    class _L:
        input_tokens, output_tokens = 1_000_000, 100_000
        cache_read_tokens = cache_write_tokens = 0

    stub = types.SimpleNamespace(
        cfg=types.SimpleNamespace(model="claude-sonnet-4-5"), llm=_L())
    stub._token_stats = lambda: AgentLoop._token_stats(stub)
    priced = AgentLoop._cost_stats(stub)
    assert priced["usd"] == pytest.approx(4.5)
    assert priced["table_version"] == models.table_version()

    stub.cfg = types.SimpleNamespace(model="model-nobody-published")
    unpriced = AgentLoop._cost_stats(stub)
    assert unpriced["usd"] is None
    assert "models.json" in unpriced["basis"]


# --- a model per team role -------------------------------------------------

def _team(cfg):
    import argus.team.coordinator as coord
    return type("_T", (coord.TeamRun,),
                {"__init__": lambda s, c: setattr(s, "cfg", c)})(cfg)


def _role_cfg(**kw):
    base = {"model": "claude-sonnet-4-5", "role_models": True,
            "policy": "cheap"}
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_role_models_is_off_unless_asked_for():
    team = _team(_role_cfg(role_models=False))
    picks = {r: team.model_for(r)
             for r in ("lead", "recon", "exploit", "report")}
    assert set(picks.values()) == {"claude-sonnet-4-5"}


def test_each_role_maps_onto_a_job_the_table_describes():
    import argus.team.coordinator as coord
    described = set(models.roles())
    for role, table_role in coord.TeamRun.TABLE_ROLE.items():
        assert table_role in described, f"{role} -> {table_role}"


def test_a_pick_with_no_credential_falls_back_to_the_run_model(monkeypatch):
    for name in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY",
                 "ARGUS_LOCAL_API_KEY", "OLLAMA_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    team = _team(_role_cfg())
    # every non-Anthropic pick is unusable, so each role runs the run's model
    for role in ("lead", "recon", "exploit", "report"):
        pick = team.model_for(role)
        spec = models.get(pick)
        assert spec is None or spec.provider == "anthropic" or spec.credential()


def test_a_credentialed_provider_is_picked_for_its_role(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-y")
    team = _team(_role_cfg())
    assert models.get(team.model_for("lead")).provider == "openai"
    assert "planner" in models.get(team.model_for("lead")).roles


def test_the_local_endpoint_is_never_picked_on_someone_elses_key(monkeypatch):
    # `local` costs nothing, so cost ordering puts it first - but an
    # OPENAI_API_KEY is not evidence that a server is listening on this host
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    monkeypatch.delenv("ARGUS_LOCAL_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    team = _team(_role_cfg())
    picks = {team.model_for(r) for r in ("lead", "recon", "exploit", "report")}
    assert "local" not in picks
    monkeypatch.setenv("ARGUS_LOCAL_API_KEY", "1")
    picks = {team.model_for(r) for r in ("lead", "recon", "exploit", "report")}
    assert "local" in picks, "an opted-in local server should be reachable"


def test_strong_policy_reaches_for_the_strong_models():
    team = _team(_role_cfg(policy="strong"))
    assert team.model_for("lead") == "claude-opus-4-5"
    assert team.model_for("exploit") == "claude-opus-4-5"


def test_the_team_cost_breakdown_names_a_model_per_agent():
    team = _team(_role_cfg(role_models=False))
    team._results = {
        "lead": {"model": "claude-opus-4-5",
                 "llm_tokens": {"in": 100_000, "out": 10_000,
                                "cache_read": 0}},
        "recon-1": {"model": "gpt-4.1-mini",
                    "llm_tokens": {"in": 50_000, "out": 5_000,
                                   "cache_read": 40_000}},
        "exploit-1": {"model": "a-model-nobody-published",
                      "llm_tokens": {"in": 1_000, "out": 100}},
    }
    out = team._cost_breakdown()
    assert out["per_agent"]["lead"]["usd"] == pytest.approx(
        models.get("claude-opus-4-5").cost(100_000, 10_000))
    assert out["per_agent"]["exploit-1"]["usd"] is None
    assert out["unpriced"] == ["exploit-1 (a-model-nobody-published)"]
    # the total is the sum of the priced agents only, and never a zero
    # standing in for an unknown
    assert out["usd"] == pytest.approx(
        out["per_agent"]["lead"]["usd"] + out["per_agent"]["recon-1"]["usd"])
    assert "models.json" in out["basis"]


def test_an_agent_that_reported_nothing_does_not_break_the_breakdown():
    team = _team(_role_cfg(role_models=False))
    team._results = {"lead": None, "recon-1": {}, "exploit-1": "crashed"}
    out = team._cost_breakdown()
    assert out["usd"] == 0.0
    assert out["per_agent"]["recon-1"]["model"] == "claude-sonnet-4-5"


# --- the credential must never be the wrong provider's -------------------

def test_the_anthropic_key_is_never_sent_to_another_provider(monkeypatch):
    """`make_client` fell back to `cfg.api_key` when the picked model's own
    variable was unset — and `cfg.api_key` is the ANTHROPIC key, which this
    client sends as a Bearer token to whatever host the table names. So
    `--model gpt-4.1` with no OPENAI_API_KEY shipped the operator's Anthropic
    credential to api.openai.com. Found by an adversarial audit of this
    session's own code."""
    for name in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY",
                 "ARGUS_LOCAL_API_KEY", "OLLAMA_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    for model in ("gpt-4.1", "gpt-4.1-mini", "deepseek-chat", "local"):
        with pytest.raises(LLMError) as exc:
            make_client(_cfg(model, api_key="sk-ANTHROPIC-SECRET"))
        message = str(exc.value)
        assert "sk-ANTHROPIC-SECRET" not in message
        assert "no credential for" in message
        spec = models.get(model)
        assert any(v in message for v in spec.api_key_env), message


def test_a_model_with_its_own_credential_uses_exactly_that(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-only")
    client = make_client(_cfg("gpt-4.1", api_key="sk-ANTHROPIC-SECRET"))
    assert client.api_key == "sk-openai-only"


def test_an_operator_api_base_does_not_inherit_the_insecure_opt_in(monkeypatch):
    """`allow_insecure_base` is a statement about the model's OWN endpoint — a
    loopback server. Applying it to a base URL from `ANTHROPIC_BASE_URL` turned
    the plaintext-credential refusal off for any host."""
    monkeypatch.setenv("ARGUS_LOCAL_API_KEY", "x")
    with pytest.raises(LLMError) as exc:
        make_client(_cfg("local",
                         api_base="http://evil.example/v1/chat/completions"))
    assert "http" in str(exc.value).lower()
    # the table's own loopback base still works
    assert make_client(_cfg("local")).api_base.startswith("http://127.0.0.1")


def test_for_role_skips_a_model_whose_credential_is_not_set(monkeypatch):
    """`local` is priced at zero, so cost ordering put it ahead of every paid
    model and `--role breadth` resolved to a loopback server that is almost
    never running. A role that resolves to a model the operator cannot call
    is not a cheap answer; it is a run that dies on its first request."""
    for name in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY",
                 "ARGUS_LOCAL_API_KEY", "OLLAMA_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    for role in models.roles():
        pick = models.for_role(role, "cheap")
        assert pick is not None, role
        assert pick.provider == "anthropic", (
            f"{role} resolved to {pick.key}, whose credential is unset")
    # and the table's own answer is still askable
    assert models.for_role("breadth", "cheap", usable_only=False).key == "local"
    monkeypatch.setenv("ARGUS_LOCAL_API_KEY", "1")
    assert models.for_role("breadth", "cheap").key == "local"


def test_a_malformed_usage_number_does_not_end_the_run():
    """A server answering `"prompt_tokens": "many"` raised ValueError and
    killed the run; `completion_tokens` was passed through unclamped, so a
    string reached the cost arithmetic instead. A token count this client
    cannot read is zero: it is a number for a report, not evidence."""
    out = _openai_to_anthropic({
        "choices": [{"message": {"content": "ok"}}],
        "usage": {"prompt_tokens": "many", "completion_tokens": "x",
                  "prompt_tokens_details": {"cached_tokens": "lots"}}})
    usage = out["usage"]
    assert usage == {"input_tokens": 0, "output_tokens": 0,
                     "cache_read_input_tokens": 0}
    for value in usage.values():
        assert isinstance(value, int)


def test_a_content_part_list_is_not_an_empty_turn():
    """Some OpenAI-compatible servers answer with content PARTS. Reading only
    `str` made that an empty turn, and an empty turn makes the agent stop
    calling tools without saying why."""
    out = _openai_to_anthropic({"choices": [{"message": {"content": [
        {"type": "text", "text": "first "},
        {"type": "text", "text": "second"}]}}]})
    assert out["content"] == [{"type": "text", "text": "first second"}]


def test_a_team_run_prices_each_worker_at_the_model_it_used(monkeypatch):
    """`loop.run()` reports `cfg.model`, and a worker's loop was built with
    the TEAM's cfg while its client talked to the role's model - so every
    worker was priced at the wrong rate, defeating --role-models."""
    import dataclasses
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-y")
    team = _team(_role_cfg())
    picks = {r: team.model_for(r) for r in ("lead", "recon", "exploit")}
    assert len(set(picks.values())) > 1, picks
    team._results = {
        "lead": {"model": picks["lead"],
                 "llm_tokens": {"in": 100_000, "out": 10_000,
                                "cache_read": 0}},
        "recon-1": {"model": picks["recon"],
                    "llm_tokens": {"in": 50_000, "out": 5_000,
                                   "cache_read": 0}},
        # a crashed worker has no result dict to name its model
        "exploit-1": {"error": "RuntimeError: boom", "turns": 0},
    }
    out = team._cost_breakdown()
    assert out["per_agent"]["lead"]["model"] == picks["lead"]
    assert out["per_agent"]["recon-1"]["model"] == picks["recon"]
    assert out["per_agent"]["exploit-1"]["model"] == picks["exploit"]
    assert dataclasses.is_dataclass or True
