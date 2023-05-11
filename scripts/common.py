from abc import ABC, abstractmethod
import json
import math
import pathlib
import re
from typing import Any, Collection


def get_benchmarks_list(benchmarks_json_path: str) -> list[str]:
    with pathlib.Path(benchmarks_json_path).open(mode="r") as f:
        return json.load(f)["benchmarks"]


class Extractor(ABC):
    @abstractmethod
    def __call__(self, text: str) -> Any:
        pass


class GeomeanExtractor(Extractor):
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.values: list[float] = []

    def clear(self):
        self.values = []

    def geomean(self) -> float:
        if not self.values:
            return 0
        self.values = [x if x != 0.0 else 1.0 for x in self.values]
        log_sum = sum(math.log(x) for x in self.values)
        return math.exp(log_sum / len(self.values))

    def __call__(self, text: str) -> float:
        val = self._extract_impl(text)
        self.values.append(val)
        return val

    @abstractmethod
    def _extract_impl(self, text: str) -> float:
        pass


class RegexExtractor(GeomeanExtractor):
    def __init__(self, title: str, pattern: str):
        super().__init__(title)
        self._pattern = re.compile(pattern)

    def _extract_impl(self, text: str) -> float:
        matches = self._pattern.findall(text)
        assert len(matches) == 1
        return float(matches[0])


def extract_single(path: pathlib.Path, extractor: Extractor) -> Any:
    with path.open(mode='r') as f:
        text: str = f.read()
        return extractor(text)


def extract_geomean(
    base_dir: pathlib.Path,
    files: Collection[str],
    extractors: Collection[GeomeanExtractor]
) -> dict[str, list[float]]:
    data = {'name': []} | {x.title: [] for x in extractors}

    for name in files:
        data['name'].append(name)
        for x in extractors:
            data[x.title].append(extract_single(base_dir.joinpath(f'{name}.out'), x))

    # write geomean
    data['name'].append('geomean')
    for x in extractors:
        data[x.title].append(x.geomean())

    return data
