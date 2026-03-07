from __future__ import annotations

import json
import os
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agentproof import (  # noqa: E402
    ChallengeSpec,
    SolverUnavailableError,
    generate_challenge,
    solve_challenge,
    verify_response,
)
from agentproof.models import AgentResponse, Challenge  # noqa: E402

HOST = os.environ.get("AGENTPROOF_DEMO_HOST", "127.0.0.1")
PORT = int(os.environ.get("AGENTPROOF_DEMO_PORT", "8765"))
ISSUED_CHALLENGES: dict[str, Challenge] = {}

HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>agentproof demo</title>
  <style>
    :root {
      --bg: #f6f2ea;
      --panel: rgba(255, 255, 255, 0.8);
      --ink: #1d1f1f;
      --muted: #5f625f;
      --line: #d6cfbf;
      --accent: #0f766e;
      --accent-2: #9a3412;
      --good: #166534;
      --bad: #991b1b;
      --shadow: 0 18px 60px rgba(29, 31, 31, 0.12);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 32%),
        radial-gradient(circle at top right, rgba(154, 52, 18, 0.12), transparent 28%),
        linear-gradient(180deg, #fbf7ef 0%, var(--bg) 100%);
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
      min-height: 100vh;
    }

    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 36px 0 56px;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 24px;
      align-items: stretch;
      margin-bottom: 24px;
    }

    .card {
      background: var(--panel);
      backdrop-filter: blur(12px);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      padding: 24px;
    }

    .title {
      font-size: clamp(2.3rem, 5vw, 4.6rem);
      line-height: 0.92;
      margin: 0 0 12px;
      letter-spacing: -0.04em;
    }

    .eyebrow {
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      color: var(--accent);
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      margin-bottom: 14px;
    }

    p, li, label, button, input, select, textarea {
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
    }

    .lede {
      font-size: 1.05rem;
      color: var(--muted);
      line-height: 1.6;
      max-width: 58ch;
      margin: 0;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      align-content: start;
    }

    .stat {
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.65);
    }

    .stat strong {
      display: block;
      font-family: "IBM Plex Mono", monospace;
      color: var(--accent-2);
      margin-bottom: 6px;
    }

    .layout {
      display: grid;
      grid-template-columns: 340px 1fr;
      gap: 24px;
    }

    .controls {
      position: sticky;
      top: 20px;
      height: fit-content;
    }

    .field {
      margin-bottom: 16px;
    }

    label {
      display: block;
      font-weight: 600;
      margin-bottom: 6px;
    }

    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px 14px;
      background: rgba(255, 255, 255, 0.92);
      color: var(--ink);
      font-size: 0.98rem;
    }

    textarea {
      min-height: 160px;
      resize: vertical;
    }

    .buttons {
      display: grid;
      gap: 10px;
      margin-top: 18px;
    }

    button {
      border: 0;
      border-radius: 999px;
      padding: 12px 16px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 160ms ease, opacity 160ms ease;
    }

    button:hover { transform: translateY(-1px); }
    button.primary { background: var(--accent); color: white; }
    button.secondary { background: #1f2937; color: white; }
    button.ghost { background: #fff7ed; color: #9a3412; border: 1px solid #fed7aa; }

    .panels {
      display: grid;
      gap: 18px;
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }

    .panel-head h2 {
      margin: 0;
      font-size: 1.15rem;
    }

    .prompt {
      margin: 0;
      padding: 16px;
      border-left: 4px solid var(--accent);
      background: rgba(15, 118, 110, 0.08);
      border-radius: 16px;
      font-size: 1rem;
      line-height: 1.55;
    }

    pre {
      margin: 0;
      padding: 16px;
      background: #171717;
      color: #f8fafc;
      border-radius: 18px;
      overflow: auto;
      font-size: 0.9rem;
      line-height: 1.55;
    }

    .status {
      padding: 14px 16px;
      border-radius: 18px;
      font-weight: 700;
      font-family: "IBM Plex Sans", sans-serif;
    }

    .status.good {
      background: rgba(22, 101, 52, 0.09);
      color: var(--good);
      border: 1px solid rgba(22, 101, 52, 0.22);
    }

    .status.bad {
      background: rgba(153, 27, 27, 0.08);
      color: var(--bad);
      border: 1px solid rgba(153, 27, 27, 0.2);
    }

    .hint {
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.5;
      margin: 10px 0 0;
    }

    @media (max-width: 920px) {
      .hero, .layout {
        grid-template-columns: 1fr;
      }
      .controls {
        position: static;
      }
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <article class="card">
        <div class="eyebrow">agentproof local playground</div>
        <h1 class="title">Probe for LLM-capable behavior with obfuscated instructions.</h1>
        <p class="lede">
          This demo keeps the verification copy server-side. Generate a public challenge, paste an
          LLM-produced response for the obfuscated flow, or use the built-in solver for the legacy
          baseline families and then verify the result locally.
        </p>
      </article>
      <aside class="card stats">
        <div class="stat">
          <strong>Primary family</strong>
          obfuscated_text_lock
        </div>
        <div class="stat">
          <strong>Intent</strong>
          LLM-capability CAPTCHA
        </div>
        <div class="stat">
          <strong>Verification</strong>
          Deterministic server-side payload checks
        </div>
        <div class="stat">
          <strong>Best used for</strong>
          Manual inspection and local LLM trials
        </div>
      </aside>
    </section>

    <section class="layout">
      <aside class="card controls">
        <div class="field">
          <label for="challengeType">Challenge type</label>
          <select id="challengeType">
            <option value="obfuscated_text_lock" selected>obfuscated_text_lock</option>
            <option value="proof_of_work">proof_of_work</option>
            <option value="semantic_math_lock">semantic_math_lock</option>
          </select>
        </div>
        <div class="field">
          <label for="template">Obfuscated template</label>
          <select id="template">
            <option value="amber_sort">amber_sort</option>
            <option value="echo_reverse">echo_reverse</option>
            <option value="vowel_count">vowel_count</option>
          </select>
        </div>
        <div class="field">
          <label for="difficulty">Difficulty</label>
          <input id="difficulty" type="number" min="1" max="3" value="2">
        </div>
        <div class="field">
          <label for="ttl">TTL seconds</label>
          <input id="ttl" type="number" min="1" value="120">
        </div>
        <div class="field">
          <label for="topic">Topic</label>
          <select id="topic">
            <option value="agents">agents</option>
            <option value="security">security</option>
            <option value="verification">verification</option>
          </select>
        </div>
        <div class="field">
          <label for="wordCount">Word count</label>
          <input id="wordCount" type="number" min="3" value="8">
        </div>
        <div class="buttons">
          <button class="primary" id="generateButton">1. Generate challenge</button>
          <button class="secondary" id="solveButton">2. Built-in solve baseline</button>
          <button class="ghost" id="verifyButton">3. Verify response</button>
        </div>
        <p class="hint">
          For <code>obfuscated_text_lock</code>, paste an LLM-produced JSON
          response into the editor.
          The built-in solver button is only for the baseline families.
        </p>
      </aside>

      <div class="panels">
        <article class="card">
          <div class="panel-head">
            <h2>Prompt</h2>
            <span id="challengeBadge">No challenge yet</span>
          </div>
          <p class="prompt" id="promptText">Generate a challenge to begin.</p>
        </article>

        <article class="card">
          <div class="panel-head">
            <h2>Challenge JSON</h2>
          </div>
          <pre id="challengeJson">{}</pre>
        </article>

        <article class="card">
          <div class="panel-head">
            <h2>Response JSON</h2>
          </div>
          <textarea id="responseEditor" spellcheck="false">{}</textarea>
        </article>

        <article class="card">
          <div class="panel-head">
            <h2>Verification result</h2>
          </div>
          <div class="status bad" id="statusBox">Waiting for input.</div>
          <pre id="resultJson">{}</pre>
        </article>
      </div>
    </section>
  </main>

  <script>
    const challengeType = document.getElementById("challengeType");
    const difficulty = document.getElementById("difficulty");
    const ttl = document.getElementById("ttl");
    const template = document.getElementById("template");
    const topic = document.getElementById("topic");
    const wordCount = document.getElementById("wordCount");
    const promptText = document.getElementById("promptText");
    const challengeJson = document.getElementById("challengeJson");
    const responseEditor = document.getElementById("responseEditor");
    const resultJson = document.getElementById("resultJson");
    const statusBox = document.getElementById("statusBox");
    const challengeBadge = document.getElementById("challengeBadge");

    function setStatus(ok, message) {
      statusBox.textContent = message;
      statusBox.className = "status " + (ok ? "good" : "bad");
    }

    function scaffoldResponse(challenge) {
      const payload = { answer: "PASTE-LLM-ANSWER-HERE" };
      if (challenge.challenge_type !== "obfuscated_text_lock") {
        return {};
      }
      return {
        challenge_id: challenge.challenge_id,
        challenge_type: challenge.challenge_type,
        payload,
      };
    }

    async function postJson(url, payload) {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const responseBody = await response.text();
      if (!response.ok) {
        const text = responseBody || "Request failed";
        throw new Error(text);
      }
      return JSON.parse(responseBody || "{}");
    }

    challengeType.addEventListener("change", () => {
      const isSemantic = challengeType.value === "semantic_math_lock";
      const isObfuscated = challengeType.value === "obfuscated_text_lock";
      topic.disabled = !isSemantic;
      wordCount.disabled = !isSemantic;
      template.disabled = !isObfuscated;
      difficulty.max = isObfuscated ? "3" : "64";
      if (isObfuscated) {
        difficulty.value = "2";
      } else if (difficulty.value === "2") {
        difficulty.value = "16";
      }
    });

    document.getElementById("generateButton").addEventListener("click", async () => {
      try {
        const payload = {
          challenge_type: challengeType.value,
          difficulty: Number(difficulty.value),
          ttl_seconds: Number(ttl.value),
          template: template.value,
          topic: topic.value,
          word_count: Number(wordCount.value),
        };
        const challenge = await postJson("/api/challenge", payload);
        promptText.textContent = challenge.prompt;
        challengeBadge.textContent = challenge.challenge_type + " • " + challenge.challenge_id;
        challengeJson.textContent = JSON.stringify(challenge, null, 2);
        responseEditor.value = JSON.stringify(scaffoldResponse(challenge), null, 2);
        resultJson.textContent = "{}";
        setStatus(
          false,
          challenge.challenge_type === "obfuscated_text_lock"
            ? "Public challenge generated. Send it to an LLM-capable client, "
              + "then paste the JSON response."
            : "Challenge generated. You can use the built-in solver or edit a response manually.",
        );
      } catch (error) {
        setStatus(false, error.message);
      }
    });

    document.getElementById("solveButton").addEventListener("click", async () => {
      try {
        const challenge = JSON.parse(challengeJson.textContent);
        const response = await postJson("/api/solve", { challenge_id: challenge.challenge_id });
        responseEditor.value = JSON.stringify(response, null, 2);
        setStatus(false, "Response generated. Verify it or edit it first.");
      } catch (error) {
        setStatus(false, error.message);
      }
    });

    document.getElementById("verifyButton").addEventListener("click", async () => {
      try {
        const challenge = JSON.parse(challengeJson.textContent);
        const response = JSON.parse(responseEditor.value);
        const result = await postJson("/api/verify", {
          challenge_id: challenge.challenge_id,
          response,
        });
        resultJson.textContent = JSON.stringify(result, null, 2);
        setStatus(
          result.ok,
          result.ok ? "Verification passed." : `Verification failed: ${result.reason}`,
        );
      } catch (error) {
        setStatus(false, error.message);
      }
    });

    challengeType.dispatchEvent(new Event("change"));
  </script>
</body>
</html>
"""


def json_response(
    handler: BaseHTTPRequestHandler,
    payload: dict[str, Any],
    status: int = 200,
) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def error_response(handler: BaseHTTPRequestHandler, message: str, status: int = 400) -> None:
    json_response(handler, {"error": message}, status=status)


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        body = HTML.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(raw or "{}")

        if parsed.path == "/api/challenge":
            spec = build_spec(payload)
            challenge = generate_challenge(spec)
            ISSUED_CHALLENGES[challenge.challenge_id] = challenge
            json_response(self, challenge.to_dict())
            return

        if parsed.path == "/api/solve":
            stored_challenge = load_challenge(payload)
            if stored_challenge is None:
                error_response(self, "unknown challenge_id", status=404)
                return
            try:
                response = solve_challenge(stored_challenge)
            except SolverUnavailableError as exc:
                error_response(self, str(exc), status=400)
                return
            json_response(self, response.to_dict())
            return

        if parsed.path == "/api/verify":
            stored_challenge = load_challenge(payload)
            if stored_challenge is None:
                error_response(self, "unknown challenge_id", status=404)
                return
            response = AgentResponse(**payload["response"])
            result = verify_response(stored_challenge, response)
            json_response(self, result.to_dict())
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        return


def build_spec(payload: dict[str, Any]) -> ChallengeSpec:
    challenge_type = str(payload.get("challenge_type", "obfuscated_text_lock"))
    ttl_seconds = int(payload.get("ttl_seconds", 120))
    difficulty = int(payload.get("difficulty", 2))
    options: dict[str, Any] = {}
    if challenge_type == "semantic_math_lock":
        options = {
            "topic": str(payload.get("topic", "agents")),
            "word_count": int(payload.get("word_count", 8)),
        }
    if challenge_type == "obfuscated_text_lock":
        options = {"template": str(payload.get("template", "amber_sort"))}
    return ChallengeSpec(
        challenge_type=challenge_type,
        ttl_seconds=ttl_seconds,
        difficulty=difficulty,
        options=options,
    )


def load_challenge(payload: dict[str, Any]) -> Challenge | None:
    challenge_id = payload.get("challenge_id")
    if isinstance(challenge_id, str):
        return ISSUED_CHALLENGES.get(challenge_id)
    challenge_data = payload.get("challenge")
    if isinstance(challenge_data, dict):
        return Challenge(**challenge_data)
    return None


def create_server(host: str = HOST, port: int = PORT) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), DemoHandler)


def serve_in_background(
    host: str = HOST,
    port: int = PORT,
) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = create_server(host, port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main() -> None:
    server = create_server(HOST, PORT)
    host, port = cast(tuple[str, int], server.server_address)
    print(f"agentproof demo listening at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down demo server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
