"""Release-rate calcs — pipeline layer 4 (calculations).

Pure functions: substance + operating conditions in, kg/s out. No I/O, no
side effects, no globals — keeps the calc layer trivially testable and
re-runnable.

Two physics paths so far:
  - Sonic gas through a sharp-edged orifice (IEC 60079-10-1 Annex B form)
  - Pool evaporation (Mackay-Matsugu simplified)

Both are simplifications appropriate for a teaching demo. They are NOT a
substitute for a competent engineer's full classification or for tools like
DNV Phast on complex consequence modelling.
"""

from __future__ import annotations

import math

from .substances import Substance


R_J_PER_MOL_K = 8.314


def is_sonic_flow(*, p_internal_pa: float, p_atm_pa: float, gamma: float) -> bool:
    """Sonic (choked) flow occurs when internal pressure exceeds the critical
    pressure ratio.

        critical_ratio = ( (gamma + 1) / 2 ) ^ ( gamma / (gamma - 1) )

    For typical hydrocarbons (gamma ~1.13–1.4) the critical ratio sits in
    1.83–1.89. We compare directly rather than hardcoding 1.9.
    """
    critical_ratio = ((gamma + 1.0) / 2.0) ** (gamma / (gamma - 1.0))
    return (p_internal_pa / p_atm_pa) >= critical_ratio


def release_rate_gas_sonic(
    *,
    p_pa: float,
    T_K: float,
    hole_area_m2: float,
    cd: float,
    substance: Substance,
) -> float:
    """Sonic mass release rate of an ideal gas through a sharp-edged orifice.

        Wg = Cd · A · P · sqrt( gamma · M / (R · T) · (2/(gamma+1))^((gamma+1)/(gamma-1)) )

    Units: Wg in kg/s.
    """
    if substance.state != "gas":
        raise ValueError(
            f"{substance.name} is {substance.state!r}, not a gas — use the "
            f"appropriate liquid/two-phase calc instead."
        )

    gamma = substance.gamma
    M = substance.molecular_weight_kg_mol

    flow_factor = (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (gamma - 1.0))
    inner = gamma * M / (R_J_PER_MOL_K * T_K) * flow_factor

    return cd * hole_area_m2 * p_pa * math.sqrt(inner)


def pool_evaporation_rate(
    *,
    pool_area_m2: float,
    T_K: float,
    wind_speed_m_s: float,
    substance: Substance,
) -> float:
    """Mass evaporation rate from an open liquid pool.

    Simplified Mackay-Matsugu form:

        We = K · A_pool · Pv · M / (R · T)

    where the mass-transfer coefficient is wind-speed driven:

        K = 0.0048 · u^0.78    (low molecular-weight species, m/s)

    Units: We in kg/s.
    """
    if substance.state != "liquid":
        raise ValueError(
            f"{substance.name} is {substance.state!r}, not a liquid — use the "
            f"gas release-rate calc instead."
        )
    if substance.vapour_pressure_pa_at_25c is None:
        raise ValueError(
            f"{substance.name} has no vapour pressure data — cannot compute "
            f"pool evaporation rate."
        )

    K = 0.0048 * (wind_speed_m_s ** 0.78)
    Pv = substance.vapour_pressure_pa_at_25c
    M = substance.molecular_weight_kg_mol

    return K * pool_area_m2 * Pv * M / (R_J_PER_MOL_K * T_K)
