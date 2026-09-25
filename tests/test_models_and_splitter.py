from pathlib import Path

import pytest
from pydantic import ValidationError

from qaforge.errors import ConfigurationError
from qaforge.io import ensure_within
from qaforge.models import GenerationConfig, ReviewConfig, SplitConfig
from qaforge.splitter import assign_split


def test_fr003_lineage_split_is_deterministic() -> None:
    config = SplitConfig(train=0.8, validation=0.1, test=0.1, salt="stable-salt")
    first = assign_split("family-001", config)
    assert assign_split("family-001", config) is first
    assert len({assign_split(f"family-{index}", config) for index in range(100)}) == 3


def test_split_ratios_must_sum_to_one() -> None:
    with pytest.raises(ValidationError, match=r"sum to 1\.0"):
        SplitConfig(train=0.8, validation=0.1, test=0.2, salt="stable-salt")


def test_nfr006_path_must_remain_inside_workspace(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="escapes workspace"):
        ensure_within(tmp_path, tmp_path / ".." / "outside")


def test_fr004_candidate_count_is_bounded_from_three_to_ten() -> None:
    assert GenerationConfig(provider_id="fixture", candidates_per_seed=3)
    assert GenerationConfig(provider_id="fixture", candidates_per_seed=10)
    with pytest.raises(ValidationError):
        GenerationConfig(provider_id="fixture", candidates_per_seed=2)
    with pytest.raises(ValidationError):
        GenerationConfig(provider_id="fixture", candidates_per_seed=11)


def test_fr010_review_cannot_be_disabled() -> None:
    with pytest.raises(ValidationError):
        ReviewConfig(required=False)  # type: ignore[arg-type]
