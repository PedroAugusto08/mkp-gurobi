from dataclasses import dataclass
import math
from pathlib import Path
import time

import gurobipy as gp
from gurobipy import GRB

from mkp_instance import MKPInstance


@dataclass(frozen=True)
class MKPResult:
    # Resultado usado depois na tabela de experimentos.
    gurobi_obj: float | None
    gap_to_reference_percent: float | None
    improvement_over_reference_percent: float | None
    is_better_than_reference: bool
    mip_gap: float | None
    runtime_seconds: float
    status: str


def solve_mkp(
    instance: MKPInstance,
    time_limit: float = 300,
    mip_gap: float | None = None,
    nodefile_dir: Path | None = None,
    nodefile_start: float = 0.5,
    log_to_console: bool = False,
) -> MKPResult:
    # Monta e resolve a formulacao ILP do MKP.
    model = gp.Model(f"{instance.file_name}_{instance.instance}")
    start_time = time.perf_counter()

    try:
        model.Params.TimeLimit = time_limit
        model.Params.LogToConsole = int(log_to_console)
        model.Params.NodefileStart = nodefile_start

        if mip_gap is not None:
            model.Params.MIPGap = mip_gap
        if nodefile_dir is not None:
            model.Params.NodefileDir = str(nodefile_dir)

        # x[j] = 1 se o item j for escolhido; 0 caso contrario.
        x = model.addVars(instance.n, vtype=GRB.BINARY, name="x")

        # Maximiza o lucro total dos itens escolhidos.
        model.setObjective(
            gp.quicksum(instance.profits[j] * x[j] for j in range(instance.n)),
            GRB.MAXIMIZE,
        )

        # Cada recurso deve respeitar sua capacidade.
        for i in range(instance.m):
            model.addConstr(
                gp.quicksum(instance.weights[i][j] * x[j] for j in range(instance.n))
                <= instance.capacities[i],
                name=f"capacity_{i + 1}",
            )

        model.optimize()

        gurobi_obj = model.ObjVal if model.SolCount > 0 else None
        result_mip_gap = model.MIPGap if model.SolCount > 0 else None

        return MKPResult(
            gurobi_obj=gurobi_obj,
            gap_to_reference_percent=_gap_to_reference_percent(gurobi_obj, instance.reference_value),
            improvement_over_reference_percent=_improvement_over_reference_percent(
                gurobi_obj, instance.reference_value
            ),
            is_better_than_reference=_is_better_than_reference(gurobi_obj, instance.reference_value),
            mip_gap=result_mip_gap,
            runtime_seconds=_safe_runtime(model.Runtime, start_time),
            status=_status_name(model.Status),
        )
    finally:
        model.dispose()


def _gap_to_reference_percent(gurobi_obj: float | None, reference_value: int) -> float | None:
    # Percentual positivo quando o Gurobi fica abaixo da referencia.
    if gurobi_obj is None or reference_value <= 0:
        return None
    return 100 * (reference_value - gurobi_obj) / reference_value


def _improvement_over_reference_percent(gurobi_obj: float | None, reference_value: int) -> float | None:
    # Percentual positivo quando o Gurobi supera a referencia.
    if gurobi_obj is None or reference_value <= 0:
        return None
    return 100 * (gurobi_obj - reference_value) / reference_value


def _is_better_than_reference(gurobi_obj: float | None, reference_value: int) -> bool:
    # Indica se a solucao encontrada supera o valor de referencia.
    return gurobi_obj is not None and gurobi_obj > reference_value


def _safe_runtime(gurobi_runtime: float, start_time: float) -> float:
    # Usa tempo externo se o runtime do Gurobi vier invalido.
    external_runtime = time.perf_counter() - start_time
    if gurobi_runtime is None or gurobi_runtime < 0 or not math.isfinite(gurobi_runtime):
        return external_runtime
    return gurobi_runtime


def _status_name(status_code: int) -> str:
    # Converte o codigo do Gurobi para um nome legivel.
    names = {
        GRB.OPTIMAL: "OPTIMAL",
        GRB.INFEASIBLE: "INFEASIBLE",
        GRB.INF_OR_UNBD: "INF_OR_UNBD",
        GRB.UNBOUNDED: "UNBOUNDED",
        GRB.TIME_LIMIT: "TIME_LIMIT",
        GRB.INTERRUPTED: "INTERRUPTED",
        GRB.NUMERIC: "NUMERIC",
        GRB.SUBOPTIMAL: "SUBOPTIMAL",
    }
    return names.get(status_code, f"STATUS_{status_code}")
