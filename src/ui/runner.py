"""Main runner combining simulation and Pygame visualization."""
from __future__ import annotations

import argparse
from typing import Optional

from ..physics import (
    ELECTRON_CHARGE_COULOMBS,
    ELECTRON_MASS_KG,
    Electron,
    UniformElectricField,
    UniformMagneticField,
    Vector2,
    Vector3,
)
from ..simulation import SimulationConfig, SimulationEngine
from .visualizer import Visualizer, VisualizerConfig


def run_interactive_simulation(
    electric_field_v_per_m: Vector2,
    magnetic_field_tesla: Vector3,
    electrons: list[Electron],
    time_step_s: float = 5e-12,
    max_frame_time_s: float = 1e-6,
) -> None:
    """Run simulation and visualization in sync with interactive controls.

    Time step is fixed for physics; frame time controls visualization framerate.
    Keyboard input adjusts E, B, and electron velocities in real time.
    """
    visualizer_config = VisualizerConfig(fps=30)
    visualizer = Visualizer(visualizer_config)
    visualizer.initialize()

    # Keep field references mutable so we can adjust them interactively
    current_e_field = Vector2(electric_field_v_per_m.x, electric_field_v_per_m.y)
    current_b_field = Vector3(magnetic_field_tesla.x, magnetic_field_tesla.y, magnetic_field_tesla.z)
    # Snapshot initial conditions for reset
    initial_e_field = Vector2(electric_field_v_per_m.x, electric_field_v_per_m.y)
    initial_b_field = Vector3(magnetic_field_tesla.x, magnetic_field_tesla.y, magnetic_field_tesla.z)
    initial_positions = [Vector2(e.position.x, e.position.y) for e in electrons]
    initial_velocities = [Vector2(e.velocity.x, e.velocity.y) for e in electrons]
    
    e_field = UniformElectricField(current_e_field)
    b_field = UniformMagneticField(current_b_field)
    engine = SimulationEngine(e_field, b_field)

    current_time = 0.0
    running = True

    try:
        while running:
            # Step forward by frame time (skip if paused)
            if not visualizer.paused:
                frame_steps = max(1, int(max_frame_time_s / time_step_s))
                frame_config = SimulationConfig(
                    time_step_s=time_step_s,
                    total_time_s=frame_steps * time_step_s,
                    record_trajectory=False,
                )

                result = engine.run(electrons, frame_config, start_time_s=current_time)
                current_time = result.final_states[0].time_s if result.final_states else current_time

            # Render and get input adjustments
            running, input_dict = visualizer.render(electrons, current_time, current_e_field, current_b_field.z)

            # Reset to initial conditions
            if input_dict.get('reset'):
                current_time = 0.0
                current_e_field = Vector2(initial_e_field.x, initial_e_field.y)
                current_b_field = Vector3(initial_b_field.x, initial_b_field.y, initial_b_field.z)
                e_field.field = current_e_field
                b_field.field = current_b_field
                for i, electron in enumerate(electrons):
                    electron.position = Vector2(initial_positions[i].x, initial_positions[i].y)
                    electron.velocity = Vector2(initial_velocities[i].x, initial_velocities[i].y)
                visualizer.clear_trails()

            # Apply B-field adjustment (incremental)
            if input_dict.get('b_adjust'):
                db = input_dict['b_adjust']
                current_b_field = Vector3(current_b_field.x, current_b_field.y, current_b_field.z + db)
                b_field.field = current_b_field

            # Apply velocity adjustments
            if input_dict.get('v_adjust'):
                dvx, dvy = input_dict['v_adjust']
                for electron in electrons:
                    electron.velocity = Vector2(electron.velocity.x + dvx, electron.velocity.y + dvy)

    finally:
        visualizer.shutdown()


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Interactive electron dynamics simulator with Pygame visualization.")
    parser.add_argument("--ex", type=float, default=0.0, help="Electric field Ex (V/m)")
    parser.add_argument("--ey", type=float, default=0.0, help="Electric field Ey (V/m)")
    parser.add_argument("--bz", type=float, default=0.1, help="Magnetic field Bz (T)")
    parser.add_argument("--v0x", type=float, default=1e5, help="Initial velocity vx (m/s)")
    parser.add_argument("--v0y", type=float, default=0.0, help="Initial velocity vy (m/s)")
    parser.add_argument("--dt", type=float, default=5e-12, help="Physics time step (s)")
    parser.add_argument("--frame-dt", type=float, default=1e-6, help="Max simulation time per frame (s)")

    args = parser.parse_args(argv)

    # Single electron at origin
    electron = Electron(
        position=Vector2(0.0, 0.0),
        velocity=Vector2(args.v0x, args.v0y),
        mass_kg=ELECTRON_MASS_KG,
        charge_c=ELECTRON_CHARGE_COULOMBS,
    )

    e_field = Vector2(args.ex, args.ey)
    b_field = Vector3(0.0, 0.0, args.bz)

    run_interactive_simulation(e_field, b_field, [electron], time_step_s=args.dt, max_frame_time_s=args.frame_dt)


if __name__ == "__main__":
    main()
