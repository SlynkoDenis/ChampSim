#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import sys
from typing import Collection


def merge_frames(frames: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, list[str]]:
    def _rename_columns(df: pd.DataFrame, suffix: str) -> pd.DataFrame:
        return df.rename(
            mapper=lambda x: x if x == 'name' else f'{x}_{suffix}',
            axis=1
        )

    assert frames
    df: pd.DataFrame = None
    columns: list[str] = None

    for name, rhs_df in frames.items():
        if df is None:
            df = rhs_df
            columns = [
                x for x in df.columns.to_list()
                if x != 'name' and not x.startswith('Unnamed:')
            ]
            df = _rename_columns(df, name)
        else:
            df = pd.merge(
                df,
                _rename_columns(rhs_df, name),
                how='left',
                left_on=['name'],
                right_on=['name'],
            )

    df['name'] = df['name'].apply(lambda x: x[:3])
    return df, columns


def plot_gists(csv_paths: Collection[pathlib.Path], logy=True):
    frames = {p.stem: pd.read_csv(p) for p in csv_paths}
    names = list(frames.keys())
    df, columns = merge_frames(frames)

    log_suffix = '_logscale' if logy else ''
    for metric_name in columns:
        df.plot.bar(
            x='name',
            y=[f'{metric_name}_{x}' for x in names],
            ylabel=metric_name,
            logy=logy
        )
        plt.savefig(f'{metric_name}{log_suffix}.png')


def main(csv_paths: list[str]):
    plot_gists([pathlib.Path(x) for x in csv_paths])


if __name__ == '__main__':
    main(sys.argv[1:])
