import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pygame

from main import Main
from timing import FixedStepClock, NANOSECONDS_PER_SECOND, SIMULATION_HZ
from training import TrainingConfig, best_model, load_checkpoint, new_run, train


class TimingTests(unittest.TestCase):
    def test_same_elapsed_time_and_trajectory_at_different_render_rates(self):
        outcomes = []
        for fps in (30, 60, 120, 144):
            clock = FixedStepClock()
            game = Main(0, display=False, timedDeath=False)
            previous = 0
            for frame in range(1, fps * 2 + 1):
                timestamp = frame * NANOSECONDS_PER_SECOND // fps
                for _ in range(clock.advance(timestamp - previous)):
                    game.step((1, game.elapsed_steps >= 50))
                previous = timestamp
            self.assertEqual(game.elapsed_steps, 2 * SIMULATION_HZ)
            outcomes.append((game.elapsed_seconds, game.players[0].rect.copy(), game.getPlayerStats()))
        self.assertTrue(all(outcome == outcomes[0] for outcome in outcomes))

    def test_timeout_reports_elapsed_seconds_and_resets(self):
        game = Main(0, display=False, timeDeathAmount=1)
        for _ in range(SIMULATION_HZ - 1):
            self.assertFalse(game.step()[2])
        _, reward, done, won, _, elapsed = game.step()
        self.assertEqual((reward, done, won, elapsed), (-10, True, False, 1.0))
        self.assertEqual(game.elapsed_seconds, 0)

    def test_win_detected_without_rendering(self):
        game = Main(0, display=False, playerXOveride=1240, playerYOveride=640)
        _, reward, done, won, score, _ = game.step()
        self.assertEqual((reward, done, won, score, game.activeLevel), (10, True, True, 1, 1))
        self.assertEqual(game.elapsed_seconds, 0)

    def test_stall_catch_up_is_bounded(self):
        self.assertEqual(FixedStepClock().advance(10 * NANOSECONDS_PER_SECOND), 15)


class TrainingTests(unittest.TestCase):
    def test_resume_matches_uninterrupted_training(self):
        config = TrainingConfig(level=0, population=4, max_steps=25, hidden_layers=1, hidden_size=12)
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temporary)
            full, partial, resumed = (root / name for name in ("full", "partial", "resumed"))
            for directory in (full, partial, resumed):
                directory.mkdir()
            train(new_run(config, seed=42), 4, full)
            train(new_run(config, seed=42), 2, partial)
            train(load_checkpoint(partial / "latest.pkl"), 2, resumed)
            expected = load_checkpoint(full / "latest.pkl")
            actual = load_checkpoint(resumed / "latest.pkl")
            self.assertEqual(expected["history"], actual["history"])
            self.assertEqual(expected["rng_state"], actual["rng_state"])
            self.assertEqual(expected["best"][1:], actual["best"][1:])
            for expected_brain, actual_brain in zip(expected["population"], actual["population"]):
                for expected_layer, actual_layer in zip(expected_brain.layers, actual_brain.layers):
                    np.testing.assert_array_equal(expected_layer.w, actual_layer.w)
                    np.testing.assert_array_equal(expected_layer.b, actual_layer.b)
            self.assertFalse(pygame.display.get_init())

    def test_legacy_checkpoint_can_replay_without_a_display(self):
        model_path = Path(__file__).resolve().parents[1] / "nn_models/21 12 3/level3.pkl"
        brain, fitness, _ = best_model(load_checkpoint(model_path))
        game = Main(3, display=False, controlledByNN=True, populationSize=0)
        game.resetAndRestartNNBrains([brain])
        _, actual_fitness, completed = game.runNN()[0]
        self.assertEqual(actual_fitness, fitness)
        self.assertTrue(completed)
        self.assertEqual(game.elapsed_seconds, game.players[0].framesAlive / SIMULATION_HZ)
        self.assertFalse(pygame.display.get_init())


if __name__ == "__main__":
    unittest.main()
