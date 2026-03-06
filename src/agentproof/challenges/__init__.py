"""Challenge handler registry."""

from agentproof.challenges.base import ChallengeHandler
from agentproof.challenges.proof_of_work import ProofOfWorkHandler
from agentproof.challenges.semantic_math import SemanticMathHandler
from agentproof.exceptions import UnknownChallengeTypeError


class ChallengeRegistry:
    """In-memory registry for built-in challenge handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ChallengeHandler] = {
            "proof_of_work": ProofOfWorkHandler(),
            "semantic_math_lock": SemanticMathHandler(),
        }

    def get_handler(self, challenge_type: str) -> ChallengeHandler:
        try:
            return self._handlers[challenge_type]
        except KeyError as exc:
            raise UnknownChallengeTypeError(
                f"unsupported challenge type: {challenge_type}"
            ) from exc


registry = ChallengeRegistry()
