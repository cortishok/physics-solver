import math
from dataclasses import dataclass
from typing import Callable
from variables import Variable
import math_engine


@dataclass(frozen=True)
class Formula:
    name: str
    result_variable: Variable
    requires: tuple[Variable, ...]
    calc: Callable[[dict], float | str]
    pretty: str
    is_bridge: bool = False
    forward_only: bool = False  # <--- Вот то, чего не хватало!


def _deg_sin(deg: float) -> float:
    return math.sin(math.radians(deg))


def _deg_cos(deg: float) -> float:
    return math.cos(math.radians(deg))


def _safe_div(a: float, b: float) -> float:
    if abs(b) == 0.0:
        raise ZeroDivisionError("Деление на 0")
    return a / b


def _safe_sqrt(x: float) -> float:
    if x < 0:
        raise ValueError("math domain error: корень из отрицательного числа")
    return math.sqrt(x)


FORMULAS_LIST: list[Formula] = [
    # Связь высоты наклонной плоскости и пройденного вдоль неё пути: S = h / sin(alpha)
    Formula(
        name="Путь по наклонной плоскости через высоту", # <--- Добавил забытое имя
        result_variable=Variable.DISPLACEMENT,
        requires=(Variable.HEIGHT, Variable.ANGLE),
        calc=lambda d: d[Variable.HEIGHT] / math.sin(math.radians(d[Variable.ANGLE])),
        pretty="S = h / sin(α)",
        forward_only=True,
    ),
    # Основное уравнение кинематики с начальной скоростью и ускорением: S = v0*t + a*t^2 / 2
    Formula(
        name="Путь при равноускоренном движении", # <--- Добавил забытое имя
        result_variable=Variable.DISPLACEMENT,
        requires=(Variable.VELOCITY_0, Variable.TIME, Variable.ACCELERATION),
        calc=lambda d: d[Variable.VELOCITY_0] * d[Variable.TIME]
        + 0.5 * d[Variable.ACCELERATION] * (d[Variable.TIME] ** 2),
        pretty="S = v0·t + a·t² / 2",
    ),

    # =========================================================================
    # 1. МАТАНАЛИЗ И АНАЛИТИЧЕСКИЕ ФУНКЦИИ (Задание №2 и интегралы)
    # =========================================================================
    Formula(
        name="Производная координаты x'(t)",
        result_variable=Variable.V_FUNC,
        requires=(Variable.X_FUNC,),
        calc=lambda d: math_engine.symbolic_derivative_str(d[Variable.X_FUNC], "t"),
        pretty="v(t) = x'(t)",
    ),
    Formula(
        name="Производная скорости v'(t)",
        result_variable=Variable.A_FUNC,
        requires=(Variable.V_FUNC,),
        calc=lambda d: math_engine.symbolic_derivative_str(d[Variable.V_FUNC], "t"),
        pretty="a(t) = v'(t)",
    ),
    Formula(
        name="Зависимость силы от времени F(t) = m·a(t)",
        result_variable=Variable.F_FUNC,
        requires=(Variable.MASS, Variable.A_FUNC),
        calc=lambda d: math_engine.scale_function_str(d[Variable.A_FUNC], d[Variable.MASS], "t"),
        pretty="F(t) = m·a(t)",
    ),
    Formula(
        name="Значение скорости v(t) в момент t",
        result_variable=Variable.VELOCITY,
        requires=(Variable.V_FUNC, Variable.TIME),
        calc=lambda d: math_engine.eval_ast(d[Variable.V_FUNC], {"t": d[Variable.TIME]}),
        pretty="v = v(t)",
    ),
    Formula(
        name="Значение ускорения a(t) в момент t",
        result_variable=Variable.ACCELERATION,
        requires=(Variable.A_FUNC, Variable.TIME),
        calc=lambda d: math_engine.eval_ast(d[Variable.A_FUNC], {"t": d[Variable.TIME]}),
        pretty="a = a(t)",
    ),
    Formula(
        name="Интеграл ускорения v = ∫a(t)dt",
        result_variable=Variable.VELOCITY,
        requires=(Variable.A_FUNC, Variable.TIME_START, Variable.TIME_END),
        calc=lambda d: math_engine.definite_integral(
            d[Variable.A_FUNC], d[Variable.TIME_START], d[Variable.TIME_END]
        ),
        pretty="v = ∫a(t)dt",
    ),
    Formula(
        name="Интеграл скорости S = ∫v(t)dt",
        result_variable=Variable.DISPLACEMENT,
        requires=(Variable.V_FUNC, Variable.TIME_START, Variable.TIME_END),
        calc=lambda d: math_engine.definite_integral(
            d[Variable.V_FUNC], d[Variable.TIME_START], d[Variable.TIME_END]
        ),
        pretty="S = ∫v(t)dt",
    ),

    # =========================================================================
    # 2. КИНЕМАТИКА
    # =========================================================================
    Formula(
        name="Скорость при равноускоренном движении",
        result_variable=Variable.VELOCITY,
        requires=(Variable.VELOCITY_0, Variable.ACCELERATION, Variable.TIME),
        calc=lambda d: d[Variable.VELOCITY_0] + d[Variable.ACCELERATION] * d[Variable.TIME],
        pretty="v = v0 + a·t",
    ),
    Formula(
        name="Ускорение через изменение скорости",
        result_variable=Variable.ACCELERATION,
        requires=(Variable.VELOCITY, Variable.VELOCITY_0, Variable.TIME),
        calc=lambda d: _safe_div(d[Variable.VELOCITY] - d[Variable.VELOCITY_0], d[Variable.TIME]),
        pretty="a = (v - v0) / t",
    ),
    Formula(
        name="Перемещение при равноускоренном движении",
        result_variable=Variable.DISPLACEMENT,
        requires=(Variable.VELOCITY_0, Variable.TIME, Variable.ACCELERATION),
        calc=lambda d: d[Variable.VELOCITY_0] * d[Variable.TIME]
        + 0.5 * d[Variable.ACCELERATION] * (d[Variable.TIME] ** 2),
        pretty="S = v0·t + a·t²/2",
    ),
    Formula(
        name="Ускорение через путь и время (без начальной скорости)",
        result_variable=Variable.ACCELERATION,
        requires=(Variable.DISPLACEMENT, Variable.TIME),
        calc=lambda d: _safe_div(2.0 * d[Variable.DISPLACEMENT], d[Variable.TIME] ** 2),
        pretty="a = 2·S / t²",
    ),
    Formula(
        name="Перемещение через среднюю скорость",
        result_variable=Variable.DISPLACEMENT,
        requires=(Variable.VELOCITY_0, Variable.VELOCITY, Variable.TIME),
        calc=lambda d: 0.5 * (d[Variable.VELOCITY_0] + d[Variable.VELOCITY]) * d[Variable.TIME],
        pretty="S = (v0 + v)·t / 2",
    ),
    Formula(
        name="Угловая скорость через частоту",
        result_variable=Variable.OMEGA,
        requires=(Variable.FREQUENCY_ROT,),
        calc=lambda d: 2.0 * math.pi * d[Variable.FREQUENCY_ROT],
        pretty="ω = 2π·ν",
    ),
    Formula(
        name="Максимальная скорость в повороте по трению (Задание №7)",
        result_variable=Variable.VELOCITY_MAX,
        requires=(Variable.FRICTION_COEFF, Variable.G_ACCEL, Variable.RADIUS),
        calc=lambda d: _safe_sqrt(
            d[Variable.FRICTION_COEFF] * d[Variable.G_ACCEL] * d[Variable.RADIUS]
        ),
        pretty="v_max = √(μ·g·R)",
    ),
    Formula(
        name="Скорость в повороте по трению (алиас v)",
        result_variable=Variable.VELOCITY,
        requires=(Variable.FRICTION_COEFF, Variable.G_ACCEL, Variable.RADIUS),
        calc=lambda d: _safe_sqrt(
            d[Variable.FRICTION_COEFF] * d[Variable.G_ACCEL] * d[Variable.RADIUS]
        ),
        pretty="v = √(μ·g·R)",
    ),
    Formula(
        name="Угол наклона мотоциклиста в повороте (Задание №7)",
        result_variable=Variable.ANGLE,
        requires=(Variable.FRICTION_COEFF,),
        calc=lambda d: math.degrees(math.atan(d[Variable.FRICTION_COEFF])),
        pretty="α = arctg(μ)",
    ),

    # =========================================================================
    # 3. ДИНАМИКА, ВЕКТОРНЫЕ ПРОЕКЦИИ, НАКЛОННАЯ ПЛОСКОСТЬ (Задания №1,3,4,5,6,8,9)
    # =========================================================================
    Formula(
        name="Второй закон Ньютона (ускорение)",
        result_variable=Variable.ACCELERATION,
        requires=(Variable.FORCE, Variable.MASS),
        calc=lambda d: _safe_div(d[Variable.FORCE], d[Variable.MASS]),
        pretty="a = F / m",
    ),
    Formula(
        name="Второй закон Ньютона (сила)",
        result_variable=Variable.FORCE,
        requires=(Variable.MASS, Variable.ACCELERATION),
        calc=lambda d: d[Variable.MASS] * d[Variable.ACCELERATION],
        pretty="F = m·a",
    ),
    Formula(
        name="Масса через силу и ускорение",
        result_variable=Variable.MASS,
        requires=(Variable.FORCE, Variable.ACCELERATION),
        calc=lambda d: _safe_div(d[Variable.FORCE], d[Variable.ACCELERATION]),
        pretty="m = F / a",
    ),
    Formula(
        name="Нормальная реакция с силой под углом (Задание №1)",
        result_variable=Variable.NORMAL_FORCE,
        requires=(Variable.MASS, Variable.G_ACCEL, Variable.FORCE, Variable.ANGLE),
        calc=lambda d: d[Variable.MASS] * d[Variable.G_ACCEL]
        - d[Variable.FORCE] * _deg_sin(d[Variable.ANGLE]),
        pretty="N = m·g - F·sin(α)",
    ),
    Formula(
        name="Сила трения скольжения F_тр = μ·N (Задание №1)",
        result_variable=Variable.FORCE_FRICTION,
        requires=(Variable.FRICTION_COEFF, Variable.NORMAL_FORCE),
        calc=lambda d: d[Variable.FRICTION_COEFF] * d[Variable.NORMAL_FORCE],
        pretty="F_тр = μ·N",
    ),
    Formula(
        name="Сила тяги вверх по наклонной плоскости с ускорением (Задания №3, №9)",
        result_variable=Variable.FORCE_PULL,
        requires=(
            Variable.MASS,
            Variable.ACCELERATION,
            Variable.G_ACCEL,
            Variable.ANGLE,
            Variable.FRICTION_COEFF,
        ),
        calc=lambda d: d[Variable.MASS]
        * (
            d[Variable.ACCELERATION]
            + d[Variable.G_ACCEL] * _deg_sin(d[Variable.ANGLE])
            + d[Variable.FRICTION_COEFF] * d[Variable.G_ACCEL] * _deg_cos(d[Variable.ANGLE])
        ),
        pretty="F_тяги = m·(a + g·sin(α) + μ·g·cos(α))",
    ),
    Formula(
        name="Сила F вверх по наклонной плоскости с ускорением (Задание №9)",
        result_variable=Variable.FORCE,
        requires=(
            Variable.MASS,
            Variable.ACCELERATION,
            Variable.G_ACCEL,
            Variable.ANGLE,
            Variable.FRICTION_COEFF,
        ),
        calc=lambda d: d[Variable.MASS]
        * (
            d[Variable.ACCELERATION]
            + d[Variable.G_ACCEL] * _deg_sin(d[Variable.ANGLE])
            + d[Variable.FRICTION_COEFF] * d[Variable.G_ACCEL] * _deg_cos(d[Variable.ANGLE])
        ),
        pretty="F = m·(a + g·sin(α) + μ·g·cos(α))",
    ),
    Formula(
        name="Растяжение пружины по закону Гука x = F_тяги / k (Задание №3)",
        result_variable=Variable.SPRING_X,
        requires=(Variable.FORCE_PULL, Variable.SPRING_K),
        calc=lambda d: _safe_div(d[Variable.FORCE_PULL], d[Variable.SPRING_K]),
        pretty="x = F_тяги / k",
    ),
    Formula(
        name="Вес тела в ускоренно движущемся вверх лифте (Задание №4)",
        result_variable=Variable.WEIGHT,
        requires=(Variable.MASS, Variable.G_ACCEL, Variable.ACCELERATION),
        calc=lambda d: d[Variable.MASS] * (d[Variable.G_ACCEL] + d[Variable.ACCELERATION]),
        pretty="P = m·(g + a)",
    ),
    Formula(
        name="Система 2х2 для связанных грузов: натяжение нити T (Задание №5)",
        result_variable=Variable.TENSION,
        requires=(
            Variable.MASS_1,
            Variable.MASS_2,
            Variable.FORCE,
            Variable.FRICTION_COEFF,
            Variable.G_ACCEL,
        ),
        calc=lambda d: math_engine.solve_linear_2x2(
            d[Variable.MASS_1],
            1.0,
            d[Variable.FORCE] - d[Variable.FRICTION_COEFF] * d[Variable.MASS_1] * d[Variable.G_ACCEL],
            d[Variable.MASS_2],
            -1.0,
            -d[Variable.FRICTION_COEFF] * d[Variable.MASS_2] * d[Variable.G_ACCEL],
        )[1],
        pretty="Система 2×2: {m1·a + T = F - μ·m1·g; m2·a - T = -μ·m2·g} ➔ T = F·m2 / (m1 + m2)",
    ),
    Formula(
        name="Угол наклонной плоскости при равномерном подъёме и спуске (Задание №6)",
        result_variable=Variable.ANGLE,
        requires=(Variable.FORCE_PULL, Variable.MASS, Variable.G_ACCEL),
        calc=lambda d: math.degrees(
            math.asin(_safe_div(d[Variable.FORCE_PULL], 2.0 * d[Variable.MASS] * d[Variable.G_ACCEL]))
        ),
        pretty="α = arcsin(F_тяги / (2·m·g))",
    ),
    Formula(
        name="Скорость после абсолютно неупругого соударения (Задание №8)",
        result_variable=Variable.U_SPEED,
        requires=(Variable.MASS_1, Variable.MASS_2, Variable.VELOCITY_1, Variable.VELOCITY_2),
        calc=lambda d: _safe_div(
            d[Variable.MASS_1] * d[Variable.VELOCITY_1] + d[Variable.MASS_2] * d[Variable.VELOCITY_2],
            d[Variable.MASS_1] + d[Variable.MASS_2],
        ),
        pretty="u = (m1·v1 + m2·v2) / (m1 + m2)",
    ),
    Formula(
        name="Механический импульс тела",
        result_variable=Variable.MOMENTUM,
        requires=(Variable.MASS, Variable.VELOCITY),
        calc=lambda d: d[Variable.MASS] * d[Variable.VELOCITY],
        pretty="p = m·v",
    ),
    Formula(
        name="Масса через плотность и объём",
        result_variable=Variable.MASS,
        requires=(Variable.DENSITY, Variable.VOLUME),
        calc=lambda d: d[Variable.DENSITY] * d[Variable.VOLUME],
        pretty="m = ρ·V",
    ),
    Formula(
        name="Сила Архимеда",
        result_variable=Variable.ARCHIMEDES_FORCE,
        requires=(Variable.DENSITY, Variable.G_ACCEL, Variable.VOLUME),
        calc=lambda d: d[Variable.DENSITY] * d[Variable.G_ACCEL] * d[Variable.VOLUME],
        pretty="F_A = ρ·g·V",
    ),

    # =========================================================================
    # 4. РАБОТА, ЭНЕРГИЯ, МОЩНОСТЬ И МОСТЫ СОХРАНЕНИЯ
    # =========================================================================
    Formula(
        name="Кинетическая энергия",
        result_variable=Variable.KINETIC_ENERGY,
        requires=(Variable.MASS, Variable.VELOCITY),
        calc=lambda d: 0.5 * d[Variable.MASS] * (d[Variable.VELOCITY] ** 2),
        pretty="E_k = m·v² / 2",
    ),
    Formula(
        name="Начальная кинетическая энергия при торможении",
        result_variable=Variable.KINETIC_ENERGY,
        requires=(Variable.MASS, Variable.VELOCITY_0),
        calc=lambda d: 0.5 * d[Variable.MASS] * (d[Variable.VELOCITY_0] ** 2),
        pretty="E_k = m·v0² / 2",
    ),
    Formula(
        name="Потенциальная энергия в поле тяжести",
        result_variable=Variable.POTENTIAL_ENERGY,
        requires=(Variable.MASS, Variable.G_ACCEL, Variable.HEIGHT),
        calc=lambda d: d[Variable.MASS] * d[Variable.G_ACCEL] * d[Variable.HEIGHT],
        pretty="E_p = m·g·h",
    ),
    Formula(
        name="Высота через потенциальную энергию",
        result_variable=Variable.HEIGHT,
        requires=(Variable.POTENTIAL_ENERGY, Variable.MASS, Variable.G_ACCEL),
        calc=lambda d: _safe_div(
            d[Variable.POTENTIAL_ENERGY], d[Variable.MASS] * d[Variable.G_ACCEL]
        ),
        pretty="h = E_p / (m·g)",
    ),
    Formula(
        name="Полная механическая энергия",
        result_variable=Variable.MECHANICAL_ENERGY,
        requires=(Variable.KINETIC_ENERGY, Variable.POTENTIAL_ENERGY),
        calc=lambda d: d[Variable.KINETIC_ENERGY] + d[Variable.POTENTIAL_ENERGY],
        pretty="E_mech = E_k + E_p",
    ),
    Formula(
        name="Механическая работа через силу и путь",
        result_variable=Variable.WORK,
        requires=(Variable.FORCE, Variable.DISPLACEMENT),
        calc=lambda d: abs(d[Variable.FORCE]) * d[Variable.DISPLACEMENT],
        pretty="A = F·S",
    ),
    Formula(
        name="Мост: Работа равна изменению кинетической энергии",
        result_variable=Variable.WORK,
        requires=(Variable.KINETIC_ENERGY,),
        calc=lambda d: d[Variable.KINETIC_ENERGY],
        pretty="A = E_k",
        is_bridge=True,
    ),
    Formula(
        name="Мост: Работа подъёма равна потенциальной энергии",
        result_variable=Variable.WORK,
        requires=(Variable.POTENTIAL_ENERGY,),
        calc=lambda d: d[Variable.POTENTIAL_ENERGY],
        pretty="A = E_p",
        is_bridge=True,
    ),
    Formula(
        name="Мост: Закон сохранения энергии E_p = E_k",
        result_variable=Variable.POTENTIAL_ENERGY,
        requires=(Variable.KINETIC_ENERGY,),
        calc=lambda d: d[Variable.KINETIC_ENERGY],
        pretty="E_p = E_k",
        is_bridge=True,
    ),
    Formula(
        name="Механическая мощность N = A / t",
        result_variable=Variable.POWER_MECH,
        requires=(Variable.WORK, Variable.TIME),
        calc=lambda d: _safe_div(d[Variable.WORK], d[Variable.TIME]),
        pretty="N = A / t",
    ),
    Formula(
        name="Затраченная электрическая мощность через КПД (Тест Подъёмник)",
        result_variable=Variable.POWER_EL,
        requires=(Variable.POWER_MECH, Variable.EFFICIENCY),
        calc=lambda d: _safe_div(d[Variable.POWER_MECH], d[Variable.EFFICIENCY]),
        pretty="P_el = N / η",
    ),

    # =========================================================================
    # 5. ТЕРМОДИНАМИКА И ТЕПЛОВЫЕ МОСТЫ
    # =========================================================================
    Formula(
        name="Количество теплоты при нагревании",
        result_variable=Variable.HEAT,
        requires=(Variable.SPECIFIC_HEAT, Variable.MASS, Variable.DELTA_TEMP),
        calc=lambda d: d[Variable.SPECIFIC_HEAT] * d[Variable.MASS] * d[Variable.DELTA_TEMP],
        pretty="Q = c·m·ΔT",
    ),
    Formula(
        name="Мост: Переход механической работы в теплоту Q = A",
        result_variable=Variable.HEAT,
        requires=(Variable.WORK,),
        calc=lambda d: d[Variable.WORK],
        pretty="Q = A",
        is_bridge=True,
    ),
    Formula(
        name="Мост: Переход джоулева тепла в теплоту Q = Q_joule",
        result_variable=Variable.HEAT,
        requires=(Variable.Q_JOULE,),
        calc=lambda d: d[Variable.Q_JOULE],
        pretty="Q = Q_joule",
        is_bridge=True,
    ),
    Formula(
        name="Полезное тепло с учётом КПД нагревателя",
        result_variable=Variable.HEAT,
        requires=(Variable.Q_JOULE, Variable.EFFICIENCY),
        calc=lambda d: d[Variable.Q_JOULE] * d[Variable.EFFICIENCY],
        pretty="Q = η·Q_joule",
    ),
    Formula(
        name="Мост: Теплота нагревателя Q1 = Q",
        result_variable=Variable.HEAT_HOT,
        requires=(Variable.HEAT,),
        calc=lambda d: d[Variable.HEAT],
        pretty="Q1 = Q",
        is_bridge=True,
    ),
    Formula(
        name="КПД тепловой машины",
        result_variable=Variable.EFFICIENCY,
        requires=(Variable.HEAT_HOT, Variable.HEAT_COLD),
        calc=lambda d: _safe_div(
            d[Variable.HEAT_HOT] - d[Variable.HEAT_COLD], d[Variable.HEAT_HOT]
        ),
        pretty="η = (Q1 - Q2) / Q1",
    ),
    Formula(
        name="Масса испарившейся жидкости m = Q / L (Тест Кипятильник)",
        result_variable=Variable.MASS,
        requires=(Variable.HEAT, Variable.LATENT_VAP),
        calc=lambda d: _safe_div(d[Variable.HEAT], d[Variable.LATENT_VAP]),
        pretty="m = Q / L_vap",
    ),
    Formula(
        name="Нагрев стержня ΔT = Q / (c·m_rod)",
        result_variable=Variable.DELTA_TEMP,
        requires=(Variable.HEAT, Variable.SPECIFIC_HEAT, Variable.MASS_ROD),
        calc=lambda d: _safe_div(
            d[Variable.HEAT], d[Variable.SPECIFIC_HEAT] * d[Variable.MASS_ROD]
        ),
        pretty="ΔT = Q / (c·m_rod)",
    ),

    # =========================================================================
    # 6. ЭЛЕКТРОДИНАМИКА И МАГНЕТИЗМ
    # =========================================================================
    Formula(
        name="Закон Ома для участка цепи I = U / R",
        result_variable=Variable.CURRENT,
        requires=(Variable.VOLTAGE, Variable.RESISTANCE),
        calc=lambda d: _safe_div(d[Variable.VOLTAGE], d[Variable.RESISTANCE]),
        pretty="I = U / R",
    ),
    Formula(
        name="Сила тока через электрическую мощность I = P_el / U",
        result_variable=Variable.CURRENT,
        requires=(Variable.POWER_EL, Variable.VOLTAGE),
        calc=lambda d: _safe_div(d[Variable.POWER_EL], d[Variable.VOLTAGE]),
        pretty="I = P_el / U",
    ),
    Formula(
        name="Напряжение по закону Ома U = I·R",
        result_variable=Variable.VOLTAGE,
        requires=(Variable.CURRENT, Variable.RESISTANCE),
        calc=lambda d: d[Variable.CURRENT] * d[Variable.RESISTANCE],
        pretty="U = I·R",
    ),
    Formula(
        name="Закон Джоуля–Ленца Q = I²·R·t",
        result_variable=Variable.Q_JOULE,
        requires=(Variable.CURRENT, Variable.RESISTANCE, Variable.TIME),
        calc=lambda d: (d[Variable.CURRENT] ** 2) * d[Variable.RESISTANCE] * d[Variable.TIME],
        pretty="Q_joule = I²·R·t",
    ),
    Formula(
        name="ЭДС индукции в движущемся проводнике E_ind = B·v·l",
        result_variable=Variable.EMF_IND,
        requires=(Variable.MAGNETIC_B, Variable.VELOCITY, Variable.WIRE_LENGTH),
        calc=lambda d: d[Variable.MAGNETIC_B] * d[Variable.VELOCITY] * d[Variable.WIRE_LENGTH],
        pretty="E_ind = B·v·l",
    ),
    Formula(
        name="Магнитный поток Φ = B·S",
        result_variable=Variable.MAGNETIC_FLUX,
        requires=(Variable.MAGNETIC_B, Variable.DISPLACEMENT),
        calc=lambda d: d[Variable.MAGNETIC_B] * d[Variable.DISPLACEMENT],
        pretty="Φ = B·S",
    ),
    Formula(
        name="Амплитуда ЭДС вращающейся рамки E_ind = Φ·ω",
        result_variable=Variable.EMF_IND,
        requires=(Variable.MAGNETIC_FLUX, Variable.OMEGA),
        calc=lambda d: d[Variable.MAGNETIC_FLUX] * d[Variable.OMEGA],
        pretty="E_ind = Φ·ω",
    ),
    Formula(
        name="Мост: Напряжение равно ЭДС индукции U = E_ind",
        result_variable=Variable.VOLTAGE,
        requires=(Variable.EMF_IND,),
        calc=lambda d: d[Variable.EMF_IND],
        pretty="U = E_ind",
        is_bridge=True,
    ),
    Formula(
        name="Скорость частицы в циклотроне v = q·B·R / m",
        result_variable=Variable.VELOCITY,
        requires=(Variable.CHARGE, Variable.MAGNETIC_B, Variable.RADIUS, Variable.MASS),
        calc=lambda d: _safe_div(
            d[Variable.CHARGE] * d[Variable.MAGNETIC_B] * d[Variable.RADIUS], d[Variable.MASS]
        ),
        pretty="v = q·B·R / m",
    ),
    Formula(
        name="Формула Томсона T = 2π·√(L·C)",
        result_variable=Variable.THOMSON_PERIOD,
        requires=(Variable.INDUCTANCE, Variable.CAPACITANCE),
        calc=lambda d: 2.0 * math.pi * _safe_sqrt(d[Variable.INDUCTANCE] * d[Variable.CAPACITANCE]),
        pretty="T = 2π·√(L·C)",
    ),

    # =========================================================================
    # 7. КВАНТОВАЯ И ЯДЕРНАЯ ФИЗИКА
    # =========================================================================
    Formula(
        name="Энергия фотона E_ph = h·ν",
        result_variable=Variable.PHOTON_ENERGY,
        requires=(Variable.PLANCK, Variable.FREQ_LIGHT),
        calc=lambda d: d[Variable.PLANCK] * d[Variable.FREQ_LIGHT],
        pretty="E_ph = h·ν",
    ),
    Formula(
        name="Уравнение Эйнштейна для фотоэффекта E_k = E_ph - A_вых",
        result_variable=Variable.KINETIC_ENERGY,
        requires=(Variable.PHOTON_ENERGY, Variable.WORK_FUNCTION),
        calc=lambda d: d[Variable.PHOTON_ENERGY] - d[Variable.WORK_FUNCTION],
        pretty="E_k = E_ph - A_вых",
    ),
    Formula(
        name="Запирающее напряжение U_stop = E_k / e",
        result_variable=Variable.STOPPING_VOLTAGE,
        requires=(Variable.KINETIC_ENERGY, Variable.ELEM_CHARGE),
        calc=lambda d: _safe_div(d[Variable.KINETIC_ENERGY], d[Variable.ELEM_CHARGE]),
        pretty="U_stop = E_k / e",
    ),
    Formula(
        name="Мост: Напряжение цепи от фототока U = U_stop",
        result_variable=Variable.VOLTAGE,
        requires=(Variable.STOPPING_VOLTAGE,),
        calc=lambda d: d[Variable.STOPPING_VOLTAGE],
        pretty="U = U_stop",
        is_bridge=True,
    ),
    Formula(
        name="Число излучённых фотонов N = Q / E_ph",
        result_variable=Variable.PARTICLES_COUNT,
        requires=(Variable.HEAT, Variable.PHOTON_ENERGY),
        calc=lambda d: _safe_div(d[Variable.HEAT], d[Variable.PHOTON_ENERGY]),
        pretty="N = Q / E_ph",
    ),
    Formula(
        name="Суммарный импульс фотонов p_photons = N·E_ph / c",
        result_variable=Variable.MOMENTUM_PHOTONS,
        requires=(Variable.PARTICLES_COUNT, Variable.PHOTON_ENERGY, Variable.SPEED_OF_LIGHT),
        calc=lambda d: _safe_div(
            d[Variable.PARTICLES_COUNT] * d[Variable.PHOTON_ENERGY], d[Variable.SPEED_OF_LIGHT]
        ),
        pretty="p_photons = N·E_ph / c",
    ),
    Formula(
        name="Активность радиоактивного распада A = λ·N",
        result_variable=Variable.ACTIVITY,
        requires=(Variable.DECAY_CONSTANT, Variable.PARTICLES_COUNT),
        calc=lambda d: d[Variable.DECAY_CONSTANT] * d[Variable.PARTICLES_COUNT],
        pretty="A_act = λ·N",
    ),
]
