"""Pygame-based real-time visualization of electron trajectories.

Render electrons as circles with optional trails showing historical positions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

from ..physics import Electron, Vector2


Color = Tuple[int, int, int]

# Standard colors for electron paths and UI elements
COLOR_BG = (25, 25, 35)  # Dark blue-gray background
COLOR_ELECTRON = (0, 200, 255)  # Bright cyan for current position
COLOR_TRAIL = (100, 150, 200)  # Softer blue for trails
COLOR_TEXT = (200, 200, 200)  # Light gray for text


@dataclass
class VisualizerConfig:
    """Visualization parameters."""

    window_width: int = 800
    window_height: int = 600
    fps: int = 30
    pixel_scale_m: float = 1e8  # meters per pixel
    electron_radius_px: int = 5
    max_trail_points: int = 500


class Visualizer:
    """Renders electron positions and trajectories in real time."""

    def __init__(self, config: VisualizerConfig):
        self.config = config
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.font: Optional[pygame.font.Font] = None
        self.running = False
        self.trails: dict[int, List[Vector2]] = {}  # Per-electron trail by id()

    def initialize(self) -> None:
        """Set up Pygame window and resources."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.config.window_width, self.config.window_height))
        pygame.display.set_caption("Electron Dynamics Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.running = True

    def shutdown(self) -> None:
        """Tear down Pygame."""
        if self.running:
            pygame.quit()
            self.running = False

    def _world_to_pixel(self, world_pos: Vector2) -> Tuple[int, int]:
        """Convert world meters to pixel coordinates (center at window center)."""
        cx, cy = self.config.window_width / 2, self.config.window_height / 2
        px = cx + world_pos.x * self.config.pixel_scale_m
        py = cy - world_pos.y * self.config.pixel_scale_m  # y-flip for screen coords
        return int(px), int(py)

    def _pixel_in_bounds(self, px: int, py: int) -> bool:
        """Check if pixel coordinates are visible."""
        return 0 <= px < self.config.window_width and 0 <= py < self.config.window_height

    def _draw_trail(self, electron_id: int, points: List[Vector2]) -> None:
        """Draw a line trail for an electron; cap old points if needed."""
        if len(points) < 2 or not self.screen:
            return
        
        # Cull oldest points if trail exceeds max length
        if len(points) > self.config.max_trail_points:
            del points[: len(points) - self.config.max_trail_points]

        # Draw segments between consecutive points
        for i in range(len(points) - 1):
            px0, py0 = self._world_to_pixel(points[i])
            px1, py1 = self._world_to_pixel(points[i + 1])
            if self._pixel_in_bounds(px0, py0) or self._pixel_in_bounds(px1, py1):
                pygame.draw.line(self.screen, COLOR_TRAIL, (px0, py0), (px1, py1), 1)

    def _draw_electron(self, electron: Electron) -> None:
        """Draw a single electron and its trail."""
        if not self.screen:
            return

        eid = id(electron)
        if eid not in self.trails:
            self.trails[eid] = []
        self.trails[eid].append(electron.position)

        # Draw trail
        self._draw_trail(eid, self.trails[eid])

        # Draw current position as a circle
        px, py = self._world_to_pixel(electron.position)
        if self._pixel_in_bounds(px, py):
            pygame.draw.circle(self.screen, COLOR_ELECTRON, (px, py), self.config.electron_radius_px)

    def render(self, electrons: List[Electron], time_s: float) -> bool:
        """Render all electrons and return False if window closed.
        
        Call this every frame after updating particle positions.
        """
        if not self.screen:
            return False

        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        # Clear and draw
        self.screen.fill(COLOR_BG)
        for electron in electrons:
            self._draw_electron(electron)

        # Draw status text
        time_text = self.font.render(f"t = {time_s:.3e} s", True, COLOR_TEXT)
        self.screen.blit(time_text, (10, 10))

        pygame.display.flip()
        self.clock.tick(self.config.fps)
        return True

    def clear_trails(self) -> None:
        """Reset all particle trails."""
        self.trails.clear()
