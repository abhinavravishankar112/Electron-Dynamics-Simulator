"""Electron particle state representation without embedded physics."""
from __future__ import annotations

from dataclasses import dataclass

from .vectors import Vector2


@dataclass
class Electron:
    """Stores electron kinematics; physics is applied by external integrators."""

    position: Vector2
    velocity: Vector2
    mass_kg: float
    charge_c: float

    def set_position(self, position: Vector2) -> None:
        """Assign an absolute position for the particle."""
        self.position = position

    def set_velocity(self, velocity: Vector2) -> None:
        """Assign an absolute velocity for the particle."""
        self.velocity = velocity

    def translate(self, delta: Vector2) -> None:
        """Shift position by a caller-provided displacement (no forces applied)."""
        self.position = self.position + delta

    def adjust_velocity(self, delta: Vector2) -> None:
        """Increment velocity by a caller-provided change (physics applied elsewhere)."""
        self.velocity = self.velocity + delta
