from collections.abc import Iterator
from dataclasses import fields
from pathlib import Path

import numpy as np
import pytest

from algoarcade.backends.base import Button
from algoarcade.backends.pyboy import PyBoyBackend
from algoarcade.games.super_mario_land.reader import SuperMarioLandReader, SuperMarioLandState

SUPER_MARIO_LAND_ROM = Path(__file__).parents[1] / "data/roms/super_mario_land.gb"
ACTIONS = [Button.UP, Button.DOWN, Button.LEFT, Button.RIGHT, Button.A, Button.B]


@pytest.fixture
def backend() -> Iterator[PyBoyBackend]:
    if not SUPER_MARIO_LAND_ROM.exists():
        pytest.skip(f"no ROM at {SUPER_MARIO_LAND_ROM}")
    backend = PyBoyBackend(SUPER_MARIO_LAND_ROM)
    backend._pyboy.game_wrapper.start_game(timer_div=0)
    yield backend
    backend.close()


def test_state_has_no_score_or_coins() -> None:
    assert {field.name for field in fields(SuperMarioLandState)} == {
        "lives_left",
        "time_left",
        "world",
        "level_progress",
    }


@pytest.mark.rom
def test_reader_matches_the_pyboy_wrapper_over_1000_random_steps(backend: PyBoyBackend) -> None:
    wrapper = backend._pyboy.game_wrapper
    reader = SuperMarioLandReader()
    rng = np.random.default_rng(0)
    states = []
    mismatches = []
    for step in range(1000):
        backend.press([ACTIONS[rng.integers(len(ACTIONS))]])
        state = reader.read(backend)
        expected = SuperMarioLandState(
            lives_left=wrapper.lives_left,
            time_left=wrapper.time_left,
            world=wrapper.world,
            level_progress=wrapper.level_progress,
        )
        states.append(state)
        if state != expected:
            mismatches.append((step, state, expected))
    assert len(set(states)) > 1, "the state never changed, so this run proves nothing"
    assert not mismatches, f"{len(mismatches)} of 1000 steps differ: {mismatches}"
