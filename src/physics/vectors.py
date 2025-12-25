"""Vector math utilities for 2D algebra.

Operations stay minimal and dependency-free so reviewers can follow the math
directly without hidden helpers.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Iterable


@dataclass(frozen=True)
class Vector2:
	x: float
	y: float

	def __add__(self, other: "Vector2") -> "Vector2":
		return Vector2(self.x + other.x, self.y + other.y)

	def __sub__(self, other: "Vector2") -> "Vector2":
		return Vector2(self.x - other.x, self.y - other.y)

	def __mul__(self, scalar: float) -> "Vector2":
		return Vector2(self.x * scalar, self.y * scalar)

	__rmul__ = __mul__

	def magnitude(self) -> float:
		return hypot(self.x, self.y)

	def to_tuple(self) -> tuple[float, float]:
		return (self.x, self.y)

	@staticmethod
	def from_iterable(values: Iterable[float]) -> "Vector2":
		x, y = values
		return Vector2(float(x), float(y))

	@staticmethod
	def zero() -> "Vector2":
		return Vector2(0.0, 0.0)
