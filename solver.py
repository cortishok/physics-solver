# solver.py
from collections import deque
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from variables import Variable
from physics_formulas import FORMULAS, Formula
from units import parse_any_input, UNITS
from math_engine import Expr


# Таблица однозначного сопоставления строкового ввода с физическими сущностями
STRING_TO_VARIABLE: Dict[str, Variable] = {
    # Кинематика и механика
    "s": Variable.DISTANCE,
    "S": Variable.DISTANCE,
    "h": Variable.HEIGHT,
    "H": Variable.HEIGHT,
    "l": Variable.LENGTH,
    "L": Variable.LENGTH,
    "r": Variable.RADIUS,
    "R_geom": Variable.RADIUS,
    "v": Variable.VELOCITY,
    "V_speed": Variable.VELOCITY,
    "v0": Variable.INITIAL_VELOCITY,
    "a": Variable.ACCELERATION,
    "a_n": Variable.CENTRIPETAL_ACC,
    "t": Variable.TIME,
    "dt": Variable.TIME_DELTA,
    "m": Variable.MASS,
    "F": Variable.FORCE,
    "F_tr": Variable.FRICTION_FORCE,
    "F_тяж": Variable.GRAVITY_FORCE,
    "F_упр": Variable.ELASTIC_FORCE,
    "k": Variable.STIFFNESS,
    "dx": Variable.ELONGATION,
    "x_elong": Variable.ELONGATION,
    "mu": Variable.FRICTION_COEFF,
    "M_torque": Variable.TORQUE,
    "omega": Variable.ANGULAR_VELOCITY,
    "T_period": Variable.PERIOD,
    "nu_freq": Variable.FREQUENCY,

    # Строгое разделение: p (импульс) vs P (давление)[cite: 1]
    "p": Variable.MOMENTUM,
    "p_impulse": Variable.MOMENTUM,
    "P": Variable.PRESSURE,
    "P_pressure": Variable.PRESSURE,

    # Энергия, работа и мощность
    # 'A' — строго механическая работа, исключая коллизии[cite: 1, 5]
    "A": Variable.WORK,
    "А": Variable.WORK,
    "A_work": Variable.WORK,
    "A_useful": Variable.USEFUL_WORK,
    "A_total": Variable.TOTAL_WORK,
    "E_k": Variable.KINETIC_ENERGY,
    "E_p": Variable.POTENTIAL_ENERGY,
    "N": Variable.POWER,
    "eta": Variable.EFFICIENCY,

    # Работа выхода (строго через индекс)[cite: 5]
    "A_vyh": Variable.WORK_FUNCTION,
    "Aвых": Variable.WORK_FUNCTION,
    "A_вых": Variable.WORK_FUNCTION,

    # МКТ и термодинамика
    "T": Variable.TEMPERATURE,
    "T1": Variable.TEMP_HOT,
    "T2": Variable.TEMP_COLD,
    "V": Variable.VOLUME,
    "rho": Variable.DENSITY,
    "nu": Variable.MOLE_AMOUNT,
    "U": Variable.INTERNAL_ENERGY,
    "c": Variable.SPECIFIC_HEAT,
    "lambda_fusion": Variable.FUSION_HEAT,
    "L_vapor": Variable.VAPOR_HEAT,
    "n_conc": Variable.CONCENTRATION,
    "E_mol": Variable.MOLECULE_KINETIC,
    "phi_hum": Variable.HUMIDITY,
    "P_sat": Variable.SATURATED_VAPOR_PRESSURE,

    # Строгое разделение: q (заряд) vs Q (теплота)[cite: 1]
    "q": Variable.CHARGE,
    "q1": Variable.CHARGE_1,
    "q2": Variable.CHARGE_2,
    "Q": Variable.HEAT,
    "Q1": Variable.HEAT_HOT,
    "Q2": Variable.HEAT_COLD,

    # Электродинамика и магнетизм
    "I": Variable.CURRENT,
    "U_volt": Variable.VOLTAGE,
    "R": Variable.RESISTANCE,
    "r_int": Variable.INTERNAL_RESISTANCE,
    "r_internal": Variable.INTERNAL_RESISTANCE,
    "E_emf": Variable.EMF,
    "eps": Variable.EMF,
    "C": Variable.CAPACITANCE,
    "E_field": Variable.ELECTRIC_FIELD,
    "rho_el": Variable.RESISTIVITY,
    "S_wire": Variable.WIRE_AREA,
    "B": Variable.MAGNETIC_FIELD,
    "Phi": Variable.MAGNETIC_FLUX,
    "dPhi": Variable.FLUX_DELTA,
    "L_ind": Variable.INDUCTANCE,
    "F_a": Variable.AMPERE_FORCE,
    "F_l": Variable.LORENTZ_FORCE,
    "F_c": Variable.COULOMB_FORCE,

    # Оптика, кванты и ядра
    "n": Variable.REFRACTIVE_INDEX,
    "lambda": Variable.WAVELENGTH,
    "lambda_wave": Variable.WAVELENGTH,
    "d_opt": Variable.OBJECT_DISTANCE,
    "f_opt": Variable.IMAGE_DISTANCE,
    "F_opt": Variable.FOCAL_LENGTH,
    "D_opt": Variable.OPTICAL_POWER,
    "d_grating": Variable.DIFFRACTION_D,
    "k_order": Variable.DIFFRACTION_ORDER,
    "E_photon": Variable.PHOTON_ENERGY,
    "U_stop": Variable.STOPPING_VOLTAGE,
    "nu_red": Variable.RED_LIMIT_FREQ,
    "T_half": Variable.HALF_LIFE,
    "N0": Variable.INITIAL_PARTICLES,
    "A_act": Variable.ACTIVITY,

    # Функциональные переменные матанализа
    "x(t)": Variable.POSITION_FUNC,
    "x_t": Variable.POSITION_FUNC,
    "v(t)": Variable.VELOCITY_FUNC,
    "v_t": Variable.VELOCITY_FUNC,
    "a(t)": Variable.ACCELERATION_FUNC,
    "a_t": Variable.ACCELERATION_FUNC,
    "F(x)": Variable.FORCE_FUNC,
    "F_x": Variable.FORCE_FUNC,
    "i(t)": Variable.CURRENT_FUNC,
    "I(t)": Variable.CURRENT_FUNC,
    "Phi(t)": Variable.MAGNETIC_FLUX_FUNC,
    "phi(t)": Variable.MAGNETIC_FLUX_FUNC,

    # Пределы интегрирования
    "x1": Variable.COORD_START,
    "x_start": Variable.COORD_START,
    "x2": Variable.COORD_END,
    "x_end": Variable.COORD_END,
    "t1": Variable.TIME_START,
    "t_start": Variable.TIME_START,
    "t2": Variable.TIME_END,
    "t_end": Variable.TIME_END,
    "m1": Variable.MASS_1,
    "m2": Variable.MASS_2,
   
    # Недостающие переменные для тестов
    "S_area": Variable.AREA,
    "F_grav": Variable.GRAVITATIONAL_FORCE,
    "v_cosmic_1": Variable.FIRST_COSMIC_VEL,
    "E_mech": Variable.MECHANICAL_ENERGY,
    "F_arch": Variable.ARCHIMEDES_FORCE,
    "P_hydro": Variable.HYDROSTATIC_PRESSURE,
    "eta_carnot": Variable.CARNOT_EFFICIENCY,
    "I_sc": Variable.SHORT_CIRCUIT_CURRENT,
    "W_el": Variable.ELECTRIC_ENERGY,
    "P_el": Variable.ELECTRIC_POWER,
    "Q_joule": Variable.JOULE_HEAT,
    "E_ind": Variable.INDUCED_EMF,
    "W_mag": Variable.MAGNETIC_ENERGY,
    "T_thomson": Variable.THOMSON_PERIOD,
    "v_wave": Variable.WAVE_SPEED,
    "Gamma": Variable.MAGNIFICATION,
    "v_light": Variable.LIGHT_SPEED_MEDIUM,
    "p_photon": Variable.PHOTON_MOMENTUM,
    "E_k_el": Variable.ELECTRON_KINETIC,
    "N_particles": Variable.PARTICLE_COUNT,
    "E_rest": Variable.REST_ENERGY,
    "delta_m": Variable.MASS_DEFECT,
    "delta_E": Variable.ENERGY_DEFECT,
    "p_vapor": Variable.VAPOR_PRESSURE,
    "rho_vapor": Variable.VAPOR_DENSITY,
    "rho_sat": Variable.SATURATED_VAPOR_DENSITY,


}


