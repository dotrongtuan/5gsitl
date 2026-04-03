from __future__ import annotations

import argparse

from channel_emulator import run_channel
from load_profile import load_profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()
    run_channel(load_profile(args.profile))


if __name__ == "__main__":
    main()
