import hashlib

from qaforge.models import Split, SplitConfig


def assign_split(lineage_id: str, config: SplitConfig) -> Split:
    """FR-003: deterministically assign a lineage before descendant generation."""
    digest = hashlib.sha256(f"{config.salt}:{lineage_id}".encode()).digest()
    point = int.from_bytes(digest[:8], "big") / float(2**64)
    if point < config.train:
        return Split.TRAIN
    if point < config.train + config.validation:
        return Split.VALIDATION
    return Split.TEST
