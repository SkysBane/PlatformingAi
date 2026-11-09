"""Genetic training and checkpoints for the NumPy platformer agents."""

from dataclasses import dataclass
from pathlib import Path
import os
import pickle
import tempfile

import numpy as np

from main import Main
from NN import NeuralNetwork

CHECKPOINT_VERSION = 1


@dataclass(frozen=True)
class TrainingConfig:
    level: int
    population: int
    max_steps: int
    hidden_layers: int
    hidden_size: int


def make_run_directory(path):
    if path is None:
        root = Path(__file__).with_name("runs")
        root.mkdir(exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="run-", dir=root))
    path.mkdir(parents=True)
    return path


def save_checkpoint(path, state):
    """Replace a checkpoint only after its complete payload has been written."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            pickle.dump(state, handle, protocol=pickle.HIGHEST_PROTOCOL)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_checkpoint(path):
    with path.open("rb") as handle:
        data = pickle.load(handle)
    if isinstance(data, dict) and data.get("version") != CHECKPOINT_VERSION:
        raise ValueError("Unsupported training checkpoint version")
    return data


def best_model(data):
    if isinstance(data, dict):
        result = data["best"]
    elif isinstance(data, list) and data:
        # Original nnStart.py saved a list of (network, fitness, completed).
        result = max(data, key=lambda row: row[1])
    else:
        result = None
    if result is None:
        raise ValueError("Checkpoint contains no evaluated model")
    brain, fitness, completed = result
    if not isinstance(brain, NeuralNetwork) or (brain.inputSize, brain.outputSize) != (21, 3):
        raise ValueError("Expected a platformer model with 21 inputs and 3 outputs")
    return brain, fitness, completed


def new_run(config, seed, initial_model=None):
    generator = np.random.default_rng(seed)
    if initial_model is None:
        population = [
            NeuralNetwork(21, 3, config.hidden_layers, config.hidden_size, generator=generator)
            for _ in range(config.population)
        ]
    else:
        population = [initial_model.clone()]
        population.extend(
            initial_model.clone().mutate(0.1, 0.1, generator=generator)
            for _ in range(config.population - 1)
        )
    return {
        "version": CHECKPOINT_VERSION,
        "config": vars(config),
        "generation": 0,
        "population": population,
        "rng_state": generator.bit_generator.state,
        "best": None,
        "history": [],
    }


def next_generation(ranked, generator):
    size = len(ranked)
    elite_count = min(3, max(1, size // 4))
    parent_count = max(2, (size + 4) // 5)
    parents = [row[0] for row in ranked[:parent_count]]
    population = [row[0].clone() for row in ranked[:elite_count]]

    while len(population) < size:
        first, second = generator.choice(len(parents), size=2, replace=False)
        child = parents[first].createOffspring(parents[second], generator=generator)
        population.append(child.mutate(0.1, 0.1, generator=generator))
    return population


def train(state, generations, directory, show=False, fast=False, fps=60, stop_on_win=False):
    config = TrainingConfig(**state["config"])
    generator = np.random.default_rng()
    generator.bit_generator.state = state["rng_state"]
    latest = directory / "latest.pkl"
    best = directory / "best.pkl"

    checkpoint_arg = "'" + str(latest.resolve()).replace("'", "''") + "'"
    resume_command = f"python cli.py resume --checkpoint {checkpoint_arg}"
    if show:
        resume_command += f" --show --fps {fps}"
        if fast:
            resume_command += " --fast"
    if stop_on_win:
        resume_command += " --stop-on-win"
    best_arg = "'" + str(best.resolve()).replace("'", "''") + "'"
    watch_command = f"python cli.py watch --checkpoint {best_arg} --fps 60"

    save_checkpoint(latest, state)
    if state["best"] is not None:
        save_checkpoint(best, state)
    print(f"Checkpoints: {directory.resolve()}", flush=True)

    game = Main(config.level, display=show, controlledByNN=True, populationSize=0)
    try:
        for _ in range(generations):
            game.resetAndRestartNNBrains(state["population"])
            results = game.runNN(maxFrames=config.max_steps, fps=fps, fast=fast)
            if results is False:
                print(f"Window closed. Resume from latest.pkl by running:\n{resume_command}")
                return 0

            ranked = sorted(results, key=lambda row: row[1], reverse=True)
            winner = ranked[0]
            completed = sum(row[2] for row in ranked)
            improved = state["best"] is None or winner[1] > state["best"][1]
            generation = state["generation"] + 1
            population = next_generation(ranked, generator)
            state = {
                **state,
                "generation": generation,
                "population": population,
                "rng_state": generator.bit_generator.state,
                "best": winner if improved else state["best"],
                "history": [*state["history"], (generation, winner[1], completed)],
            }
            save_checkpoint(latest, state)
            if improved:
                save_checkpoint(best, state)
            print(
                f"Generation {generation} | best fitness {winner[1]:.2f} | "
                f"completed {completed}/{len(ranked)}",
                flush=True,
            )
            if stop_on_win and completed:
                break

        print(f"Training complete. Watch best.pkl by running:\n{watch_command}")
        
    except KeyboardInterrupt:
        print(f"\nTraining stopped. Resume from latest.pkl by running:\n{resume_command}")
        return 130
    finally:
        game.quitPygame()
    return 0
