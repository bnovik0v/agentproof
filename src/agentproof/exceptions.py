"""Library exceptions."""


class AgentProofError(Exception):
    """Base exception for library-specific errors."""


class UnknownChallengeTypeError(AgentProofError):
    """Raised when the caller requests an unsupported challenge type."""


class InvalidChallengeError(AgentProofError):
    """Raised when challenge data is malformed."""


class InvalidResponseError(AgentProofError):
    """Raised when response data is malformed."""


class SolverUnavailableError(AgentProofError):
    """Raised when a challenge family intentionally has no built-in solver."""
