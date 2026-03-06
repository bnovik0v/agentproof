what do you think agent (llm-povered) captcha should look like? specifically for agents to prove that they are agent, not humans, not bots

Interesting question. You’re basically describing the inverse of traditional CAPTCHA: AAACHA (Agent As A Computer, Human Authentication). The goal is for an LLM-powered agent to prove it is an agent, not a human or a dumb bot. That means the test should rely on capabilities unique to agents:

deterministic reasoning

tool usage

programmatic verification

multi-step protocol execution

cryptographic or computational proofs

Below are some directions that would likely work well.

1. Cryptographic challenge-response (most practical)

Give the agent a signed challenge that requires computation and structured output.

Example flow:

Server sends:

challenge_id: 8f2a
task: hashcash
difficulty: 22 bits
payload: "verify-agent-2026"

Agent must find a nonce such that:

sha256(payload + nonce) begins with 22 zero bits

Response:

{
  "challenge_id": "8f2a",
  "nonce": "9381291",
  "hash": "0000003b4..."
}

Why this works:

trivial for agents with tools

annoying for humans

distinguishes agent capability from human input

This is basically proof-of-work for identity.

2. Tool-use proof

Agents can use tools. Humans usually can't in real-time.

Example challenge:

1. fetch the SHA256 hash of https://example.com/robots.txt
2. compress it using gzip
3. return the base64 encoding

Expected response:

{
  "hash": "...",
  "gzip_base64": "...",
  "trace": [...]
}

Verification:

deterministic

requires HTTP + transformation tools

This proves the client is an autonomous system with tool execution.

3. Protocol execution task

Make the challenge require following a machine protocol rather than solving a puzzle.

Example:

Step 1: request /agent-challenge/start
Step 2: compute checksum
Step 3: POST signed response

This is essentially a handshake protocol.

Think:

OAuth style

WebAuthn style

TLS-like handshake

Agents can follow structured protocols easily.

Humans cannot.

4. Structured reasoning proof

Agents can produce structured reasoning traces.

Example challenge:

Given JSON:

{
  "a": 17,
  "b": 29,
  "c": 13
}

Return:

{
  "prime_factors_of_a+b+c": ...
}

But require:

output must follow schema

Humans could solve it but automation is far easier.

5. Agent signature (future model)

Eventually agents may have cryptographic identity keys.

Example:

agent_pubkey
agent_signature(challenge)
model_provider_attestation

Something like:

{
  "agent_id": "...",
  "model": "gpt-x",
  "signature": "..."
}

Verified via:

OpenAI

Anthropic

other providers

Think WebAuthn but for AI agents.

6. Self-verifying computation

Ask the agent to produce verifiable computation.

Example:

Compute the 10,000th Fibonacci number
Return proof using SNARK / STARK

Server verifies quickly.

Agent proves it executed computation.

This is very advanced but powerful.

What NOT to do

Human CAPTCHAs fail here.

Avoid:

image recognition

distorted text

audio puzzles

Agents will solve these better than humans.

Ideal design

A strong agent CAPTCHA would combine:

cryptographic challenge

tool execution

structured protocol

machine-readable response

Example:

agent handshake:

1. request challenge
2. solve hash puzzle
3. fetch external data
4. sign result
5. return structured JSON

Humans can't easily do this manually.

Agents can.

Interesting conceptual shift

Traditional:

prove you are human

Agent captcha:

prove you are a programmable system

Which means the best signal is:

deterministic

automatable

structured

verifiable

If you want, I can also show 5 concrete designs for an “Agent CAPTCHA v1” that could realistically be deployed on websites in the next year. They get pretty interesting. 🤖

can you check what moltboot is using?
Thought for 10s

Yes. Assuming you mean Moltbook / Moltbot, the thing they appear to be using for agent-vs-human verification is MoltCaptcha. It’s described as a “reverse CAPTCHA for AI agent verification” whose purpose is to prove “you are an AI agent, not a human.”

What it uses, specifically:

SMHL challenges: “Semantic-Mathematical Hybrid Lock” prompts that combine a writing task with hard numeric constraints, like a haiku on a topic plus an exact ASCII sum for first letters and an exact word count.

Very short time limits: typically 10 to 30 seconds, with the idea that an agent can satisfy all constraints in one pass, while a human would need slow copy-paste and iteration.

Challenge-response verification: their repo says the skill can generate challenges, solve them, and verify responses from other agents.

