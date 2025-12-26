"""Runge–Kutta 4 integrator for second-order motion.

We track position and velocity; acceleration is supplied by a caller so the
integrator stays reusable across force models.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .vectors import Vector2


@dataclass
class State:
	"""System state at a given time."""

	time_s: float
	position: Vector2
	velocity: Vector2


# Acceleration provider: a(t, x, v) -> Vector2 (m/s^2)
AccelerationFn = Callable[[float, Vector2, Vector2], Vector2]


def rk4_step(state: State, dt_s: float, acceleration_fn: AccelerationFn) -> State:
	"""Advance state by one RK4 step.

	RK4 offers better stability and accuracy than simple Euler for the same
	step size, which limits error growth in stiff or rotating systems.
	"""

	def deriv(time_s: float, position: Vector2, velocity: Vector2) -> tuple[Vector2, Vector2]:
		return velocity, acceleration_fn(time_s, position, velocity)

	# Stage 1
	k1_pos, k1_vel = deriv(state.time_s, state.position, state.velocity)

	# Stage 2
	mid_pos_1 = state.position + k1_pos * (0.5 * dt_s)
	mid_vel_1 = state.velocity + k1_vel * (0.5 * dt_s)
	k2_pos, k2_vel = deriv(state.time_s + 0.5 * dt_s, mid_pos_1, mid_vel_1)

	# Stage 3
	mid_pos_2 = state.position + k2_pos * (0.5 * dt_s)
	mid_vel_2 = state.velocity + k2_vel * (0.5 * dt_s)
	k3_pos, k3_vel = deriv(state.time_s + 0.5 * dt_s, mid_pos_2, mid_vel_2)

	# Stage 4
	end_pos = state.position + k3_pos * dt_s
	end_vel = state.velocity + k3_vel * dt_s
	k4_pos, k4_vel = deriv(state.time_s + dt_s, end_pos, end_vel)

	new_position = state.position + (dt_s / 6.0) * (
		k1_pos + 2.0 * k2_pos + 2.0 * k3_pos + k4_pos
	)
	new_velocity = state.velocity + (dt_s / 6.0) * (
		k1_vel + 2.0 * k2_vel + 2.0 * k3_vel + k4_vel
	)

	return State(
		time_s=state.time_s + dt_s,
		position=new_position,
		velocity=new_velocity,
	)
