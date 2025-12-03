"""SynMix entry point - allows running as 'python -m synmix' or 'uv run synmix'."""

import moderngl_window as mglw

from synmix.top_level.screen import Screen


def main() -> None:
    """Main entry point for SynMix application."""
    config = mglw.create_window_config_instance(config_cls=Screen)
    try:
        mglw.run_window_config_instance(config)
    except KeyboardInterrupt:
        print("Stopped")


if __name__ == "__main__":
    main()
