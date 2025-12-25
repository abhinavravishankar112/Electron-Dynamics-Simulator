"""Field models for electric and magnetic effects.

Start with uniform fields but keep interfaces extensible for spatial or
temporal variation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .vectors import Vector2, Vector3


class ElectricField(ABC):
    """Interface for 2D electric field models."""

    @abstractmethod
    def field_at(self, time_s: float, position: Vector2) -> Vector2:
        """Return electric field (V/m) at a given time and position."""

    def __call__(self, time_s: float, position: Vector2) -> Vector2:
        return self.field_at(time_s, position)


class MagneticField(ABC):
    """Interface for 3D magnetic field models."""

    @abstractmethod
    def field_at(self, time_s: float, position: Vector2) -> Vector3:
        """Return magnetic field (Tesla) at a given time and position."""

    def __call__(self, time_s: float, position: Vector2) -> Vector3:
        return self.field_at(time_s, position)


@dataclass
class UniformElectricField(ElectricField):
    """Spatially and temporally uniform electric field."""

    field: Vector2

    def field_at(self, time_s: float, position: Vector2) -> Vector2:  # noqa: ARG002
        return self.field


@dataclass
class UniformMagneticField(MagneticField):
    """Spatially and temporally uniform magnetic field."""

    field: Vector3

    def field_at(self, time_s: float, position: Vector2) -> Vector3:  # noqa: ARG002
        return self.field
