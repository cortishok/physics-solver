from variables import (
    Variable,
    VARIABLE_DISPLAY_NAMES,
    VARIABLE_UNITS,
    STRING_TO_VARIABLE,
)
from units import parse_value_with_unit
from physics_formulas import FORMULAS_LIST, Formula
import math_engine

DEFAULT_CONSTANTS = {
    Variable.G_ACCEL: 9.81,
    Variable.SPEED_OF_LIGHT: 3.0e8,
    Variable.PLANCK: 6.626e-34,
    Variable.ELEM_CHARGE: 1.602e-19,
    Variable.GAS_CONSTANT: 8.314,
}

ELECTRICAL_CONTEXT_KEYS = {
    "I", "U", "U_volt", "Q_joule", "P_el", "E_ind", "E_emf",
    "U_stop", "A_vyh", "l", "freq_rot", "C", "L_ind", "R_ohm",
}


def get_display_name(var: Variable) -> str:
    return VARIABLE_DISPLAY_NAMES.get(var, var.value)


def _format_val(val) -> str:
    if isinstance(val, str):
        return val
    if abs(val) >= 1e5 or (0 < abs(val) < 1e-3):
        return f"{val:.4e}"
    if abs(val - round(val)) < 1e-7:
        return str(int(round(val)))
    return f"{val:.4f}".rstrip("0").rstrip(".")


def _resolve_variable_name(k_str: str, raw_val: str, all_keys: set[str]) -> Variable | None:
    """Разрешение коллизии имени 'R' (Радиус vs Сопротивление)."""
    if k_str == "R":
        val_s = str(raw_val).strip()
        parts = val_s.split()
        unit_part = parts[-1] if len(parts) > 1 else ""
        if unit_part in ("м", "см", "мм", "км"):
            return Variable.RADIUS
        if unit_part in ("Ом", "кОм"):
            return Variable.RESISTANCE
        if not (all_keys & ELECTRICAL_CONTEXT_KEYS):
            return Variable.RADIUS
        return Variable.RESISTANCE
    return STRING_TO_VARIABLE.get(k_str)