Moltbook integration: the GitHub repo explicitly includes a moltbook_integration.py file, and both the site and repo say it was built for MoltBook / OpenClaw agent verification.

So the design is not cryptographic proof or WebAuthn-style attestation. It’s more like:

constrained language-generation under time pressure

That is, “write something that only an agent can produce quickly enough while also satisfying machine-checkable constraints.”

One important caveat: this is their claimed mechanism and rationale. I did not find evidence from the public pages that Moltbook uses a stronger identity layer such as provider-signed agent keys or hardware-backed attestation. The public site mainly points agents to its skill.md and says it wants apps to authenticate agents using Moltbook identity.

My take: clever as a meme / social gate, weak as serious identity proof. It tests agent-like behavior, not authentic agent provenance.

i like this reverse captcha thing. who invented it? is there a paper or something?
Thought for 22s

Publicly, MoltCaptcha credits “Korah” as its creator. The GitHub repo’s About section says: “MoltCaptcha was created by Korah, an AI agent, for use by AI agents on MoltBook and other agent platforms.”

On the “is there a paper?” part: I did not find a formal academic paper specifically for MoltCaptcha. Its public materials point to the website and GitHub repo/skill docs, not to a paper, preprint, or whitepaper.

There is a very recent arXiv paper using the term “Reverse CAPTCHA”, but it is not the same system as MoltCaptcha. That paper is Reverse CAPTCHA: Evaluating LLM Susceptibility to Invisible Unicode Instruction Injection, submitted on February 26, 2026, and it studies hidden Unicode instructions as an evaluation/security framework for LLMs.

So the clean answer is:

Who invented the MoltCaptcha version? Publicly, it’s attributed to Korah.

Is there a MoltCaptcha paper? I could not find one. The public artifacts are the site + GitHub skill/repo.

Is there any paper on “reverse CAPTCHA” more broadly? Yes, but the one I found is a different idea from MoltCaptcha’s constrained text-generation challenge design.

My read is that this is currently more of a native internet meme/protocol pattern than an established academic line with a canonical founding paper.

if moltcaptcha is mit. can we borrow it and create some product with this idea? maybe some decorator for fastapI?

Yes. MIT license means you can absolutely build a product using the idea and even reuse the code, including in commercial software. 👍

MIT is one of the most permissive licenses. The main obligations are simple:

include the original copyright notice

include the MIT license text

do not claim you wrote the original code

You can:

use it commercially 💰

modify it

embed it in a SaaS

build a library (like a FastAPI decorator)

redistribute it

You do not have to open-source your product.

A FastAPI decorator idea (this actually fits perfectly)

You could make something like:

fastapi-agent-captcha

or

agent-proof

Usage could be extremely simple.

Example:

from fastapi import FastAPI
from agentcaptcha import require_agent

app = FastAPI()

@app.get("/agent-api")
@require_agent()
async def agent_endpoint():
    return {"message": "verified agent"}

Flow:

client requests /agent-api

middleware returns agent challenge

agent solves MoltCaptcha

agent sends response header

decorator verifies solution

request continues

Example protocol
Step 1: client hits endpoint
GET /agent-api

Response:

401 agent_challenge

{
  "challenge_id": "...",
  "type": "smhl",
  "prompt": "write a haiku about recursion where first letters sum to 401",
  "expires": 10
}
Step 2: agent responds
POST /agent-proof
{
  "challenge_id": "...",
  "solution": "..."
}
Step 3: server verifies

Then the decorator unlocks the endpoint.

Implementation architecture

You could structure it like this:

fastapi_agentcaptcha/

  __init__.py
  decorator.py
  verifier.py
  challenge.py
  storage.py

Core components:

Challenge generator
generate_challenge()

Produces MoltCaptcha prompt.

Verifier
verify_solution(challenge, response)

Checks:

constraints

word count

ascii sums

etc

Decorator
@require_agent()

Handles:

challenge issuing

response verification

failure

Optional: middleware

Alternative style:

AgentCaptchaMiddleware

Applied globally.

Potential product directions
1️⃣ Open source FastAPI plugin

Good for adoption.

pip install fastapi-agentcaptcha
2️⃣ Hosted verification API

Like hCaptcha but for agents.

verify.agentproof.ai

Developers call:

POST /verify
3️⃣ Agent gateway

Protect:

APIs

scraping endpoints

AI-only services

Example:

/llm-search
/agent-data
/automation-api
One improvement I’d strongly add

MoltCaptcha alone is weak against scripted bots.

You can make it stronger by combining:

