from dataclasses import dataclass

import gurobipy as gp
from gurobipy import GRB

from mkp_instance import MKPInstance


@dataclass(frozen=True)
class MKPResult:
    # Resultado usado depois na tabela de experimentos.
    gurobi_obj: float | None
    gap_to_reference: float | None
    mip_gap: float | None
    runtime_seconds: float
    status: str


def solve_mkp(instance: MKPInstance, time_limit: float = 300, log_to_console: bool = False) -> MKPResult:
    # Monta e resolve a formulacao ILP do MKP.
    model = gp.Model(f"{instance.file_name}_{instance.instance}")
    model.Params.TimeLimit = time_limit
    model.Params.LogToConsole = int(log_to_console)

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
    mip_gap = model.MIPGap if model.SolCount > 0 else None
    gap_to_reference = _gap_to_reference(gurobi_obj, instance.reference_value)

    return MKPResult(
        gurobi_obj=gurobi_obj,
        gap_to_reference=gap_to_reference,
        mip_gap=mip_gap,
        runtime_seconds=model.Runtime,
        status=_status_name(model.Status),
    )


def _gap_to_reference(gurobi_obj: float | None, reference_value: int) -> float | None:
    # Diferenca relativa entre referencia e objetivo do Gurobi.
    if gurobi_obj is None or reference_value <= 0:
        return None
    return (reference_value - gurobi_obj) / reference_value


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
