# test_benchmark.py
import random
import math
from typing import Dict, Any, List

from variables import Variable
from physics_formulas import FORMULAS, Formula
from solver import solve_and_calculate, STRING_TO_VARIABLE
from math_engine import parse_expr, Expr

# 1. Автоматический генератор обратного словаря алиасов
# Позволяет тесту имитировать реальный ввод пользователя (передает "m" вместо "mass")
VAR_TO_ALIAS = {}
for alias, var in STRING_TO_VARIABLE.items():
    if var not in VAR_TO_ALIAS:
        VAR_TO_ALIAS[var] = alias

# 2. Моки (заглушки) для функциональных переменных матанализа
FUNC_MOCKS = {
    Variable.POSITION_FUNC: "3*t^2 - 5*t + 2",
    Variable.VELOCITY_FUNC: "6*t - 5",
    Variable.ACCELERATION_FUNC: "6",
    Variable.FORCE_FUNC: "4*x + 1",
    Variable.CURRENT_FUNC: "3*t^2 + 2*t",
    Variable.MAGNETIC_FLUX_FUNC: "sin(2*t)",
}

VAR_BENCHMARK_RANGES: Dict[Variable, tuple] = {
    Variable.MASS: (0.5, 10.0),
    Variable.MASS_1: (1.0, 10.0),
    Variable.MASS_2: (1.0, 10.0),
    Variable.VELOCITY: (2.0, 25.0),
    Variable.INITIAL_VELOCITY: (1.0, 10.0),
    Variable.TIME: (1.0, 15.0),
    Variable.TIME_DELTA: (0.1, 2.0),
    Variable.ACCELERATION: (1.0, 8.0),
    Variable.CENTRIPETAL_ACC: (2.0, 10.0),
    Variable.RADIUS: (0.5, 5.0),
    Variable.ANGULAR_VELOCITY: (1.0, 10.0),
    Variable.FREQUENCY: (10.0, 100.0),
    Variable.PERIOD: (0.1, 5.0),
    Variable.HALF_LIFE: (10.0, 100.0),
    Variable.FORCE: (5.0, 50.0),
    Variable.AMPERE_FORCE: (1.0, 20.0),
    Variable.FRICTION_FORCE: (2.0, 10.0),
    Variable.GRAVITY_FORCE: (10.0, 100.0),
    Variable.ELASTIC_FORCE: (5.0, 30.0),
    Variable.COULOMB_FORCE: (1e-6, 1e-4),
    Variable.STIFFNESS: (20.0, 200.0),
    Variable.ELONGATION: (0.02, 0.2),
    Variable.HEIGHT: (1.0, 20.0),
    Variable.FRICTION_COEFF: (0.1, 0.4),
    Variable.LENGTH: (0.2, 2.0),
    Variable.TORQUE: (2.0, 20.0),
    Variable.DISTANCE: (10.0, 100.0),
    Variable.AREA: (0.01, 1.0),
    Variable.WIRE_AREA: (1e-6, 1e-4),
    Variable.VOLUME: (0.01, 0.5),
    Variable.DENSITY: (800.0, 1200.0),
    Variable.HYDROSTATIC_PRESSURE: (1000.0, 10000.0),
    Variable.ARCHIMEDES_FORCE: (5.0, 50.0),
    Variable.MOLE_AMOUNT: (1.0, 5.0),
    Variable.TEMPERATURE: (280.0, 450.0),
    Variable.PRESSURE: (50000.0, 200000.0),
    Variable.CONCENTRATION: (1e24, 1e25),
    Variable.MOLECULE_KINETIC: (1e-21, 5e-21),
    Variable.SPECIFIC_HEAT: (400.0, 4200.0),
    Variable.FUSION_HEAT: (1e5, 3e5),
    Variable.VAPOR_HEAT: (1e6, 2.5e6),
    Variable.HEAT: (500.0, 5000.0),
    Variable.HEAT_HOT: (1000.0, 2000.0),
    Variable.HEAT_COLD: (200.0, 600.0),
    Variable.TEMP_HOT: (400.0, 600.0),
    Variable.TEMP_COLD: (250.0, 350.0),
    Variable.WORK: (100.0, 2000.0),
    Variable.USEFUL_WORK: (200.0, 800.0),
    Variable.TOTAL_WORK: (1000.0, 1500.0),
    Variable.EFFICIENCY: (0.2, 0.8),
    Variable.CARNOT_EFFICIENCY: (0.3, 0.7),
    Variable.INTERNAL_ENERGY: (300.0, 1500.0),
    Variable.POWER: (50.0, 500.0),
    Variable.VOLTAGE: (10.0, 220.0),
    Variable.CURRENT: (0.5, 10.0),
    Variable.RESISTANCE: (2.0, 50.0),
    Variable.INTERNAL_RESISTANCE: (0.5, 2.0),
    Variable.EMF: (5.0, 24.0),
    Variable.CHARGE: (1e-6, 1e-4),
    Variable.CHARGE_1: (1e-6, 1e-5),
    Variable.CHARGE_2: (2e-6, 1e-5),
    Variable.CAPACITANCE: (1e-6, 1e-4),
    Variable.MAGNETIC_FIELD: (0.1, 2.0),
    Variable.MAGNETIC_FLUX: (0.01, 0.5),
    Variable.FLUX_DELTA: (0.01, 0.1),
    Variable.INDUCTANCE: (0.01, 0.5),
    Variable.WAVELENGTH: (400e-9, 700e-9),
    Variable.OBJECT_DISTANCE: (0.2, 1.0),
    Variable.IMAGE_DISTANCE: (0.2, 1.0),
    Variable.FOCAL_LENGTH: (0.05, 0.15),
    Variable.OPTICAL_POWER: (5.0, 20.0),
    Variable.DIFFRACTION_D: (1e-5, 5e-5),
    Variable.DIFFRACTION_ORDER: (1.0, 3.0),
    Variable.REFRACTIVE_INDEX: (1.2, 1.8),
    Variable.LIGHT_SPEED_MEDIUM: (1.5e8, 2.2e8),
    Variable.WORK_FUNCTION: (2e-19, 5e-19),
    Variable.INITIAL_PARTICLES: (1e6, 1e8),
    Variable.RESISTIVITY: (1e-7, 1e-6),
    Variable.ELECTRIC_FIELD: (100.0, 5000.0),
    Variable.ELECTRON_KINETIC: (1e-19, 8e-19),
    Variable.STOPPING_VOLTAGE: (0.5, 5.0),
    Variable.RED_LIMIT_FREQ: (3e14, 8e14),
    Variable.ACTIVITY: (100.0, 10000.0),
    Variable.DECAY_CONSTANT: (1e-6, 1e-4),
    Variable.HUMIDITY: (0.2, 0.9),
    Variable.VAPOR_PRESSURE: (500.0, 1500.0),
    Variable.SATURATED_VAPOR_PRESSURE: (2000.0, 3500.0),
    Variable.VAPOR_DENSITY: (0.005, 0.015),
    Variable.SATURATED_VAPOR_DENSITY: (0.02, 0.04),
    Variable.COORD_START: (0.0, 1.0),
    Variable.COORD_END: (2.0, 5.0),
    Variable.TIME_START: (0.0, 1.0),
    Variable.TIME_END: (2.0, 5.0),
}


