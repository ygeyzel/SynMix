"""Check that each button drives at most one param."""

import tomllib
from collections import defaultdict
from pathlib import Path

import pytest

from synmix.inputs.midi_config import MidiConfig
from synmix.resource_loader import get_post_processing_params_file, get_scenes_dir

POST_PROCESSING_FILE = get_post_processing_params_file()
SCENE_FILES = sorted(
    p for p in get_scenes_dir().glob("*.toml") if p != POST_PROCESSING_FILE
)


def _params_by_button(path: Path) -> dict[str, list[str]]:
    with path.open("rb") as f:
        params = tomllib.load(f).get("params", [])
    by_button = defaultdict(list)
    for param in params:
        by_button[param["button"]].append(param["name"])
    return by_button


@pytest.mark.parametrize(
    "path", [*SCENE_FILES, POST_PROCESSING_FILE], ids=lambda p: p.name
)
def test_no_button_bound_twice(path: Path) -> None:
    """Bindings are keyed by button, so the last param bound wins."""
    dups = {b: names for b, names in _params_by_button(path).items() if len(names) > 1}
    assert not dups, f"buttons bound to more than one param: {dups}"


@pytest.mark.parametrize("path", SCENE_FILES, ids=lambda p: p.name)
def test_no_button_shadows_post_processing(path: Path) -> None:
    """Scene params take precedence over post-processing params."""
    post = _params_by_button(POST_PROCESSING_FILE)
    shadowed = {
        b: (names, post[b]) for b, names in _params_by_button(path).items() if b in post
    }
    assert not shadowed, f"scene params shadow post-processing params: {shadowed}"


@pytest.mark.parametrize(
    "path", [*SCENE_FILES, POST_PROCESSING_FILE], ids=lambda p: p.name
)
def test_every_label_is_in_the_midi_config(path: Path) -> None:
    """Scenes bind buttons by label, which the DDJ-T1 config must define."""
    config = MidiConfig.load("pioneer-ddj-t1")
    missing = []
    for label in _params_by_button(path):
        try:
            config.get_buttons_by_label(label)
        except ValueError:
            missing.append(label)
    assert not missing, f"labels missing from {config.config_name}: {missing}"
