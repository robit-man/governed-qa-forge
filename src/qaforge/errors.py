class ForgeError(RuntimeError):
    """Base error for expected policy and workflow failures."""


class ConfigurationError(ForgeError):
    """Configuration or registry data is invalid."""


class AuthorizationError(ForgeError):
    """A source or teacher is not authorized for the requested operation."""


class GateError(ForgeError):
    """A mandatory quality or release gate failed."""


class ImmutableArtifactError(ForgeError):
    """An immutable run or release path already exists."""