def solve_and_calculate(given: dict, target_str: str) -> dict:
    target_clean = str(target_str).strip()
    all_input_keys = {str(k).strip() for k in given.keys()} | {target_clean}

    target_var = _resolve_variable_name(target_clean, "", all_input_keys)
    if target_var is None:
        return {"error": f"Целевая переменная '{target_clean}' не распознана."}

    # 1. Парсинг входного словаря Дано
    known_values: dict[Variable, float | str] = dict(DEFAULT_CONSTANTS)
    user_vars: set[Variable] = set()

    for raw_k, raw_v in given.items():
        k_str = str(raw_k).strip()
        var_enum = _resolve_variable_name(k_str, str(raw_v), all_input_keys)
        if var_enum is None:
            return {"error": f"Ошибка разбора: неизвестная переменная '{k_str}'"}

        is_func_var = var_enum in (
            Variable.X_FUNC,
            Variable.V_FUNC,
            Variable.A_FUNC,
            Variable.F_FUNC,
        )
        try:
            parsed_val = parse_value_with_unit(raw_v, is_func=is_func_var)
            if is_func_var:
                math_engine.normalize_expr(str(parsed_val))
            known_values[var_enum] = parsed_val
            user_vars.add(var_enum)
        except Exception as exc:
            return {"error": str(exc)}

    # Контекстная маршрутизация цели
    if target_var == Variable.MOMENTUM and Variable.FREQ_LIGHT in user_vars:
        target_var = Variable.MOMENTUM_PHOTONS

    if (
        target_var == Variable.FORCE
        and Variable.X_FUNC in user_vars
        and Variable.TIME not in user_vars
    ):
        target_var = Variable.F_FUNC

    if target_var in user_vars:
        val = known_values[target_var]
        unit = VARIABLE_UNITS.get(target_var, "")
        ans_str = f"{_format_val(val)} {unit}".strip()
        return {
            "result": val,
            "final_answer_str": ans_str,
            "steps": [f"1. {get_display_name(target_var)} = {ans_str} (из условия)"],
            "error": None,
        }

    # 2. Послойный вывод с защитой физических областей применимости
    known_vars = set(known_values.keys())
    derivation: dict[Variable, tuple[str, Formula]] = {}

    def _depends_on(var: Variable, target: Variable) -> bool:
        stack = [var]
        seen = set()
        while stack:
            curr = stack.pop()
            if curr == target:
                return True
            if curr in seen or curr in known_values or curr not in derivation:
                continue
            seen.add(curr)
            mode, f = derivation[curr]
            if mode == "direct":
                stack.extend(f.requires)
            else:
                stack.append(f.result_variable)
                stack.extend(r for r in f.requires if r != curr)
        return False

    def _tree_stats(deps: list[Variable], mode: str, formula: Formula) -> tuple:
        u_vars = set()
        all_direct = 1 if mode == "direct" else 0
        bridges = 1 if formula.is_bridge else 0
        steps_count = 1

        stack = list(deps)
        seen = set()
        while stack:
            curr = stack.pop()
            if curr in seen:
                continue
            seen.add(curr)
            if curr in user_vars:
                u_vars.add(curr)
            if curr in known_values or curr not in derivation:
                continue
            steps_count += 1
            m_curr, f_curr = derivation[curr]
            if m_curr != "direct":
                all_direct = 0
            if f_curr.is_bridge:
                bridges += 1
            if m_curr == "direct":
                stack.extend(f_curr.requires)
            else:
                stack.append(f_curr.result_variable)
                stack.extend(r for r in f_curr.requires if r != curr)

        is_phys_law = 0 if formula.is_bridge else 1
        return (is_phys_law, all_direct, len(u_vars), -bridges, -steps_count, len(formula.requires))

    def _current_var_score(var: Variable) -> tuple:
        mode, f = derivation[var]
        deps = (
            list(f.requires)
            if mode == "direct"
            else [f.result_variable] + [r for r in f.requires if r != var]
        )
        return _tree_stats(deps, mode, f)

    for _ in range(8):
        updates_in_layer: dict[Variable, tuple[str, Formula, tuple]] = {}

        for formula in FORMULAS_LIST:
            res_var = formula.result_variable

            # Физическое ограничение 1: энергия торможения E_k = m*v0^2/2 только при v0 != 0
            if (
                formula.name == "Начальная кинетическая энергия при торможении"
                and known_values.get(Variable.VELOCITY_0) == 0.0
            ):
                continue

            # Физическое ограничение 2: формула a = 2S/t^2 применима только если нет ненулевой v0
            if (
                formula.pretty == "a = 2·S / t²"
                and Variable.VELOCITY_0 in user_vars
                and known_values.get(Variable.VELOCITY_0) != 0.0
            ):
                continue

            # Физическое ограничение 3: угол наклона мотоциклиста α = arctg(μ) не должен
            # создавать фантомную наклонную плоскость, если угол α не является целью задачи
            if formula.pretty == "α = arctg(μ)" and target_var != Variable.ANGLE:
                continue

            # Прямой шаг
            if res_var not in known_values and all(req in known_vars for req in formula.requires):
                if any(_depends_on(req, res_var) for req in formula.requires):
                    continue
                cand_score = _tree_stats(list(formula.requires), "direct", formula)
                existing_score = (
                    updates_in_layer[res_var][2]
                    if res_var in updates_in_layer
                    else (_current_var_score(res_var) if res_var in derivation else None)
                )
                if existing_score is None or cand_score > existing_score:
                    updates_in_layer[res_var] = ("direct", formula, cand_score)

            # Обратный алгебраический шаг
            elif not formula.is_bridge and res_var in known_vars:
                missing = [req for req in formula.requires if req not in known_vars]
                if len(missing) == 1:
                    miss_var = missing[0]
                    if (
                        miss_var not in known_vars
                        and miss_var not in updates_in_layer
                        and miss_var
                        not in (
                            Variable.X_FUNC,
                            Variable.V_FUNC,
                            Variable.A_FUNC,
                            Variable.F_FUNC,
                        )
                    ):
                        deps = [res_var] + [r for r in formula.requires if r != miss_var]
                        cand_score = _tree_stats(deps, "inverse", formula)
                        updates_in_layer[miss_var] = ("inverse", formula, cand_score)

        if not updates_in_layer:
            break

        for v, (m, f, _) in updates_in_layer.items():
            known_vars.add(v)
            derivation[v] = (m, f)

    if target_var not in known_vars:
        return {"error": "Не удалось найти решение: цепочка формул не замкнулась."}

    # 3. Топологическая сортировка дерева вывода для target_var
    pruned_vars: list[Variable] = []
    visited_topo: set[Variable] = set()

    def _topo_dfs(v: Variable):
        if v in visited_topo or v in known_values or v not in derivation:
            return
        visited_topo.add(v)
        mode, formula = derivation[v]
        if mode == "direct":
            for req in formula.requires:
                _topo_dfs(req)
        else:
            _topo_dfs(formula.result_variable)
            for req in formula.requires:
                if req != v:
                    _topo_dfs(req)
        pruned_vars.append(v)

    _topo_dfs(target_var)

    # 4. Пошаговое вычисление
    state = dict(known_values)
    steps_str = []

    try:
        for idx, out_var in enumerate(pruned_vars, 1):
            mode, formula = derivation[out_var]
            if mode == "direct":
                val = formula.calc(state)
                state[out_var] = val
                unit = VARIABLE_UNITS.get(out_var, "")
                val_str = f"{_format_val(val)} {unit}".strip()
                steps_str.append(f"{idx}. {formula.pretty} ➔ {val_str}")
            else:
                known_sub = {r: state[r] for r in formula.requires if r != out_var}
                expected_y = state[formula.result_variable]
                val = math_engine.solve_implicit_for_var(
                    formula.calc, known_sub, out_var, expected_y
                )
                state[out_var] = val
                unit = VARIABLE_UNITS.get(out_var, "")
                val_str = f"{_format_val(val)} {unit}".strip()
                steps_str.append(
                    f"{idx}. Из [{formula.pretty}] выражаем {get_display_name(out_var)} ➔ {val_str}"
                )
    except Exception as exc:
        return {"error": f"Математическая ошибка при расчёте: {exc}"}

    final_val = state[target_var]
    final_unit = VARIABLE_UNITS.get(target_var, "")
    final_answer_str = f"{_format_val(final_val)} {final_unit}".strip()

    return {
        "result": final_val,
        "final_answer_str": final_answer_str,
        "steps": steps_str,
        "error": None,
    }