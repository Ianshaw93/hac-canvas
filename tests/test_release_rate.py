"""Tests for release-rate calcs (calc-pipeline layer 4 — calculations).

Verification-style tests for the calc primitives. Validation against full
IEC Annex E worked examples lives in tests/golden/ once those fixtures land.
"""

import math

import pytest

from hac.release_rate import (
    is_sonic_flow,
    pool_evaporation_rate,
    release_rate_gas_sonic,
)
from hac.substances import get_substance


# ---------------------------------------------------------------------------
# is_sonic_flow — pressure-ratio threshold detection
# ---------------------------------------------------------------------------

def test_high_internal_pressure_is_sonic():
    # 9 barg vs atm — ratio ~9, well above critical
    assert is_sonic_flow(p_internal_pa=9e5, p_atm_pa=1e5, gamma=1.13) is True


def test_atmospheric_pressure_is_subsonic():
    assert is_sonic_flow(p_internal_pa=1.05e5, p_atm_pa=1e5, gamma=1.30) is False


def test_critical_ratio_boundary_is_sonic():
    # gamma=1.4 -> critical ratio 1.893; just above = sonic, just below = subsonic
    gamma = 1.4
    crit = ((gamma + 1) / 2) ** (gamma / (gamma - 1))
    assert is_sonic_flow(p_internal_pa=crit * 1.001, p_atm_pa=1.0, gamma=gamma) is True
    assert is_sonic_flow(p_internal_pa=crit * 0.999, p_atm_pa=1.0, gamma=gamma) is False


# ---------------------------------------------------------------------------
# release_rate_gas_sonic — sonic mass flow through orifice
# ---------------------------------------------------------------------------

def test_propane_pump_seal_matches_worked_example():
    """Worked example S2: propane at 8 barg, S1 hole, Cd=0.8 -> Wg ~5e-5 kg/s."""
    propane = get_substance("propane")
    Wg = release_rate_gas_sonic(
        p_pa=9e5,            # 8 barg + atm
        T_K=298,
        hole_area_m2=2.5e-8, # S1 ~0.025 mm^2
        cd=0.8,
        substance=propane,
    )
    # Hand-calc: 4.8e-5 kg/s. 30% tolerance for the simplified physics.
    assert Wg == pytest.approx(4.8e-5, rel=0.30)


def test_hydrogen_at_high_pressure_releases_fast():
    """Worked example S4: H2 at 50 barg, S2 hole. Should be ~1e-3 kg/s order."""
    hydrogen = get_substance("hydrogen")
    Wg = release_rate_gas_sonic(
        p_pa=51e5,           # 50 barg + atm
        T_K=298,
        hole_area_m2=2.5e-7, # S2 ~0.25 mm^2
        cd=0.8,
        substance=hydrogen,
    )
    assert 1e-4 < Wg < 1e-2, f"H2 release rate {Wg} out of plausible range"


def test_release_rate_scales_linearly_with_pressure():
    propane = get_substance("propane")
    base = release_rate_gas_sonic(p_pa=5e5, T_K=298, hole_area_m2=1e-8, cd=0.8, substance=propane)
    doubled = release_rate_gas_sonic(p_pa=10e5, T_K=298, hole_area_m2=1e-8, cd=0.8, substance=propane)
    assert doubled == pytest.approx(2 * base, rel=0.01)


def test_release_rate_scales_linearly_with_hole_area():
    methane = get_substance("methane")
    base = release_rate_gas_sonic(p_pa=5e5, T_K=298, hole_area_m2=1e-8, cd=0.8, substance=methane)
    doubled = release_rate_gas_sonic(p_pa=5e5, T_K=298, hole_area_m2=2e-8, cd=0.8, substance=methane)
    assert doubled == pytest.approx(2 * base, rel=0.01)


def test_release_rate_is_positive():
    methane = get_substance("methane")
    Wg = release_rate_gas_sonic(p_pa=2e5, T_K=298, hole_area_m2=1e-8, cd=0.8, substance=methane)
    assert Wg > 0


def test_liquid_substance_in_gas_calc_raises():
    methanol = get_substance("methanol")
    with pytest.raises(ValueError, match="not a gas"):
        release_rate_gas_sonic(p_pa=5e5, T_K=298, hole_area_m2=1e-8, cd=0.8, substance=methanol)


# ---------------------------------------------------------------------------
# pool_evaporation_rate — Mackay-Matsugu simplified
# ---------------------------------------------------------------------------

def test_methanol_pool_evaporation_at_1ms_wind():
    """Worked example S3: 0.1 m^2 pool, 1 m/s wind -> ~1e-4 kg/s order."""
    methanol = get_substance("methanol")
    We = pool_evaporation_rate(
        pool_area_m2=0.1,
        T_K=298,
        wind_speed_m_s=1.0,
        substance=methanol,
    )
    assert 1e-5 < We < 1e-3, f"Methanol pool evap rate {We} out of plausible range"


def test_pool_evaporation_increases_with_wind():
    methanol = get_substance("methanol")
    calm = pool_evaporation_rate(pool_area_m2=0.1, T_K=298, wind_speed_m_s=0.5, substance=methanol)
    breezy = pool_evaporation_rate(pool_area_m2=0.1, T_K=298, wind_speed_m_s=5.0, substance=methanol)
    assert breezy > calm


def test_gas_substance_in_pool_calc_raises():
    methane = get_substance("methane")
    with pytest.raises(ValueError, match="not a liquid"):
        pool_evaporation_rate(pool_area_m2=0.1, T_K=298, wind_speed_m_s=1.0, substance=methane)
