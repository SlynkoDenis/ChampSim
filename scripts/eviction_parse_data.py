#!/usr/bin/python3

import argparse
import pandas as pd
import pathlib
import re

import common


class CacheHitExtractor(common.GeomeanExtractor):
    def __init__(self, title: str, cache_name: str):
        super().__init__(title)
        self._pattern = re.compile(cache_name + r' TOTAL[ \t]+ACCESS:[ \t]+(\d+)[ \t]+HIT:[ \t]+(\d+)[ \t]+MISS')

    def _extract_impl(self, text: str) -> float:
        matches = self._pattern.findall(text)
        assert len(matches) == 1
        return float(matches[0][1]) / float(matches[0][0])


def main(benchmarks_json_path: str, results_dir_path: str, output_csv_path: str):
    benchmarks: list[str] = common.get_benchmarks_list(benchmarks_json_path)

    extractors = [
        common.RegexExtractor('IPC', r'CPU 0 cumulative IPC: (.+) instructions'),
        CacheHitExtractor('L2C', 'cpu0_L2C'),
        CacheHitExtractor('L1D', 'cpu0_L1D'),
        CacheHitExtractor('LLC', 'LLC'),
    ]

    data = common.extract_geomean(pathlib.Path(results_dir_path), benchmarks, extractors)

    pd.DataFrame.from_dict(data).to_csv(output_csv_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='L2 Cache Eviction Data Parser')
    parser.add_argument('--benchmarks-file', type=str, default='benchmarks.json')
    parser.add_argument('--results-dir', type=str)
    parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()

    main(args.benchmarks_file, args.results_dir, args.output)
