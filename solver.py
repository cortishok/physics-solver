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

MAGNETIC_FLUX_CONTEXT_KEYS = {
    "Phi", "MAGNETIC_FLUX", "freq_rot", "omega",
}

# Переменные-функции матанализа (значения — строки-выражения, а не числа)
FUNCTION_VARS = {
    Variable.X_FUNC,
    Variable.V_FUNC,
    Variable.A_FUNC,
    Variable.F_FUNC,
    Variable.CURRENT_FUNC,
    Variable.MAGNETIC_FLUX_FUNC,
}

# Ключи для контекстной маршрутизации цели (п.4 ревью): электричество vs механика
MECHANICAL_CONTEXT_KEYS = {
    "m", "v", "v0", "a", "t", "F", "h", "S", "p", "E_k", "E_p",
    "N_power", "A", "mu", "k", "x_spring", "P_weight", "T_tension", "N_norm",
}
ELASTIC_CONTEXT_KEYS = {"k", "x_spring"}
CURRENT_CONTEXT_KEYS = {"I", "i(t)", "q", "Q_joule", "R", "U"}


def _has_implicit_velocity_direction(state: dict, var: Variable) -> bool | None:
    """
    Возвращает знак скорости из кинематического контекста Дано,
    если он однозначно следует из заданных проекций (v0 / v). Иначе None.
    Нужно для обратного хода формул с v^2 (E_k, p): там теряется знак.
    """
    for src_var in (Variable.VELOCITY_0, Variable.VELOCITY):
        if src_var in state and isinstance(state[src_var], (int, float)) and src_var != var:
            if state[src_var] < 0:
                return False
    return None


def get_display_name(var: Variable) -> str:
    return VARIABLE_DISPLAY_NAMES.get(var, var.value)


def _format_val(val) -> str:
    if isinstance(val, str):
        return val
    if val == 0.0:
        return "0"
    if abs(val) >= 1e5 or (0 < abs(val) < 1e-3):
        return f"{val:.4e}"
    if abs(val - round(val)) < 1e-7:
        return str(int(round(val)))
    return f"{val:.4f}".rstrip("0").rstrip(".")