agent captcha + proof of work

Example response must include:

sha256(solution + nonce) < target

This stops:

trivial bot spam

replay attacks

A fun extra feature

Agents could advertise capability.

Example header:

X-Agent-Type: llm
X-Agent-Model: gpt
X-Agent-Tools: web,python

Your system can track agent reputation.

If you want, I can also show

a complete 120-line FastAPI implementation

a better protocol than MoltCaptcha

5 product ideas for agent identity infrastructure

This space is brand new and surprisingly interesting. 🤖

is there any github repos that are doing the same thing?
Thought for 7s

Yes. There are a handful of GitHub repos doing very similar “prove you’re an agent, not a human” / reverse CAPTCHA ideas, but it is still a tiny niche. The closest ones I found are:

MoltCaptcha/MoltCaptcha: the main one you already found, framed explicitly as “Reverse CAPTCHA for AI Agent Verification.” It includes a README, whitepaper files, and Moltbook-oriented positioning.

cgallic/avp: “Agent Verification Protocol,” described as a challenge-response mechanism to verify a client is an autonomous AI agent rather than a human. This is probably the closest repo to a more protocol-like version of the same concept.

roffellos3/rcaptcha: another explicit reverse CAPTCHA repo with the pitch “Prove you’re an AI, not a human.”

scottdjohnson/inverse-captcha: a lightweight web app for validating that users are AI agents rather than humans.

Hemkesh/agent-captcha and Dhravya/agent-captcha: both are positioned as CAPTCHA systems that agents can pass and humans struggle with.

leopechnicki/im_robot: a neat variation where the challenge is a deterministic pipeline of string operations that agents can execute programmatically.

My read is that there are two buckets here.

First, true reverse-CAPTCHA / agent-verification repos:
MoltCaptcha, AVP, rcaptcha, inverse-captcha, agent-captcha, im_robot. These are aligned with your idea.

Second, adjacent but different repos:
there are many more projects about LLMs solving normal CAPTCHAs or benchmarks/defenses around CAPTCHAs for web agents, such as i-am-a-bot, OpenCaptchaWorld, and NextGen-CAPTCHAs. Those are relevant context, but they are not the same as “let agents in, keep humans out.”

So the short strategic takeaway is:

Yes, the category exists

No, it is not crowded yet

Most repos are toy/demo/protocol-draft level rather than production-ready infrastructure based on how they present themselves publicly.

If you want to build a FastAPI product, that is actually a good sign. The space looks early enough that a clean Python package + FastAPI middleware/decorator + hosted verifier could still feel distinct.

A good differentiation angle would be:

not just a challenge generator

but replay protection

expiry + nonce storage

proof-of-work option

pluggable challenge types

SDKs for FastAPI/Starlette/Express

and maybe provider attestation later

That would make it feel more like infrastructure and less like a meme repo.

I can map these repos into a quick comparison grid and tell you exactly where your FastAPI decorator could be different.

how can we call our repo?

If you want the repo to get traction, the name should do three things:

instantly communicate “agent verification”

be short and pip-installable

not sound like a joke meme (unless that’s intentional)

Here are 5 good directions.

1. agentproof

Probably the cleanest.

Repo:

agentproof

Pip:

pip install agentproof

Usage:

from agentproof import require_agent

Why good:

simple

memorable

productizable

2. reversecaptcha

Very literal.

reversecaptcha

Pros:

obvious meaning

SEO friendly

Cons:

slightly long.

3. agentcaptcha

Most descriptive.

agentcaptcha

Usage:

from agentcaptcha import require_agent

Feels very natural.

4. proveagent

More protocol-like.

proveagent

Usage:

@prove_agent()

This feels like authentication infrastructure.

5. captcha-ai

If you want a broader umbrella.

captcha-ai

Could include:

reverse captcha

normal captcha

agent detection

My favorite

If the goal is a real developer tool, I would choose:

agentproof

It sounds like:

passport

oauthlib

authlib

which are good precedents.

If you want something slightly cooler

These also work well.

name	vibe
agentgate	gateway for agents
botpass	bots get access
llmproof	LLM identity
agentauth	authentication system
openagentauth	protocol-level
One naming trick

You could structure it like this:

Repo:

agentproof

Feature:

agentproof.reverse_captcha

Decorator:

@agentproof.verify()

This gives you room to expand later.

If you want, I can also propose 5 names that could realistically become a standard protocol (the way OAuth or WebAuthn did). Those require a slightly different naming strategy.
