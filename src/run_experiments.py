import argparse
import csv
import gc
from pathlib import Path

from mkp_instance import load_benchmark_instances
from mkp_model import solve_mkp


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DEFAULT_OUTPUT = ROOT_DIR / "results" / "resultados.csv"
NODEFILE_DIR = ROOT_DIR / "results" / "gurobi_nodefiles"
REPRESENTATIVE_INSTANCES = {1, 2, 3, 11, 12, 13, 21, 22, 23}
LIGHT_FILES = {"mknapcb1.txt", "mknapcb2.txt", "mknapcb4.txt"}


CSV_COLUMNS = [
    "file",
    "instance",
    "n",
    "m",
    "alpha",
    "reference_value",
    "gurobi_obj",
    "gap_to_reference_percent",
    "improvement_over_reference_percent",
    "is_better_than_reference",
    "mip_gap",
    "runtime_seconds",
    "status",
]


def parse_args() -> argparse.Namespace:
    # Argumentos opcionais ajudam a testar sem rodar tudo.
    parser = argparse.ArgumentParser(description="Run MKP experiments with Gurobi.")
    parser.add_argument("--time-limit", type=float, default=60, help="Gurobi time limit per instance.")
    parser.add_argument("--mip-gap", type=float, default=None, help="Stop when this relative MIP gap is reached.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV output path.")
    parser.add_argument("--all-instances", action="store_true", help="Run all 270 instances.")
    parser.add_argument("--all-sizes", action="store_true", help="Run the 81-instance representative set.")
    parser.add_argument("--max-instances", type=int, default=None, help="Optional limit for quick tests.")
    parser.add_argument("--file", type=str, default=None, help="Optional instance file filter, e.g. mknapcb1.txt.")
    parser.add_argument("--start", type=int, default=None, help="First instance number inside each file.")
    parser.add_argument("--end", type=int, default=None, help="Last instance number inside each file.")
    parser.add_argument("--restart", action="store_true", help="Overwrite the CSV instead of resuming it.")
    parser.add_argument("--log", action="store_true", help="Show Gurobi log in the terminal.")
    return parser.parse_args()


def format_number(value: float | None) -> str:
    # CSV fica vazio quando o Gurobi nao encontra solucao.
    if value is None:
        return ""
    return f"{value:.10g}"


def result_row(instance, result) -> dict[str, object]:
    # Converte a instancia e o resultado em uma linha do CSV.
    return {
        "file": instance.file_name,
        "instance": instance.instance,
        "n": instance.n,
        "m": instance.m,
        "alpha": f"{instance.alpha:.2f}",
        "reference_value": instance.reference_value,
        "gurobi_obj": format_number(result.gurobi_obj),
        "gap_to_reference_percent": format_number(result.gap_to_reference_percent),
        "improvement_over_reference_percent": format_number(result.improvement_over_reference_percent),
        "is_better_than_reference": result.is_better_than_reference,
        "mip_gap": format_number(result.mip_gap),
        "runtime_seconds": format_number(result.runtime_seconds),
        "status": result.status,
    }


def instance_key(row_or_instance) -> tuple[str, int]:
    # Identifica uma instancia pelo arquivo e pelo numero interno.
    return (row_or_instance.file_name, row_or_instance.instance)


def read_completed_instances(path: Path) -> set[tuple[str, int]]:
    # Permite continuar uma execucao interrompida sem repetir trabalho.
    if not path.exists():
        return set()

    with path.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return {(row["file"], int(row["instance"])) for row in reader}


def filter_instances(instances, args: argparse.Namespace):
    # Filtra subconjuntos para rodadas menores de experimento.
    if args.all_instances:
        pass
    elif args.all_sizes:
        instances = [instance for instance in instances if instance.instance in REPRESENTATIVE_INSTANCES]
    else:
        instances = [instance for instance in instances if instance.file_name in LIGHT_FILES]
    if args.file is not None:
        instances = [instance for instance in instances if instance.file_name == args.file]
    if args.start is not None:
        instances = [instance for instance in instances if instance.instance >= args.start]
    if args.end is not None:
        instances = [instance for instance in instances if instance.instance <= args.end]
    if args.max_instances is not None:
        instances = instances[: args.max_instances]
    return instances


def main() -> None:
    args = parse_args()
    instances = filter_instances(load_benchmark_instances(DATA_DIR), args)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    NODEFILE_DIR.mkdir(parents=True, exist_ok=True)
    completed = set() if args.restart else read_completed_instances(args.output)
    pending = [instance for instance in instances if instance_key(instance) not in completed]

    write_header = args.restart or not args.output.exists()
    mode = "w" if args.restart else "a"

    print(f"Instancias selecionadas: {len(instances)}")
    print(f"Modo: {selection_name(args)}")
    print(f"Instancias ja resolvidas: {len(instances) - len(pending)}")
    print(f"Instancias pendentes: {len(pending)}")

    with args.output.open(mode, newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()

        for index, instance in enumerate(pending, start=1):
            print(f"[{index}/{len(pending)}] {instance.file_name} instancia {instance.instance}")
            result = solve_mkp(
                instance,
                time_limit=args.time_limit,
                mip_gap=args.mip_gap,
                nodefile_dir=NODEFILE_DIR,
                log_to_console=args.log,
            )
            writer.writerow(result_row(instance, result))
            csv_file.flush()
            gc.collect()

    print(f"CSV gerado em: {args.output}")


def selection_name(args: argparse.Namespace) -> str:
    # Nome amigavel do conjunto escolhido para o experimento.
    if args.all_instances:
        return "todas as instancias"
    if args.all_sizes:
        return "subconjunto representativo completo"
    return "subconjunto leve de 90 instancias"


if __name__ == "__main__":
    main()