def _resolve_variable_name(k_str: str, raw_val: str, all_keys: set[str]) -> Variable | None:
    """Разрешение коллизий имён ('R': Радиус vs Сопротивление, 'S': Путь vs Площадь, 'L': Теплота vs Индуктивность)."""
    fallbacks = {
        "q_charge": Variable.CHARGE,
        "nu_freq": Variable.FREQ_LIGHT,
        "t_tension": Variable.TENSION,
        "s_area": Variable.AREA,
        "mass_rod": Variable.MASS_ROD,
    }
    k_lower = k_str.lower()
    if k_lower in fallbacks:
        return fallbacks[k_lower]

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

    if k_str == "S":
        val_s = str(raw_val).strip()
        parts = val_s.split()
        unit_part = parts[-1] if len(parts) > 1 else ""
        if unit_part in ("м2", "м²", "см2", "см²", "мм2", "мм²"):
            return Variable.AREA
        if (all_keys & MAGNETIC_FLUX_CONTEXT_KEYS) and not (all_keys & {"v", "v0", "a", "t", "F", "h"}):
            return Variable.AREA
        return Variable.DISPLACEMENT

    if k_str == "L":
        if all_keys & {"C", "T_thomson", "T_period", "I"}:
            return Variable.INDUCTANCE
        return Variable.LATENT_VAP

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

        is_func_var = var_enum in FUNCTION_VARS
        try:
            parsed_val = parse_value_with_unit(raw_v, is_func=is_func_var)
            if is_func_var:
                math_engine.normalize_expr(str(parsed_val))
            known_values[var_enum] = parsed_val
            user_vars.add(var_enum)
        except Exception as exc:
            return {"error": str(exc)}

    # --- ПРОВЕРКА ФИЗИЧЕСКОГО ОДЗ НА ВХОДЕ (после заполнения known_values) ---
    if Variable.EFFICIENCY in user_vars:
        eta_val = known_values[Variable.EFFICIENCY]
        if isinstance(eta_val, (int, float)):
            if 1.0 < eta_val <= 100.0:
                known_values[Variable.EFFICIENCY] = eta_val / 100.0
            elif eta_val <= 0 or eta_val > 100.0:
                return {"error": f"Физическая ошибка: КПД не может быть равен {eta_val}."}

    # Углы: синусы/косинсы в формулах решают задачу только при alpha ∈ (-90°; 90°)
    for angle_key, angle_label in ((Variable.ANGLE, "Угол наклона (alpha)"),):
        if angle_key in user_vars and isinstance(known_values[angle_key], (int, float)):
            if abs(known_values[angle_key]) >= 90.0:
                return {
                    "error": f"Физическая ошибка в Дано: {angle_label} должен лежать в пределах (-90°; 90°), получено {known_values[angle_key]}°."
                }

    # Абсолютная температура не может быть отрицательной (п.6 ревью)
    if Variable.TEMP in user_vars and isinstance(known_values[Variable.TEMP], (int, float)):
        if known_values[Variable.TEMP] < 0:
            return {"error": "Физическая ошибка в Дано: абсолютная температура T не может быть меньше 0 К."}

    strictly_positive = {
        Variable.MASS: "Масса (m)",
        Variable.MASS_1: "Масса (m1)",
        Variable.MASS_2: "Масса (m2)",
        Variable.MASS_ROD: "Масса стержня (m_rod)",
        Variable.WAVELENGTH: "Длина волны",
        Variable.FREQ_LIGHT: "Частота излучения",
        Variable.RADIUS: "Радиус",
        Variable.AREA: "Площадь (S_area)",
        Variable.VOLUME: "Объём (V)",
        Variable.TEMP: "Абсолютная температура (T)",
    }
    for var_key, var_label in strictly_positive.items():
        if var_key in user_vars and isinstance(known_values[var_key], (int, float)):
            if known_values[var_key] <= 0:
                return {"error": f"Физическая ошибка в Дано: {var_label} должна быть больше нуля."}

    if Variable.TIME in user_vars and isinstance(known_values[Variable.TIME], (int, float)):
        if known_values[Variable.TIME] < 0:
            return {"error": "Физическая ошибка в Дано: время (t) не может быть отрицательным."}

    # Контекстная маршрутизация цели
    if target_var == Variable.MOMENTUM and Variable.FREQ_LIGHT in user_vars:
        target_var = Variable.MOMENTUM_PHOTONS

    # Импульс тока: в чисто электрической задаче "I" (импульс) — это заряд q = I·t (п.4 ревью)
    if target_var == Variable.MOMENTUM:
        given_keys = {get_display_name(v) for v in user_vars} | set(all_input_keys)
        if given_keys & CURRENT_CONTEXT_KEYS and not (given_keys & MECHANICAL_CONTEXT_KEYS):
            target_var = Variable.CHARGE

    if (
        target_var == Variable.FORCE
        and Variable.X_FUNC in user_vars
        and Variable.TIME not in user_vars
    ):
        target_var = Variable.F_FUNC

    if target_var == Variable.PERIOD and (Variable.INDUCTANCE in user_vars or Variable.CAPACITANCE in user_vars):
        target_var = Variable.THOMSON_PERIOD

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
            if formula.pretty == "E_k = m·v0² / 2" and known_values.get(Variable.VELOCITY_0) == 0.0:
                continue

            # Физическое ограничение 2: формула a = 2S/t^2 применима только если нет ненулевой v0
            if formula.pretty == "a = 2·S / t²" and Variable.VELOCITY_0 in user_vars and known_values.get(Variable.VELOCITY_0) != 0.0:
                continue

            # Физическое ограничение 3: интеграл ускорения без v0 применяется только если v0 не задана (или равна 0)
            if formula.pretty == "v = ∫a(t)dt" and Variable.VELOCITY_0 in user_vars and known_values.get(Variable.VELOCITY_0) != 0.0:
                continue

            # Физическое ограничение 4: фантомная наклонная плоскость мотоциклиста
            if formula.pretty == "α = arctg(μ)" and target_var != Variable.ANGLE:
                continue

            # Физическое ограничение 5: Изоляция квантового моста U = U_stop
            if formula.pretty == "U = U_stop":
                quantum_context = {Variable.WORK_FUNCTION, Variable.PHOTON_ENERGY, Variable.FREQ_LIGHT, Variable.WAVELENGTH}
                if not any(q in user_vars for q in quantum_context) and target_var not in quantum_context:
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

            # Обратный алгебраический шаг (с учётом флагов forward_only и is_symbolic)
            elif (
                not formula.is_bridge
                and not getattr(formula, "forward_only", False)
                and not getattr(formula, "is_symbolic", False)
                and res_var in known_vars
            ):
                missing = [req for req in formula.requires if req not in known_vars]
                if len(missing) == 1:
                    miss_var = missing[0]
                    if (
                        miss_var not in known_vars
                        and miss_var not in updates_in_layer
                        and miss_var not in FUNCTION_VARS
                    ):
                        # Запрет круговой тавтологии E_k(v_0) -> v
                        if formula.result_variable == Variable.KINETIC_ENERGY and Variable.VELOCITY in formula.requires:
                            ek_source = derivation.get(Variable.KINETIC_ENERGY)
                            if ek_source and Variable.VELOCITY_0 in ek_source[1].requires:
                                continue

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
            else:
                known_sub = {r: state[r] for r in formula.requires if r != out_var}
                expected_y = state[formula.result_variable]
                val = math_engine.solve_implicit_for_var(
                    formula.calc, known_sub, out_var, expected_y
                )

            # --- ФИЗИЧЕСКИЙ ФИЛЬТР ---
            if isinstance(val, (int, float)):
                if out_var == Variable.TIME and val < 0:
                    return {"error": f"Физическое противоречие: получено отрицательное время t = {val:.4g} с."}

            state[out_var] = val
            unit = VARIABLE_UNITS.get(out_var, "")
            val_str = f"{_format_val(val)} {unit}".strip()

            if mode == "direct":
                steps_str.append(f"{idx}. {formula.pretty} ➔ {val_str}")
            else:
                steps_str.append(f"{idx}. Из [{formula.pretty}] выражаем {get_display_name(out_var)} ➔ {val_str}")

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
