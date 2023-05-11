#!/usr/bin/python3

import argparse
import pandas as pd
import pathlib

import common


def main(benchmarks_json_path: str, results_dir_path: str, output_csv_path: str):
    benchmarks: list[str] = common.get_benchmarks_list(benchmarks_json_path)

    extractors = [
        common.RegexExtractor('IPC', r'CPU 0 cumulative IPC: (.+) instructions'),
        common.RegexExtractor('BP Accuracy', r'CPU 0 Branch Prediction Accuracy: (.+)%'),
        common.RegexExtractor('MPKI', r'MPKI: (.+) Average'),
    ]

    data = common.extract_geomean(pathlib.Path(results_dir_path), benchmarks, extractors)

    pd.DataFrame.from_dict(data).to_csv(output_csv_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Branch Predictions Data Parser')
    parser.add_argument('--benchmarks-file', type=str, default='benchmarks.json')
    parser.add_argument('--results-dir', type=str)
    parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()

    main(args.benchmarks_file, args.results_dir, args.output)
