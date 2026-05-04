"""Tests for the substance database (calc-pipeline layer 3 — methods/parameters)."""

import pytest

from hac.substances import Substance, get_substance, list_substances


def test_list_includes_all_four_demo_substances():
    names = set(list_substances())
    assert {"methane", "propane", "methanol", "hydrogen"} <= names


def test_methane_properties():
    s = get_substance("methane")
    assert isinstance(s, Substance)
    assert s.formula == "CH4"
    assert s.state == "gas"
    assert s.molecular_weight_kg_mol == pytest.approx(0.01604, rel=0.01)
    assert s.lfl_vol_fraction == pytest.approx(0.05, rel=0.01)
    assert s.gas_density_at_ntp_kg_m3 == pytest.approx(0.668, rel=0.05)
    assert s.gamma == pytest.approx(1.30, rel=0.05)
    assert s.equipment_group == "IIA"
    assert s.temperature_class == "T1"


def test_propane_is_heaviest_gas_in_set():
    propane = get_substance("propane")
    methane = get_substance("methane")
    hydrogen = get_substance("hydrogen")
    assert propane.gas_density_at_ntp_kg_m3 > methane.gas_density_at_ntp_kg_m3
    assert methane.gas_density_at_ntp_kg_m3 > hydrogen.gas_density_at_ntp_kg_m3


def test_methanol_is_liquid_with_vapour_pressure():
    s = get_substance("methanol")
    assert s.state == "liquid"
    assert s.vapour_pressure_pa_at_25c == pytest.approx(16900, rel=0.1)


def test_hydrogen_is_iic_t1_hardest_substance():
    s = get_substance("hydrogen")
    assert s.equipment_group == "IIC"
    assert s.temperature_class == "T1"


def test_gas_substances_have_no_vapour_pressure_field_or_none():
    for name in ("methane", "propane", "hydrogen"):
        s = get_substance(name)
        assert s.vapour_pressure_pa_at_25c is None


def test_unknown_substance_raises_keyerror():
    with pytest.raises(KeyError, match="xenon"):
        get_substance("xenon")
