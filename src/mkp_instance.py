"""Utilities to read OR-Library MKP benchmark instances."""

from dataclasses import dataclass, replace
from pathlib import Path
import re


@dataclass(frozen=True)
class MKPInstance:
    """One 0-1 Multidimensional Knapsack instance."""

    file_name: str
    instance: int
    n: int
    m: int
    alpha: float
    reference_value: int
    profits: list[int]
    weights: list[list[int]]
    capacities: list[int]


def alpha_from_instance(instance_number: int) -> float:
    """Return the Chu-Beasley alpha group for instances 1..30."""
    if 1 <= instance_number <= 10:
        return 0.25
    if 11 <= instance_number <= 20:
        return 0.50
    if 21 <= instance_number <= 30:
        return 0.75
    raise ValueError(f"invalid instance number: {instance_number}")


def read_mknapcb_file(path: Path) -> list[MKPInstance]:
    """Read all instances from one mknapcb file using numeric tokens only."""
    tokens = [int(value) for value in path.read_text().split()]
    if not tokens:
        raise ValueError(f"empty instance file: {path}")

    total_instances = tokens[0]
    cursor = 1
    instances: list[MKPInstance] = []

    for instance_number in range(1, total_instances + 1):
        n = tokens[cursor]
        m = tokens[cursor + 1]
        reference_value = tokens[cursor + 2]
        cursor += 3

        profits = tokens[cursor : cursor + n]
        cursor += n

        weights = []
        for _ in range(m):
            weights.append(tokens[cursor : cursor + n])
            cursor += n

        capacities = tokens[cursor : cursor + m]
        cursor += m

        # Fail early if a malformed file silently produced short slices.
        if len(profits) != n or len(weights) != m or len(capacities) != m:
            raise ValueError(f"incomplete data in {path}, instance {instance_number}")
        if any(len(row) != n for row in weights):
            raise ValueError(f"invalid weight matrix in {path}, instance {instance_number}")

        instances.append(
            MKPInstance(
                file_name=path.name,
                instance=instance_number,
                n=n,
                m=m,
                alpha=alpha_from_instance(instance_number),
                reference_value=reference_value,
                profits=profits,
                weights=weights,
                capacities=capacities,
            )
        )

    if cursor != len(tokens):
        extra = len(tokens) - cursor
        raise ValueError(f"{path} has {extra} unused numeric tokens")

    return instances


def read_all_mknapcb(data_dir: Path) -> list[MKPInstance]:
    """Read the nine Chu-Beasley MKP benchmark files."""
    all_instances: list[MKPInstance] = []
    for index in range(1, 10):
        all_instances.extend(read_mknapcb_file(data_dir / f"mknapcb{index}.txt"))
    return all_instances


def load_benchmark_instances(data_dir: Path) -> list[MKPInstance]:
    """Read all instances and attach mkcbres best-known values."""
    instances = read_all_mknapcb(data_dir)
    references = read_reference_values(data_dir / "mkcbres.txt")

    loaded: list[MKPInstance] = []
    for instance in instances:
        key = reference_key(instance)
        if key not in references:
            raise ValueError(f"missing reference value for {key}")
        loaded.append(replace(instance, reference_value=references[key]))

    return loaded


def read_reference_values(path: Path) -> dict[str, int]:
    """Read the best feasible values table from mkcbres.txt."""
    references: dict[str, int] = {}
    pattern = re.compile(r"^\s*(\d+\.\d+-\d+)\s+(\d+)\s*$")

    for line in path.read_text().splitlines():
        if line.strip().startswith("Problem Name") and references:
            break

        match = pattern.match(line)
        if match:
            name, value = match.groups()
            references[name] = int(value)

    return references


def reference_key(instance: MKPInstance) -> str:
    """Build the mkcbres key, e.g. 5.100-00."""
    return f"{instance.m}.{instance.n}-{instance.instance - 1:02d}"
