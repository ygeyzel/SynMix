"""Compile every shader and check it against the params that drive it."""

import os
import tomllib
from pathlib import Path

import moderngl
import pytest

from synmix.resource_loader import (
    get_post_processing_params_file,
    get_scenes_dir,
    get_shaders_dir,
)

SHADERS_DIR = get_shaders_dir()
VERTEX_SHADER = "vertex.glsl"
FRAGMENT_SHADERS = sorted(
    p.name for p in SHADERS_DIR.glob("*.glsl") if p.name != VERTEX_SHADER
)


def _params_files() -> dict[str, Path]:
    """Map each params TOML to the fragment shader it drives."""
    files = {}
    for path in sorted(get_scenes_dir().glob("*.toml")):
        if path == get_post_processing_params_file():
            continue
        with path.open("rb") as f:
            files[path.name] = (path, tomllib.load(f)["fragment_shader_filename"])
    post = get_post_processing_params_file()
    files[post.name] = (post, "post_processing.glsl")
    return files


PARAMS_FILES = _params_files()


@pytest.fixture(scope="session")
def ctx() -> moderngl.Context:
    """Headless OpenGL context; falls back to EGL where there is no display."""
    errors = []
    for kwargs in ({}, {"backend": "egl"}):
        try:
            return moderngl.create_standalone_context(require=330, **kwargs)
        except Exception as e:  # noqa: BLE001 - moderngl raises bare Exception
            errors.append(f"{kwargs or 'default'}: {e}")
    msg = "No OpenGL 3.3 context available: " + "; ".join(errors)
    if os.environ.get("CI"):
        pytest.fail(msg)
    pytest.skip(msg)


def _compile(ctx: moderngl.Context, fragment_shader: str) -> moderngl.Program:
    return ctx.program(
        vertex_shader=(SHADERS_DIR / VERTEX_SHADER).read_text(),
        fragment_shader=(SHADERS_DIR / fragment_shader).read_text(),
    )


@pytest.mark.parametrize("fragment_shader", FRAGMENT_SHADERS)
def test_shader_compiles(ctx: moderngl.Context, fragment_shader: str) -> None:
    _compile(ctx, fragment_shader)


@pytest.mark.parametrize("params_file", PARAMS_FILES)
def test_params_are_active_uniforms(ctx: moderngl.Context, params_file: str) -> None:
    """A param whose uniform is missing or optimized out is silently ignored."""
    path, fragment_shader = PARAMS_FILES[params_file]
    with path.open("rb") as f:
        param_names = [p["name"] for p in tomllib.load(f).get("params", [])]
    program = _compile(ctx, fragment_shader)
    missing = [n for n in param_names if n not in program]
    assert not missing, f"params not used by {fragment_shader}: {missing}"