def run_benchmark():
    print("=" * 68)
    print(" 🚀 СТРОГИЙ БЕНЧМАРК (ВКЛЮЧАЯ АНАЛИТИЧЕСКИЙ МАТАНАЛИЗ)")
    print("=" * 68)

    random.seed(42)
    samples_per_formula = 5
    passed_by_formula: Dict[str, int] = {}
    total_by_formula: Dict[str, int] = {}

    for formula_id, formula in FORMULAS.items():
        total_by_formula[formula_id] = samples_per_formula
        passed_by_formula[formula_id] = 0

        for _ in range(samples_per_formula):
            env_sim: Dict[Variable, Any] = {}
            given_inputs: Dict[str, str] = {}

            # Генерация входных данных
            for req in formula.requires:
                alias = VAR_TO_ALIAS.get(req, req.value)
                
                if req in FUNC_MOCKS:
                    # Подстановка функционального выражения
                    expr_str = FUNC_MOCKS[req]
                    env_sim[req] = parse_expr(expr_str)
                    given_inputs[alias] = expr_str
                else:
                    # Случайное число для скалярных величин
                    v_min, v_max = VAR_BENCHMARK_RANGES.get(req, (1.0, 10.0))
                    val = random.uniform(v_min, v_max)

                    if req == Variable.OBJECT_DISTANCE and Variable.FOCAL_LENGTH in formula.requires:
                        val = 0.30
                    elif req == Variable.FOCAL_LENGTH and Variable.OBJECT_DISTANCE in formula.requires:
                        val = 0.10

                    env_sim[req] = val
                    given_inputs[alias] = f"{val:.8e}"

            target_alias = VAR_TO_ALIAS.get(formula.result_variable, formula.result_variable.value)

            try:
                # 1. Считаем эталон
                expected_val = formula.calc(env_sim)
                # 2. Считаем через солвер
                calc_val = solve_and_calculate(given_inputs, target_alias, verbose=False)

                # 3. Сравнение (учитывая объекты Expr)
                if isinstance(expected_val, Expr) and isinstance(calc_val, Expr):
                    test_env = {"t": 2.0, "x": 2.0}
                    e_val = expected_val.eval(test_env)
                    c_val = calc_val.eval(test_env)
                    if math.isclose(e_val, c_val, rel_tol=1e-4, abs_tol=1e-12):
                        passed_by_formula[formula_id] += 1
                elif calc_val is not None and not isinstance(calc_val, Expr):
                    if math.isclose(float(calc_val), float(expected_val), rel_tol=1e-4, abs_tol=1e-12):
                        passed_by_formula[formula_id] += 1
            except Exception:
                pass

    col_name = 42
    print(f"{'Формула':<{col_name}} {'Точность':<10} {'Успешно'}")
    print("-" * 68)

    all_scores = []
    for f_id in FORMULAS.keys():
        n_passed = passed_by_formula.get(f_id, 0)
        n_total = total_by_formula.get(f_id, 5)
        score = n_passed / n_total
        all_scores.append(score)
        f_name = f_id if len(f_id) <= (col_name - 3) else (f_id[:col_name - 4] + "...")
        print(f"{f_name:<{col_name}} {score:<10.2f} {n_passed}/{n_total}")

    mean_acc = sum(all_scores) / len(all_scores) if all_scores else 0.0
    print("=" * 68)
    print(f"{'ИТОГОВАЯ ТОЧНОСТЬ (PHYSICAL ACCURACY):':<{col_name}} {mean_acc * 100:.1f}%")
    print("=" * 68)


if __name__ == "__main__":
    run_benchmark()