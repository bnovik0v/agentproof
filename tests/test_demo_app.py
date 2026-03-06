from __future__ import annotations

import importlib.util
import json
import time
import urllib.request
from pathlib import Path
from types import ModuleType
from typing import Any, cast


def load_demo_app_module() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "demo" / "app.py"
    spec = importlib.util.spec_from_file_location("agentproof_demo_app", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load demo module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request_json(url: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        return cast(dict[str, object], json.loads(response.read().decode("utf-8")))


def test_demo_roundtrip() -> None:
    module = load_demo_app_module()
    server, thread = module.serve_in_background(port=0)
    host, port = cast(tuple[str, int], server.server_address)
    base_url = f"http://{host}:{port}"
    try:
        for _ in range(10):
            if thread.is_alive():
                break
            time.sleep(0.05)

        challenge = request_json(
            f"{base_url}/api/challenge",
            {"challenge_type": "proof_of_work", "difficulty": 8, "ttl_seconds": 120},
        )
        response = request_json(f"{base_url}/api/solve", challenge)
        result = request_json(
            f"{base_url}/api/verify",
            {"challenge": challenge, "response": response},
        )

        assert challenge["challenge_type"] == "proof_of_work"
        assert "prompt" in challenge
        response_payload = cast(dict[str, Any], response["payload"])
        assert "nonce" in response_payload
        assert result["ok"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
