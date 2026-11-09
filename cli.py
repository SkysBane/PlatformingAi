"""Play the platformer, train a genetic population, or replay a model."""

import argparse
from pathlib import Path
import pickle

import pygame

from levels import LEVEL_COUNT
from main import Main
from training import (
    TrainingConfig,
    best_model,
    load_checkpoint,
    make_run_directory,
    new_run,
    train,
)


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def add_level(command, default=None):
    command.add_argument("--level", type=int, choices=range(LEVEL_COUNT), default=default)


def add_fps(command):
    command.add_argument("--fps", type=nonnegative, default=60, help="render cap (0 for uncapped)")


def add_training_options(command):
    command.add_argument("--generations", type=positive, default=50)
    command.add_argument("--output", type=Path, help="new directory for checkpoints")
    display = command.add_mutually_exclusive_group()
    display.add_argument("--show", dest="show", action="store_true", help="render in real time")
    command.add_argument("--fast", action="store_true", help="run simulation as fast as possible with --show")
    display.add_argument("--headless", dest="show", action="store_false", help="train without a window (default)")
    command.set_defaults(show=False)
    command.add_argument("--stop-on-win", action="store_true", help="stop after a generation reaches the flag")
    add_fps(command)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    play = commands.add_parser("play", help="play using the arrow keys")
    add_level(play, default=0)
    add_fps(play)
    play.add_argument("--repeat", action="store_true", help="stay on the selected level")
    play.add_argument("--rays", action="store_true", help="show the player raycasts")

    fresh = commands.add_parser("train", help="start a genetic training run")
    add_training_options(fresh)
    add_level(fresh)
    fresh.add_argument("--population", type=positive, default=25)
    fresh.add_argument("--max-steps", type=positive, default=1800)
    fresh.add_argument("--hidden-layers", type=nonnegative)
    fresh.add_argument("--hidden-size", type=positive)
    fresh.add_argument("--seed", type=nonnegative)
    fresh.add_argument("--init-from", type=Path, help="seed a new run from a trusted model or checkpoint")

    resume = commands.add_parser("resume", help="continue a training checkpoint")
    add_training_options(resume)
    resume.add_argument("--checkpoint", type=Path, required=True)

    watch = commands.add_parser("watch", help="replay the best model in a trusted checkpoint")
    watch.add_argument("--checkpoint", type=Path, required=True)
    add_level(watch)
    add_fps(watch)
    watch.add_argument("--max-steps", type=positive)
    watch.add_argument("--once", action="store_true", help="exit after one episode")
    watch.add_argument("--rays", action="store_true", help="show the player raycasts")
    return parser


def train_command(args):
    if args.fast and not args.show:
        raise ValueError("--fast requires --show; headless training already runs at full speed")
    if args.command == "resume":
        state = load_checkpoint(args.checkpoint)
        if not isinstance(state, dict):
            raise ValueError("Legacy model files can seed a new run with train --init-from")
    else:
        initial_model = None
        level = args.level
        hidden_layers = 1 if args.hidden_layers is None else args.hidden_layers
        hidden_size = args.hidden_size or 21
        if args.init_from:
            if args.hidden_layers is not None or args.hidden_size is not None:
                raise ValueError("--init-from uses the saved model architecture")
            saved = load_checkpoint(args.init_from)
            initial_model, _, _ = best_model(saved)
            hidden_layers = initial_model.hiddenLayers
            hidden_size = initial_model.hiddenLayerSize
            if level is None and isinstance(saved, dict):
                level = saved["config"]["level"]
        if args.population < 2:
            raise ValueError("--population must be at least 2")
        config = TrainingConfig(
            7 if level is None else level, args.population, args.max_steps, hidden_layers, hidden_size
        )
        state = new_run(config, args.seed, initial_model)
    directory = make_run_directory(args.output)
    return train(state, args.generations, directory, args.show, args.fast, args.fps, args.stop_on_win)


def watch_command(args):
    saved = load_checkpoint(args.checkpoint)
    brain, fitness, _ = best_model(saved)
    config = saved["config"] if isinstance(saved, dict) else {}
    level = args.level if args.level is not None else config.get("level")
    if level is None:
        raise ValueError("--level is required when watching a legacy model")
    max_steps = args.max_steps or config.get("max_steps", 1800)

    print(f"Playing level {level} | saved fitness {fitness:.2f}", flush=True)
    game = Main(level, controlledByNN=True, populationSize=0, rayCastOnly=args.rays)
    try:
        while True:
            game.resetAndRestartNNBrains([brain])
            results = game.runNN(maxFrames=max_steps, fps=args.fps)
            if results is False:
                break
            _, fitness, completed = results[0]
            print(
                f"{'Completed' if completed else 'Stopped'} after {game.elapsed_seconds:.3f}s "
                f"| fitness {fitness:.2f}",
                flush=True,
            )
            if args.once:
                break
    finally:
        game.quitPygame()
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in ("train", "resume"):
            return train_command(args)
        if args.command == "watch":
            return watch_command(args)

        game = Main(args.level, args.repeat, rayCastOnly=args.rays, timedDeath=False)
        try:
            game.run(fps=args.fps)
        finally:
            game.quitPygame()
        return 0
    except (OSError, ValueError, pickle.UnpicklingError, EOFError, pygame.error) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