def resolve_variable(name: str) -> Optional[Variable]:
    """Разрешает строковое имя в сущность Variable с сохранением регистра."""
    cleaned = name.strip()
    return STRING_TO_VARIABLE.get(cleaned)


def get_display_name(var: Variable) -> str:
    """Возвращает каноническое строковое имя переменной для вывода ответа."""
    for str_key, var_val in STRING_TO_VARIABLE.items():
        if var_val == var:
            return str_key
    return var.value


def format_physical_value(val: Union[float, Expr], unit: str) -> str:
    """Форматирует числовое значение или символьное выражение для консоли."""
    if isinstance(val, Expr):
        return f"{val} [{unit}]" if unit else str(val)
    if isinstance(val, (int, float)):
        if abs(val) >= 1e5 or (0 < abs(val) < 1e-3):
            return f"{val:.4e} {unit}".strip()
        if float(val).is_integer():
            return f"{int(val)} {unit}".strip()
        return f"{val:.4g} {unit}".strip()
    return f"{val} {unit}".strip()


def build_solution_plan(available_vars: List[Variable], target_var: Variable) -> Optional[List[Formula]]:
    """
    Планировщик на основе обхода в ширину (BFS).
    Ищет кратчайшую последовательность формул от известных величин к целевой.
    """
    if target_var in available_vars:
        return []

    # Состояние очереди: (множество_известных_переменных, цепочка_формул)
    queue: deque[Tuple[Set[Variable], List[Formula]]] = deque([
        (set(available_vars), [])
    ])
    
    # Множество посещенных наборов переменных для защиты от зацикливания
    visited_states: Set[frozenset] = {frozenset(available_vars)}

    all_formulas = list(FORMULAS.values())

    while queue:
        current_vars, plan = queue.popleft()

        for formula in all_formulas:
            # Проверяем, можно ли применить данную формулу
            if all(req in current_vars for req in formula.requires):
                res_var = formula.result_variable

                # Если формула дает целевую переменную — решение найдено
                if res_var == target_var:
                    return plan + [formula]

                # Если формула порождает новую промежуточную переменную
                if res_var not in current_vars:
                    new_vars = current_vars | {res_var}
                    frozen_new = frozenset(new_vars)

                    if frozen_new not in visited_states:
                        visited_states.add(frozen_new)
                        queue.append((new_vars, plan + [formula]))

    return None


