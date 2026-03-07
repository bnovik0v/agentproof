from __future__ import annotations

from agentproof.baselines import literal_oldstyle_solver, normalized_rule_parser
from agentproof.models import Challenge


def test_literal_oldstyle_solver_solves_amber_prompt() -> None:
    challenge = Challenge(
        challenge_id="old-amber",
        challenge_type="obfuscated_text_lock",
        prompt=(
            "keep only shards carrying the amber tag\n"
            "task: order the kept shard words by slot number from low to high\n"
            "deck: slot2 amber orbit\n"
            "deck: slot1 amber ember\n"
            "deck: slot4 amber signal\n"
        ),
        issued_at="2026-03-07T00:00:00+00:00",
        expires_at="2026-03-08T00:00:00+00:00",
        data={},
    )
    response = literal_oldstyle_solver(challenge)
    assert response is not None
    assert response.payload["answer"] == "EMBER-ORBIT-SIGNAL"


def test_literal_oldstyle_solver_solves_echo_prompt() -> None:
    challenge = Challenge(
        challenge_id="old-echo",
        challenge_type="obfuscated_text_lock",
        prompt=(
            "keep only shards carrying the echo mark\n"
            "task: reverse each kept shard word\n"
            "task: order the transformed words by lane number from high to low\n"
            "deck: lane4 echo ember\n"
            "deck: lane1 echo mira\n"
            "deck: lane3 echo fable\n"
        ),
        issued_at="2026-03-07T00:00:00+00:00",
        expires_at="2026-03-08T00:00:00+00:00",
        data={},
    )
    response = literal_oldstyle_solver(challenge)
    assert response is not None
    assert response.payload["answer"] == "REBME-ELBAF-ARIM"


def test_normalized_rule_parser_solves_redesigned_obfuscated_prompt() -> None:
    challenge = Challenge(
        challenge_id="new-amber",
        challenge_type="obfuscated_text_lock",
        prompt=(
            "gl1tch//llm-cap-v1::d2\n"
            "legend: warm class means the amber label\n"
            "brief: retain only entries in the warm class\n"
            "brief: rank the kept terms by rung from low to high\n"
            "ledger: rung=2 | label=amber | term=orbit\n"
            "ledger: rung=1 | label=amber | term=ember\n"
            "ledger: rung=4 | label=amber | term=signal\n"
            "ledger: rung=3 | label=cobalt | term=mira\n"
        ),
        issued_at="2026-03-07T00:00:00+00:00",
        expires_at="2026-03-08T00:00:00+00:00",
        data={},
    )
    response = normalized_rule_parser(challenge)
    assert response is not None
    assert response.payload["answer"] == "EMBER-ORBIT-SIGNAL"


def test_normalized_rule_parser_solves_multi_pass_prompt() -> None:
    challenge = Challenge(
        challenge_id="new-multi",
        challenge_type="multi_pass_lock",
        prompt=(
            "legend: chorus mark means the echo label\n"
            "brief: retain only cards in the chorus mark\n"
            "brief: trim each kept card to its first 4 letters\n"
            "brief: rank the kept terms by perch from high to low\n"
            "tray: perch=1 | label=echo | term=mira\n"
            "tray: perch=4 | label=echo | term=ember\n"
            "tray: perch=3 | label=echo | term=fable\n"
            "tray: perch=2 | label=glow | term=orbit\n"
        ),
        issued_at="2026-03-07T00:00:00+00:00",
        expires_at="2026-03-08T00:00:00+00:00",
        data={},
    )
    response = normalized_rule_parser(challenge)
    assert response is not None
    assert response.payload["answer"] == "EMBE-FABL-MIRA"


def test_normalized_rule_parser_solves_vowel_trim_prompt() -> None:
    challenge = Challenge(
        challenge_id="new-vowel",
        challenge_type="multi_pass_lock",
        prompt=(
            "brief: retain only piece words whose vowel load equals two\n"
            "brief: drop the final letter from each kept piece\n"
            "brief: rank the kept terms alphabetically descending\n"
            "board: piece=orbit\n"
            "board: piece=rivet\n"
            "board: piece=cinder\n"
            "board: piece=glyph\n"
        ),
        issued_at="2026-03-07T00:00:00+00:00",
        expires_at="2026-03-08T00:00:00+00:00",
        data={},
    )
    response = normalized_rule_parser(challenge)
    assert response is not None
    assert response.payload["answer"] == "RIVE-ORBI-CINDE"
