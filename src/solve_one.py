from pathlib import Path

from mkp_instance import load_benchmark_instances
from mkp_model import solve_mkp


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"


def main() -> None:
    # Resolve uma instancia pequena para validar o modelo.
    instance = load_benchmark_instances(DATA_DIR)[0]
    result = solve_mkp(instance, time_limit=60, log_to_console=True)

    print(f"File: {instance.file_name}")
    print(f"Instance: {instance.instance}")
    print(f"Reference: {instance.reference_value}")
    print(f"Gurobi objective: {result.gurobi_obj}")
    print(f"Gap to reference (%): {result.gap_to_reference_percent}")
    print(f"Improvement over reference (%): {result.improvement_over_reference_percent}")
    print(f"Better than reference: {result.is_better_than_reference}")
    print(f"MIP gap: {result.mip_gap}")
    print(f"Runtime seconds: {result.runtime_seconds:.2f}")
    print(f"Status: {result.status}")


if __name__ == "__main__":
    main()