def solve_and_calculate(given_raw: Dict[str, str], target_raw: str) -> Dict[str, Any]:
    """
    Главная точка входа: парсит входные данные, строит план,
    рассчитывает значения и возвращает структурированный ответ (JSON-подобный словарь)
    для интеграции с графическим интерфейсом.
    """
    response = {
        "target": target_raw,
        "result": None,
        "final_answer_str": None,
        "steps": [],
        "error": None
    }

    target_var = resolve_variable(target_raw)
    if not target_var:
        response["error"] = f"Целевая переменная '{target_raw}' не распознана."
        return response

    # Формируем рабочее окружение с переводом в СИ
    env: Dict[Variable, Any] = {}
    for raw_k, raw_v in given_raw.items():
        var_enum = resolve_variable(raw_k)
        if not var_enum:
            continue
        try:
            val_si, _ = parse_any_input(raw_v)
            env[var_enum] = val_si
        except Exception as e:
            response["error"] = f"Ошибка разбора величины '{raw_k}': {e}"
            return response

    # Поиск плана решения
    plan = build_solution_plan(list(env.keys()), target_var)
    if plan is None:
        response["error"] = "Не удалось найти решение: цепочка формул не замкнулась."
        return response

    # Выполнение формул из плана
    for idx, formula in enumerate(plan, 1):
        try:
            res_val = formula.calc(env)
            env[formula.result_variable] = res_val
            unit_str = UNITS.get(formula.result_variable, "")
            
            val_repr = format_physical_value(res_val, unit_str)
            
            # Сохраняем шаг в виде словаря вместо принта
            response["steps"].append({
                "step": idx,
                "formula": formula.pretty,
                "result_str": val_repr,
                "result_var": get_display_name(formula.result_variable)
            })
        except Exception as e:
            response["error"] = f"Ошибка на шаге {idx} ({formula.id}): {e}"
            return response

    final_result = env.get(target_var)
    response["result"] = final_result
    
    if final_result is not None:
        target_unit = UNITS.get(target_var, "")
        response["final_answer_str"] = format_physical_value(final_result, target_unit)

    return response