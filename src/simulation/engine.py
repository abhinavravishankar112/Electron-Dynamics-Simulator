"""Simulation engine advancing electrons under Lorentz force using RK4.

RK4 is used instead of Euler to curb numerical drift in rotating systems and
keep trajectories stable without requiring extremely small time steps.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from ..physics import AccelerationFn, ElectricField, Electron, MagneticField, State, Vector2, lorentz_force, rk4_step


@dataclass
class SimulationConfig:
	"""Simulation timing configuration."""

	time_step_s: float
	total_time_s: float
	record_trajectory: bool = True

	def steps(self) -> int:
		return int(self.total_time_s / self.time_step_s)


@dataclass
class SimulationResult:
	"""Holds final states and optional trajectories for all particles."""

	final_states: List[State]
	trajectories: List[List[State]]


class SimulationEngine:
	"""Advances one or more electrons through time under given fields."""

	def __init__(self, electric_field: ElectricField, magnetic_field: MagneticField):
		self._electric_field = electric_field
		self._magnetic_field = magnetic_field

	def _acceleration_fn(self, electron: Electron) -> AccelerationFn:
		"""Create an acceleration closure bound to a specific electron."""

		def accel(time_s: float, position: Vector2, velocity: Vector2) -> Vector2:
			force = lorentz_force(
				charge_c=electron.charge_c,
				velocity=velocity,
				electric_field=self._electric_field,
				magnetic_field=self._magnetic_field,
				time_s=time_s,
				position=position,
			)
			return Vector2(force.x / electron.mass_kg, force.y / electron.mass_kg)

		return accel

	def run(self, electrons: Sequence[Electron], config: SimulationConfig, start_time_s: float = 0.0) -> SimulationResult:
		if config.time_step_s <= 0:
			raise ValueError("time_step_s must be positive")
		if config.total_time_s <= 0:
			raise ValueError("total_time_s must be positive")

		# Initialize integrator state per electron.
		states: List[State] = [
			State(time_s=start_time_s, position=e.position, velocity=e.velocity) for e in electrons
		]
		trajectories: List[List[State]] = [[s] if config.record_trajectory else [] for s in states]
		acceleration_fns: List[AccelerationFn] = [self._acceleration_fn(e) for e in electrons]

		for _ in range(config.steps()):
			for idx, state in enumerate(states):
				next_state = rk4_step(state, config.time_step_s, acceleration_fns[idx])
				states[idx] = next_state
				if config.record_trajectory:
					trajectories[idx].append(next_state)

		# Propagate final integrator state back into electron objects.
		for electron, state in zip(electrons, states):
			electron.position = state.position
			electron.velocity = state.velocity

		return SimulationResult(final_states=states, trajectories=trajectories)
