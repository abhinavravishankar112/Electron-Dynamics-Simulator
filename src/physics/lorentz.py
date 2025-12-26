"""Lorentz force computation for a charged particle in 2D motion.

The force is F = q (E + v x B). We assume velocity has no z-component and
return the in-plane force components. Magnetic field keeps full 3D support so
future extensions can lift the 2D velocity constraint if needed.
"""
from __future__ import annotations

from .fields import ElectricField, MagneticField
from .vectors import Vector2, Vector3


def _cross_v2_v3(velocity: Vector2, magnetic_field: Vector3) -> Vector3:
	"""Compute v x B where v=(vx, vy, 0) and B=(Bx, By, Bz)."""
	vx, vy = velocity.x, velocity.y
	bx, by, bz = magnetic_field.x, magnetic_field.y, magnetic_field.z
	return Vector3(vy * bz, -vx * bz, vx * by - vy * bx)


def lorentz_force(
	charge_c: float,
	velocity: Vector2,
	electric_field: ElectricField,
	magnetic_field: MagneticField,
	time_s: float,
	position: Vector2,
) -> Vector2:
	"""Compute Lorentz force on a particle at a given time and position.

	Returns in-plane force (Newtons) consistent with a 2D trajectory model.
	"""
	e_vec = electric_field(time_s, position)
	b_vec = magnetic_field(time_s, position)
	vx_b = _cross_v2_v3(velocity, b_vec)

	fx = charge_c * (e_vec.x + vx_b.x)
	fy = charge_c * (e_vec.y + vx_b.y)
	return Vector2(fx, fy)
