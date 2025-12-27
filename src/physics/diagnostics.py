"""Energy utilities and validations for electron dynamics.

Design notes:
- Magnetic fields do no work: with E=0, kinetic energy should remain constant.
- Functions are stateless and reusable across simulation setups.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from .electron import Electron
from .integrators import State
from .vectors import Vector2


def kinetic_energy(mass_kg: float, velocity: Vector2) -> float:
    """Return kinetic energy (Joules): 0.5 * m * |v|^2.

    Keeping this standalone avoids coupling to specific particle classes.
    """
    vx, vy = velocity.x, velocity.y
    return 0.5 * mass_kg * (vx * vx + vy * vy)


@dataclass
class EnergyConservationCheck:
    """Summary of per-electron energy stability when E=0 (magnetic-only)."""

    passed: bool
    max_relative_deviation: List[float]
    max_absolute_deviation: List[float]


def verify_magnetic_energy_conservation(
    electrons: Sequence[Electron],
    trajectories: Sequence[Sequence[State]],
    rel_tol: float = 1e-3,
    abs_tol: float = 1e-12,
) -> EnergyConservationCheck:
    """Verify kinetic energy is conserved for each electron when E=0.

    Assumptions:
    - Only magnetic field is present (E=0). Magnetic fields do no work.
    - Trajectories align index-wise with the provided electrons.

    Returns an `EnergyConservationCheck` with aggregate deviation metrics and
    a pass/fail flag using both absolute and relative tolerances.
    """
    max_rel: List[float] = []
    max_abs: List[float] = []

    for e, samples in zip(electrons, trajectories):
        if not samples:
            # No samples: trivially passes with zero deviation.
            max_rel.append(0.0)
            max_abs.append(0.0)
            continue

        e0 = kinetic_energy(e.mass_kg, samples[0].velocity)
        rel_deviation = 0.0
        abs_deviation = 0.0
        denom = e0 if e0 != 0.0 else 1.0  # avoid divide-by-zero in relative error

        for s in samples:
            ek = kinetic_energy(e.mass_kg, s.velocity)
            d = abs(ek - e0)
            abs_deviation = max(abs_deviation, d)
            rel_deviation = max(rel_deviation, d / denom)

        max_rel.append(rel_deviation)
        max_abs.append(abs_deviation)

    passed = all((r <= rel_tol) or (a <= abs_tol) for r, a in zip(max_rel, max_abs))
    return EnergyConservationCheck(passed=passed, max_relative_deviation=max_rel, max_absolute_deviation=max_abs)
