#!/usr/bin/python3

import argparse
import pathlib
import subprocess
from tqdm import tqdm


DEFAULT_WARMUP = 10_000_000
DEFAULT_SIMULATION = 50_000_000


def run_command(*args, **kwargs) -> str:
    if "stdout" not in kwargs:
        kwargs["stdout"] = subprocess.PIPE
    if "stderr" not in kwargs:
        kwargs["stderr"] = subprocess.PIPE
    if "shell" not in kwargs:
        kwargs["shell"] = True
    cmd = " ".join(str(x) for x in args)
    status, output = subprocess.getstatusoutput(cmd)
    if status != 0:
        raise RuntimeError(f"Process {cmd} failed with non-null status. Out: {output}")
    return output


def run_sim(benchmark: str, warmup_instructions: int, simulation_instructions: int) -> str:
    return run_command(
        "./bin/champsim",
        "--warmup_instructions",
        warmup_instructions,
        "--simulation_instructions",
        simulation_instructions,
        benchmark)


def main(config: str, benchmarks_dir: str, warmup_instructions: int, simulation_instructions: int):
    dir: pathlib.Path = pathlib.Path(benchmarks_dir)
    if not dir.is_dir():
        raise RuntimeError(f"Provided {benchmarks_dir} is not directory")
    run_command("./config.sh", config)
    run_command("make", "-j16")

    files = [x for x in dir.iterdir() if x.name.endswith(".xz")]
    for file in tqdm(files):
        output = run_sim(dir.joinpath(file.name), warmup_instructions, simulation_instructions)
        with dir.joinpath(f"{file.name}.out").open(mode="w") as f:
            f.write(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Simulation Runner")
    parser.add_argument("--config", default="champsim_config.json")
    parser.add_argument("--benchmarks-dir", default="benchmarks")
    parser.add_argument("--warmup-instructions", type=int, default=DEFAULT_WARMUP)
    parser.add_argument("--simulation-instructions", type=int, default=DEFAULT_SIMULATION)
    args = parser.parse_args()

    main(args.config, args.benchmarks_dir, args.warmup_instructions, args.simulation_instructions)
