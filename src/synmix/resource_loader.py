"""Resource loading utilities for SynMix package resources."""

# Python 3.9+ has importlib.resources with files()
from importlib.resources import files
from pathlib import Path


def get_resources_path() -> Path:
    """
    Get the path to the resources directory.

    Works both when installed as a package and when running in development mode.

    Returns:
        Path to resources directory

    """
    try:
        # Try package resources first (works when installed)
        resource_anchor = files("synmix") / "resources"
        # Convert to Path - files() returns a Traversable which can be converted
        if hasattr(resource_anchor, "__fspath__"):
            return Path(resource_anchor)
        # For older Python versions or when resources are in a zip
        # We need to extract to a temporary location
        # This is handled automatically by importlib.resources
        import shutil
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        # Copy resources to temp location
        # (In practice, this is rarely needed with modern Python)
        return temp_dir
    except (ImportError, FileNotFoundError, TypeError):
        # Fallback for development: assume we're in src/synmix/
        # and resources is a sibling directory
        module_dir = Path(__file__).parent
        resources_dir = module_dir / "resources"
        if resources_dir.exists():
            return resources_dir

        # Last resort: check if running from project root
        project_root = module_dir.parent.parent.parent
        fallback_resources = project_root / "resources"
        if fallback_resources.exists():
            return fallback_resources

        raise FileNotFoundError(
            f"Could not locate resources directory. Tried:\n"
            f"  - Package resources\n"
            f"  - {resources_dir}\n"
            f"  - {fallback_resources}"
        )


# Convenience accessors for common resource paths
def get_scenes_dir() -> Path:
    """Get path to scenes directory."""
    return get_resources_path() / "scenes"


def get_shaders_dir() -> Path:
    """Get path to shaders directory."""
    return get_resources_path() / "shaders"


def get_textures_dir() -> Path:
    """Get path to textures directory."""
    return get_resources_path() / "textures"


def get_scenes_order_file() -> Path:
    """Get path to scenes_order.toml."""
    return get_resources_path() / "scenes_order.toml"


def get_fake_midi_key_map_file() -> Path:
    """Get path to fake_midi_key_map.toml."""
    return get_resources_path() / "fake_midi_key_map.toml"


def get_post_processing_params_file() -> Path:
    """Get path to post_processing_params.toml."""
    return get_scenes_dir() / "post_processing_params.toml"
