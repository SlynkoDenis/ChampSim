#!/usr/bin/python3

import argparse
import pathlib
from tqdm import tqdm
import urllib.request

import common


def get_download_url(benchmark_name: str) -> str:
    url_prefix: str = "https://dpc3.compas.cs.stonybrook.edu/champsim-traces/speccpu"
    return f"{url_prefix}/{benchmark_name}"

def create_dir(dirname: str) -> pathlib.Path:
    path: pathlib.Path = pathlib.Path("./").joinpath(dirname)
    if path.exists() and not path.is_dir():
        raise AssertionError(f"{dirname} must not exists or be a directory")

    path.mkdir(exist_ok=True)
    return path

def download_benchmarks(dirname: str, benchmarks: list[str]):
    dirpath = create_dir(dirname)
    for name in tqdm(benchmarks):
        urllib.request.urlretrieve(get_download_url(name), dirpath.joinpath(name))


def main(dirname: str, benchmarks_json_path: str):
    download_benchmarks(dirname, common.get_benchmarks_list(benchmarks_json_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Benchmarks Downloader")
    parser.add_argument("--dirname", default="benchmarks")
    parser.add_argument("--benchmarks-file", default="benchmarks.json")
    args = parser.parse_args()

    main(args.dirname, args.benchmarks_file)
