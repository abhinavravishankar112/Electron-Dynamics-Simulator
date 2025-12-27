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
    pixel_scale_m: float = 1e7  # meters per pixel (adjusted for electron cyclotron motion)
    electron_radius_px: int = 5
    max_trail_points: int = 500


class Visualizer:
    """Renders electron positions and trajectories in real time with interactive controls."""

    def __init__(self, config: VisualizerConfig):
        self.config = config
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self.running = False
        self.paused = False
        self.trails: dict[int, List[Vector2]] = {}  # Per-electron trail by id()
        self.show_help = True
        # Adjustment factors for interactive controls
        self.e_adjust_factor = 1e4  # V/m per keypress
        self.b_adjust_factor = 0.01  # T per keypress
        self.v_adjust_factor = 1e4  # m/s per keypress

    def initialize(self) -> None:
        """Set up Pygame window and resources."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.config.window_width, self.config.window_height))
        pygame.display.set_caption("Electron Dynamics Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
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

        # Draw current position as a circle
        px, py = self._world_to_pixel(electron.position)
        if self._pixel_in_bounds(px, py):
            pygame.draw.circle(self.screen, COLOR_ELECTRON, (px, py), self.config.electron_radius_px)

    def _handle_input(self) -> dict:
        """Process keyboard input and return adjustment dict.
        
        Returns dict with keys: 'quit', 'pause_toggle', 'reset', 'help_toggle',
        'e_adjust', 'b_adjust', 'v_adjust'.
        """
        result = {
            'quit': False,
            'pause_toggle': False,
            'reset': False,
            'help_toggle': False,
            'e_adjust': (0.0, 0.0),  # (ex_delta, ey_delta)
            'b_adjust': 0.0,  # bz_delta
            'v_adjust': (0.0, 0.0),  # (vx_delta, vy_delta)
        }
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                result['quit'] = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result['quit'] = True
                elif event.key == pygame.K_SPACE:
                    result['pause_toggle'] = True
                elif event.key == pygame.K_r:
                    result['reset'] = True
                elif event.key == pygame.K_h:
                    result['help_toggle'] = True
                # E-field adjustments (arrow keys or WASD)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    result['e_adjust'] = (0.0, self.e_adjust_factor)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    result['e_adjust'] = (0.0, -self.e_adjust_factor)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    result['e_adjust'] = (-self.e_adjust_factor, 0.0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    result['e_adjust'] = (self.e_adjust_factor, 0.0)
                # B-field adjustments
                elif event.key == pygame.K_q:
                    result['b_adjust'] = self.b_adjust_factor
                elif event.key == pygame.K_e:
                    result['b_adjust'] = -self.b_adjust_factor
                # Velocity adjustments
                elif event.key == pygame.K_i:
                    result['v_adjust'] = (0.0, self.v_adjust_factor)
                elif event.key == pygame.K_k:
                    result['v_adjust'] = (0.0, -self.v_adjust_factor)
                elif event.key == pygame.K_j:
                    result['v_adjust'] = (-self.v_adjust_factor, 0.0)
                elif event.key == pygame.K_l:
                    result['v_adjust'] = (self.v_adjust_factor, 0.0)
        
        return result

    def _draw_help(self) -> None:
        """Draw on-screen help text."""
        if not self.small_font or not self.screen:
            return
        
        lines = [
            "=== CONTROLS ===",
            "SPACE: Pause/Resume",
            "R: Reset trails",
            "H: Toggle help",
            "ESC: Quit",
            "--- Electric Field ---",
            "Arrow Keys / WASD: Adjust E_x, E_y",
            "--- Magnetic Field ---",
            "Q / E: Increase/Decrease B_z",
            "--- Velocity ---",
            "I / K / J / L: Adjust V_x, V_y",
        ]
        
        y_offset = self.config.window_height - len(lines) * 16 - 10
        for i, line in enumerate(lines):
            text_surf = self.small_font.render(line, True, COLOR_TEXT)
            self.screen.blit(text_surf, (10, y_offset + i * 16))

    def render(
        self,
        electrons: List[Electron],
        time_s: float,
        e_field_v_per_m: Vector2,
        b_field_tesla_z: float,
    ) -> tuple[bool, dict]:
        """Render all electrons and return (continue_flag, input_dict).
        
        Call this every frame after updating particle positions.
        Caller should apply input adjustments to fields/velocities.
        """
        if not self.screen:
            return False, {}

        # Handle input
        input_dict = self._handle_input()
        if input_dict['quit']:
            return False, input_dict
        if input_dict['pause_toggle']:
            self.paused = not self.paused
        if input_dict['help_toggle']:
            self.show_help = not self.show_help
        if input_dict['reset']:
            self.clear_trails()

        # Clear and draw
        self.screen.fill(COLOR_BG)
        for electron in electrons:
            self._draw_electron(electron)

        # Draw status text
        status_lines = [
            f"t = {time_s:.3e} s",
            f"E = ({e_field_v_per_m.x:.2e}, {e_field_v_per_m.y:.2e}) V/m",
            f"B_z = {b_field_tesla_z:.2e} T",
        ]
        if self.paused:
            status_lines.append("[PAUSED]")
        
        for i, line in enumerate(status_lines):
            text_surf = self.font.render(line, True, COLOR_TEXT)
            self.screen.blit(text_surf, (10, 10 + i * 28))

        if self.show_help:
            self._draw_help()

        pygame.display.flip()
        self.clock.tick(self.config.fps)
        return not input_dict['quit'], input_dict

    def clear_trails(self) -> None:
        """Reset all particle trails."""
        self.trails.clear()
