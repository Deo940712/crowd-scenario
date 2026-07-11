"""make_seed scenario-label parameter: new name preferred, old name a deprecated alias.

part-015: ``scenario_label`` is the preferred (3rd, positional-friendly) parameter;
``market_scenario_label`` stays usable as a keyword-only alias that warns. The resolved
label string is identical either way, so the seed hash — and therefore every downstream
artifact — is byte-identical (locked separately by the determinism byte-compare).
"""

from __future__ import annotations

import warnings

import pytest

from crowdscenario import STOCK_TW, make_seed

_METRICS = {"discount_premium": -0.6, "yield": 8.5}


def test_new_scenario_label_keyword_works():
    seed = make_seed("0056", _METRICS, scenario_label="evt", pack=STOCK_TW)
    assert seed.market_scenario_label == "evt"  # field name unchanged (schema stability)


def test_positional_third_argument_still_works():
    # The label has always been passable as the 3rd positional argument; that must hold.
    seed = make_seed("0056", _METRICS, "evt", pack=STOCK_TW)
    assert seed.market_scenario_label == "evt"


def test_old_alias_still_works_and_warns():
    with pytest.warns(DeprecationWarning):
        seed = make_seed("0056", _METRICS, market_scenario_label="evt", pack=STOCK_TW)
    assert seed.market_scenario_label == "evt"


def test_new_name_emits_no_deprecation_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        make_seed("0056", _METRICS, scenario_label="evt", pack=STOCK_TW)


def test_both_names_conflicting_raises_type_error():
    with pytest.raises(TypeError):
        make_seed(
            "0056", _METRICS, scenario_label="a", market_scenario_label="b", pack=STOCK_TW
        )


def test_both_names_same_value_is_allowed():
    with pytest.warns(DeprecationWarning):
        seed = make_seed(
            "0056", _METRICS, scenario_label="evt", market_scenario_label="evt", pack=STOCK_TW
        )
    assert seed.market_scenario_label == "evt"


def test_missing_label_raises_type_error():
    with pytest.raises(TypeError):
        make_seed("0056", _METRICS, pack=STOCK_TW)


def test_old_and_new_paths_hash_identically():
    # Same resolved string -> same seed hash: the alias cannot perturb determinism.
    new = make_seed("0056", _METRICS, scenario_label="evt", pack=STOCK_TW)
    with pytest.warns(DeprecationWarning):
        old = make_seed("0056", _METRICS, market_scenario_label="evt", pack=STOCK_TW)
    assert new.seed_hash == old.seed_hash
    assert new.seed_id == old.seed_id
