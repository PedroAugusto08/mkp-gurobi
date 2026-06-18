from pathlib import Path

from mkp_instance import load_benchmark_instances, read_reference_values, reference_key


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"


def main() -> None:
    # Verificacao simples do parser, sem usar o Gurobi.
    instances = load_benchmark_instances(DATA_DIR)
    references = read_reference_values(DATA_DIR / "mkcbres.txt")

    missing = [reference_key(instance) for instance in instances if reference_key(instance) not in references]
    invalid_references = [instance for instance in instances if instance.reference_value <= 0]

    print(f"Instances read: {len(instances)}")
    print(f"Reference values read: {len(references)}")
    print(f"Missing references: {len(missing)}")
    print(f"Invalid references: {len(invalid_references)}")

    if missing:
        print("First missing keys:", ", ".join(missing[:5]))


if __name__ == "__main__":
    main()
