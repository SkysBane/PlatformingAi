# PlatformingAI

A Pygame platformer with nine levels and a NumPy neural network that learns to play through genetic evolution. Play the levels yourself, train a population, or replay a saved model.

## Setup

Use Python 3.12 or 3.13. Clone the repository and create a virtual environment.

```bash
git clone https://github.com/SkysBane/PlatformingAi.git
cd PlatformingAi
python -m venv .venv
```

Activate the environment in PowerShell.

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate it with the shell script.

```bash
source .venv/bin/activate
```

Then install the dependencies and list the available commands.

```bash
python -m pip install -r requirements.txt
python cli.py --help
```

Use `python cli.py <command> --help` for the options for an individual command. The old launchers still work. `gameStart.py` forwards to `play`, and `nnStart.py` forwards to `train`.

## Play

```bash
python cli.py play
python cli.py play --level 7 --repeat --fps 120 --rays
```

| Control | Action |
| --- | --- |
| Left and Right arrows | Move |
| Up arrow | Jump. Hold to jump again when you land |
| R | Restart the current level and its timer |
| Q or close the window | Exit |

Levels are numbered **0–8**. The game advances when you reach the flag and loops back to level 0 after level 8. Use `--repeat` to stay on one level and `--rays` to see the sensor rays. Finishing times are saved in `records.local.txt` for this checkout. The original timing records are in [legacy/records.txt](legacy/records.txt).

## Train a population

Start with a small run to check your setup.

```bash
python cli.py train --level 0 --population 8 --generations 5 --seed 42
```

This command trains a larger population on level 7 and stops if any model reaches the flag.

```bash
python cli.py train --level 7 --population 100 --generations 500 --headless --stop-on-win --output runs/level7
```

| Option | Default | What it controls |
| --- | --- | --- |
| `--level` | `7` | Level to train on. A new-format seed checkpoint supplies its level when omitted |
| `--population` | `25` | Models evaluated in each generation. Minimum is two |
| `--generations` | `50` | Generations to evaluate in this invocation |
| `--max-steps` | `1800` | Simulation steps per episode. At 60 steps per second, 1800 steps is 30 seconds |
| `--hidden-layers` / `--hidden-size` | `1` / `21` | Network depth and hidden width. Use `--hidden-layers 0` for a direct input-to-output network |
| `--seed` | Random | Seed for initialization, parent selection, crossover, and mutation |
| `--output` | A new folder in `runs/` | Directory for checkpoints. An explicit directory must be new |
| `--headless` / `--show` | Headless | Run without a window, or see the population at interactive speed |
| `--fast`| Not Fast | Use with `--show` to allow the simulation to run as fast as possible while still rendering |
| `--fps` | `60` | Rendering cap when using `--show`. Use `0` for uncapped rendering |
| `--stop-on-win` | Off | Stop after saving the first generation with a finisher |

Each player observes eight rays, their danger flags, horizontal and vertical velocity, direction to the flag, and whether it is grounded. The network's three outputs control left, right, and jump. Fitness rewards farthest horizontal progress. Reaching the flag adds a completion bonus and rewards fewer steps. The next generation keeps up to three top models and fills the remaining slots by crossing and mutating models from the ranked parent pool.

### Checkpoints and resuming

Training prints the run directory on startup and saves automatically.

| File | When it is written | Use it to |
| --- | --- | --- |
| `latest.pkl` | At startup and after every completed generation | Resume from the latest saved population |
| `best.pkl` | After the first completed generation and each improvement | Watch the best model or resume from the generation where it improved |

Both files store the population for the next generation, run settings, generation history, random generator state, and best evaluated model if available. Each save replaces its checkpoint atomically. If you press Ctrl+C or close a visible training run, resume from `latest.pkl` to start again at the last saved generation boundary.

```bash
python cli.py resume --checkpoint runs/level7/latest.pkl --generations 100 --output runs/level7-continued
```

Resuming keeps the checkpoint's level, architecture, population, and episode length. `--generations` adds that many generations to the saved run. The continuation writes to a new folder so the source checkpoint stays available. For reproducible comparisons, use the same Python and NumPy versions.

### Watch a model

```bash
python cli.py watch --checkpoint runs/level7/best.pkl --fps 60
python cli.py watch --checkpoint runs/level7/best.pkl --level 6 --once --rays
```

Replay uses the saved level and episode length unless you pass `--level` or `--max-steps`. It loops until you press Q or close the window. `--once` exits after the first episode and prints its result.

### Use an older model

The existing files in [nn_models/](nn_models/) work with `watch` and can seed a fresh run. Pass the level explicitly when watching an old file because it stores scored models without level metadata. Keep quotes around paths with spaces.

```bash
python cli.py watch --checkpoint "nn_models/21 21 3/level7.pkl" --level 7
python cli.py train --init-from "nn_models/21 21 3/level7.pkl" --level 7 --population 25
```

`--init-from` keeps the source model's architecture and starts a new population with a copy of the best saved model and mutated copies. Use it when you want to change the level or population, or when an old file lacks the state needed for an exact resume. Load pickle files only from sources you trust. Python can execute code while loading them.

## Timing and FPS

Physics, collision checks, jump timing, model decisions, and episode timers advance at **60 simulation steps per second**. The HUD's **time** comes from the number of simulation steps, and **FPS** measures rendered frames per wall-clock second. At 30 FPS, each render usually follows two simulation steps. At 120 FPS, some frames render between steps. Headless training runs as fast as the computer can simulate.

If rendering stalls, the interactive loop limits catch-up to 250 ms per frame to keep the window responsive. The simulation timer can fall behind wall time during a long stall. Training still evaluates the same number of steps per episode at any render cap.

## Repository layout

| Path | Contents |
| --- | --- |
| `cli.py` | Play, train, resume, and watch commands |
| `main.py`, `player.py` | Gameplay, simulation steps, input, and rendering |
| `levels.py` | Geometry, hazards, and flag positions |
| `timing.py` | Fixed-step scheduling, render pacing, and FPS measurement |
| `NN.py`, `training.py` | NumPy networks, genetic evolution, and checkpoint storage |
| `nn_models/` | Original genetic model files |
| `legacy/` | Archived Q-learning, PPO, search, and rule-based experiments |
| `tests/` | Timing, replay, and checkpoint regression checks |

The archived experiments are reference code. Some depend on older game APIs or optional libraries such as PyTorch. See [legacy/README.md](legacy/README.md) for the baseline commit and file map.

## Run the checks

```bash
python -m unittest discover -s tests -v
```

The suite checks fixed-step movement at several render rates, timeout and win handling, headless model replay, and whether resuming produces the same population as uninterrupted training.
