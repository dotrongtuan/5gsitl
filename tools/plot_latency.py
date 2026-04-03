from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from tools.common import outputs_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    args = parser.parse_args()
    data = pd.read_csv(args.csv_path)
    out = outputs_dir("figures") / f"{Path(args.csv_path).stem}.png"
    data.T.plot(kind="bar", legend=False, figsize=(8, 4), title="Latency Snapshot")
    plt.tight_layout()
    plt.savefig(out)
    print(out)


if __name__ == "__main__":
    main()
