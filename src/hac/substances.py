"""Substance database — pipeline layer 3 (methods/parameters).

Substance properties are reference data, not method code. Loaded once from
the JSON DB sitting at the repo root and cached in-process. Add new substances
by editing `substances.json`; do not hardcode them here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


_DB_PATH = Path(__file__).parent.parent.parent / "substances.json"


@dataclass(frozen=True)
class Substance:
    """A flammable substance and the properties that drive HAC calcs.

    Field units are SI throughout — kg, m, s, Pa, K, mol — to keep formulas
    dimensionally sane. Vapour pressure is only meaningful for liquids.
    """

    name: str
    formula: str
    state: str  # "gas" | "liquid"
    molecular_weight_kg_mol: float
    lfl_vol_fraction: float
    gas_density_at_ntp_kg_m3: float
    gamma: float  # ratio of specific heats
    equipment_group: str  # IIA | IIB | IIC
    temperature_class: str  # T1..T6
    vapour_pressure_pa_at_25c: Optional[float] = None  # liquids only


_cache: Optional[dict[str, Substance]] = None


def _load() -> dict[str, Substance]:
    global _cache
    if _cache is None:
        rows = json.loads(_DB_PATH.read_text(encoding="utf-8"))
        _cache = {row["name"]: Substance(**row) for row in rows}
    return _cache


def list_substances() -> list[str]:
    return list(_load().keys())


def get_substance(name: str) -> Substance:
    db = _load()
    if name not in db:
        raise KeyError(f"Unknown substance: {name!r}. Known: {sorted(db.keys())}")
    return db[name]
