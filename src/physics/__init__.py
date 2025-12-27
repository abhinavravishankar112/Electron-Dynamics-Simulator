"""Namespace for physics utilities such as vectors, constants, and forces."""

from .constants import ELECTRON_CHARGE_COULOMBS, ELECTRON_MASS_KG
from .vectors import Vector2, Vector3
from .fields import ElectricField, MagneticField, UniformElectricField, UniformMagneticField
from .electron import Electron
from .lorentz import lorentz_force
from .integrators import State, AccelerationFn, rk4_step
from .diagnostics import kinetic_energy, verify_magnetic_energy_conservation, EnergyConservationCheck

__all__ = [
    "ELECTRON_CHARGE_COULOMBS",
    "ELECTRON_MASS_KG",
	"ElectricField",
	"MagneticField",
	"UniformElectricField",
	"UniformMagneticField",
	"Electron",
	"lorentz_force",
	"State",
	"AccelerationFn",
	"rk4_step",
	"kinetic_energy",
	"verify_magnetic_energy_conservation",
	"EnergyConservationCheck",
]
