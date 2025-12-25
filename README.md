# Electron Dynamics Simulator

Portfolio-grade, interview-ready simulator for 2D classical electron motion using the Lorentz force and a hand-rolled Runge–Kutta 4 integrator.

## Architecture
- `src/physics`: vector math utilities, constants, Lorentz force, and RK4 integrator.
- `src/simulation`: simulation engine that orchestrates time stepping and sampling.
- `src/ui`: CLI entry point for running scenarios and exporting trajectories.

## Running the simulator
Python 3.11+ recommended.

```bash
python -m src.ui.cli --dt 1e-11 --duration 2e-7 --ex 0 --ey 1e5 --bz 0.1 --v0x 1e5 --v0y 0
```

Use `--export trajectory.csv` to write samples with columns `time_s,x_m,y_m,vx_m_per_s,vy_m_per_s`.

## Design choices
- **Manual RK4**: explicit stages for transparency during review.
- **Pluggable fields**: electric and magnetic fields are callables of `(time, position)` to allow spatial or temporal variation.
- **Lightweight vectors**: minimal dataclasses keep math readable without external dependencies.
- **No magic numbers**: default parameters are named constants to make physical assumptions explicit.

## Extending
- Swap `constant_*_field` in `src/ui/cli.py` with spatially varying functions.
- Add diagnostics (energy, gyrofrequency) by iterating over `SimulationResult.samples`.
- Integrate with visualization by plotting exported CSV data.
