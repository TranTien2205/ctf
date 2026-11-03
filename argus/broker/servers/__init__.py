"""One module per MCP server. Each exposes `SERVER`, a `mcp.Server` instance."""

SERVER_NAMES = ("http", "recon", "fuzz", "scan", "exploit", "proof", "web", "session",
                "ledger", "knowledge")


def load(name: str):
    """Import one server by name, late, so a missing optional dependency in one
    server never stops the others from being served."""
    if name not in SERVER_NAMES:
        raise KeyError(f"no server {name!r}; known: {SERVER_NAMES}")
    module = __import__(f"argus.broker.servers.{name}", fromlist=["SERVER"])
    return module.SERVER


def load_all() -> dict:
    servers = {}
    for name in SERVER_NAMES:
        try:
            servers[name] = load(name)
        except Exception as error:                                  # noqa: BLE001
            servers[name] = error
    return servers
