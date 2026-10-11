# units.py
import math
import re
from typing import Tuple
from variables import Variable


class UnknownUnitError(ValueError):
    """Исключение, выбрасываемое при попытке разобрать неподдерживаемую единицу измерения."""
    pass


# Базовые единицы для отображения в солвере
UNITS = {
    Variable.MASS_1: "кг",
    Variable.MASS_2: "кг",
    Variable.DISTANCE: "м",
    Variable.VELOCITY: "м/с",
    Variable.INITIAL_VELOCITY: "м/с",
    Variable.ACCELERATION: "м/с²",
    Variable.CENTRIPETAL_ACC: "м/с²",
    Variable.TIME: "с",
    Variable.TIME_DELTA: "с",
    Variable.MASS: "кг",
    Variable.FORCE: "Н",
    Variable.FRICTION_FORCE: "Н",
    Variable.GRAVITY_FORCE: "Н",
    Variable.ELASTIC_FORCE: "Н",
    Variable.AMPERE_FORCE: "Н",
    Variable.LORENTZ_FORCE: "Н",
    Variable.COULOMB_FORCE: "Н",
    Variable.PRESSURE: "Па",
    Variable.HYDROSTATIC_PRESSURE: "Па",
    Variable.TEMPERATURE: "К",
    Variable.TEMP_HOT: "К",
    Variable.TEMP_COLD: "К",
    Variable.WORK: "Дж",
    Variable.USEFUL_WORK: "Дж",
    Variable.TOTAL_WORK: "Дж",
    Variable.HEAT: "Дж",
    Variable.HEAT_HOT: "Дж",
    Variable.HEAT_COLD: "Дж",
    Variable.KINETIC_ENERGY: "Дж",
    Variable.POTENTIAL_ENERGY: "Дж",
    Variable.INTERNAL_ENERGY: "Дж",
    Variable.ELECTRIC_ENERGY: "Дж",
    Variable.MAGNETIC_ENERGY: "Дж",
    Variable.PHOTON_ENERGY: "Дж",
    Variable.ELECTRON_KINETIC: "Дж",
    Variable.POWER: "Вт",
    Variable.CURRENT: "А",
    Variable.VOLTAGE: "В",
    Variable.EMF: "В",
    Variable.STOPPING_VOLTAGE: "В",
    Variable.RESISTANCE: "Ом",
    Variable.INTERNAL_RESISTANCE: "Ом",
    Variable.CHARGE: "Кл",
    Variable.CAPACITANCE: "Ф",
    Variable.MAGNETIC_FIELD: "Тл",
    Variable.MAGNETIC_FLUX: "Вб",
    Variable.FLUX_DELTA: "Вб",
    Variable.INDUCTANCE: "Гн",
    Variable.FREQUENCY: "Гц",
    Variable.RED_LIMIT_FREQ: "Гц",
    Variable.PERIOD: "с",
    Variable.HALF_LIFE: "с",
    Variable.WAVELENGTH: "м",
    Variable.LENGTH: "м",
    Variable.RADIUS: "м",
    Variable.HEIGHT: "м",
    Variable.OBJECT_DISTANCE: "м",
    Variable.IMAGE_DISTANCE: "м",
    Variable.FOCAL_LENGTH: "м",
    Variable.OPTICAL_POWER: "дптр",
    Variable.AREA: "м²",
    Variable.WIRE_AREA: "м²",
    Variable.VOLUME: "м³",
    Variable.DENSITY: "кг/м³",
    Variable.EFFICIENCY: "%",
    Variable.CARNOT_EFFICIENCY: "%",
    Variable.HUMIDITY: "%",
    Variable.VAPOR_PRESSURE: "Па",
    Variable.SATURATED_VAPOR_PRESSURE: "Па",
    Variable.VAPOR_DENSITY: "кг/м³",
    Variable.SATURATED_VAPOR_DENSITY: "кг/м³",
    Variable.ACTIVITY: "Бк",
    Variable.DECAY_CONSTANT: "с⁻¹",
    Variable.RESISTIVITY: "Ом·м",
}

# Известные базовые и составные единицы с множителями перевода в СИ
BASE_UNITS = {
    # Безразмерные / служебные
    "": (1.0, ""),
    "си": (1.0, ""),
    "%": (0.01, "%"),
    
    # Расстояние
    "м": (1.0, "м"),
    "m": (1.0, "м"),
    
    # Масса
    "г": (1e-3, "кг"),
    "g": (1e-3, "кг"),
    "кг": (1.0, "кг"),
    "kg": (1.0, "кг"),
    "т": (1e3, "кг"),
    "t": (1e3, "кг"),

    # Время
    "с": (1.0, "с"),
    "c": (1.0, "с"),  # русская с / латинская c
    "s": (1.0, "с"),
    "сек": (1.0, "с"),
    "мин": (60.0, "с"),
    "min": (60.0, "с"),
    "ч": (3600.0, "с"),
    "h": (3600.0, "с"),
    "сут": (86400.0, "с"),

    # Сила
    "н": (1.0, "Н"),
    "n": (1.0, "Н"),

    # Давление
    "па": (1.0, "Па"),
    "pa": (1.0, "Па"),
    "атм": (101325.0, "Па"),
    "atm": (101325.0, "Па"),
    "ммртст": (133.322, "Па"),

    # Энергия и работа
    "дж": (1.0, "Дж"),
    "j": (1.0, "Дж"),
    "эв": (1.602176634e-19, "Дж"),
    "ev": (1.602176634e-19, "Дж"),
    "квт*ч": (3.6e6, "Дж"),
    "квт-ч": (3.6e6, "Дж"),
    "квтч": (3.6e6, "Дж"),
    "kwh": (3.6e6, "Дж"),

    # Мощность
    "вт": (1.0, "Вт"),
    "w": (1.0, "Вт"),

    # Электричество и магнетизм
    "а": (1.0, "А"),
    "a": (1.0, "А"),
    "в": (1.0, "В"),
    "v": (1.0, "В"),
    "ом": (1.0, "Ом"),
    "ohm": (1.0, "Ом"),
    "кл": (1.0, "Кл"),
    "coulomb": (1.0, "Кл"),
    "ф": (1.0, "Ф"),
    "f": (1.0, "Ф"),
    "тл": (1.0, "Тл"),
    "tl": (1.0, "Тл"),
    "вб": (1.0, "Вб"),
    "wb": (1.0, "Вб"),
    "гн": (1.0, "Гн"),
    "h_ind": (1.0, "Гн"),
    "ом*м": (1.0, "Ом·м"),
    "ом·м": (1.0, "Ом·м"),

    # Частота и активность
    "гц": (1.0, "Гц"),
    "hz": (1.0, "Гц"),
    "бк": (1.0, "Бк"),
    "bq": (1.0, "Бк"),

    # Оптика
    "дптр": (1.0, "дптр"),
    "dptr": (1.0, "дптр"),

    # Составные механики
    "м/с": (1.0, "м/с"),
    "m/s": (1.0, "м/с"),
    "км/ч": (1.0 / 3.6, "м/с"),
    "km/h": (1.0 / 3.6, "м/с"),
    "м/с2": (1.0, "м/с²"),
    "м/с^2": (1.0, "м/с²"),
    "м/с²": (1.0, "м/с²"),
    "m/s2": (1.0, "м/с²"),

    # Площадь и объём
    "мм2": (1e-6, "м²"),
    "мм^2": (1e-6, "м²"),
    "см2": (1e-4, "м²"),
    "см^2": (1e-4, "м²"),
    "м2": (1.0, "м²"),
    "м^2": (1.0, "м²"),
    "см3": (1e-6, "м³"),
    "см^3": (1e-6, "м³"),
    "л": (1e-3, "м³"),
    "l": (1e-3, "м³"),
    "м3": (1.0, "м³"),
    "м^3": (1.0, "м³"),

    # Плотность
    "кг/м3": (1.0, "кг/м³"),
    "кг/м^3": (1.0, "кг/м³"),
    "г/см3": (1000.0, "кг/м³"),
    "г/см^3": (1000.0, "кг/м³"),

    # Количество вещества
    "моль": (1.0, "моль"),
    "mol": (1.0, "моль"),
}

# Множители стандартных приставок СИ
PREFIXES = {
    "п": 1e-12, "p": 1e-12,   # пико
    "н": 1e-9,  "n": 1e-9,    # нано
    "мк": 1e-6, "mk": 1e-6, "u": 1e-6, "µ": 1e-6,  # микро
    "м": 1e-3,  "m": 1e-3,    # милли[cite: 9]
    "с": 1e-2,  "c": 1e-2,    # санти[cite: 9]
    "д": 1e-1,  "d": 1e-1,    # деци
    "к": 1e3,   "k": 1e3,     # кило
    "мг": 1e6,  "M": 1e6,     # мега
    "гг": 1e9,  "G": 1e9,     # гига
}


def parse_to_si(raw_val_str: str) -> Tuple[float, str, float, str]:
    """
    Разбирает строку (например: '20 г', '0.4 Тл', '5 banana').
    Возвращает кортеж: (исходное_число, исходная_единица, значение_СИ, единица_СИ).
    При неизвестной единице измерения выбрасывает UnknownUnitError.
    """
    cleaned = raw_val_str.strip().replace("−", "-").replace("–", "-")

    # Регулярка для отделения числа от единицы измерения (поддерживает e-нотацию)
    match = re.match(r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*(.*)$", cleaned)
    if not match:
        raise ValueError(f"Не удалось извлечь числовое значение из '{raw_val_str}'")

    num_val = float(match.group(1))
    unit_str = match.group(2).strip()
    u_lower = unit_str.lower()

    # 1. Проверка градусов Цельсия
    if u_lower in ["°c", "°с", "c", "с", "град", "градус", "градусов"] and ("t" in cleaned.lower() or "°" in unit_str):
        return num_val, unit_str, num_val + 273.15, "К"[cite: 8]
    if unit_str in ["°C", "°С"]:
        return num_val, unit_str, num_val + 273.15, "К"[cite: 8]
    if u_lower in ["к", "k", "кельвин", "кельвинов"]:
        return num_val, unit_str, num_val, "К"

    # 2. Прямой поиск базовой/составной единицы[cite: 9]
    if u_lower in BASE_UNITS:
        mult, si_unit = BASE_UNITS[u_lower]
        return num_val, unit_str, num_val * mult, si_unit

    # 3. Поиск комбинации (приставка + известная базовая единица)[cite: 9]
    # Сортируем приставки по убыванию длины ('мк' раньше 'м')
    sorted_prefixes = sorted(PREFIXES.items(), key=lambda x: len(x[0]), reverse=True)
    for p_name, p_mult in sorted_prefixes:
        if u_lower.startswith(p_name):
            base_part = u_lower[len(p_name):]
            if base_part in BASE_UNITS and base_part not in ["", "си", "%"]:
                b_mult, si_unit = BASE_UNITS[base_part]
                total_mult = p_mult * b_mult
                return num_val, unit_str, num_val * total_mult, si_unit

    # 4. Если ничего не подошло — выбрасываем исключение[cite: 9, 12]
    raise UnknownUnitError(
        f"Неизвестная единица измерения: '{unit_str}'. "
        f"Проверьте правильность написания величины."
    )







from math_engine import Expr, parse_expr

# Сопоставление функциональных переменных с базовыми единицами
UNITS[Variable.POSITION_FUNC] = "м"
UNITS[Variable.VELOCITY_FUNC] = "м/с"
UNITS[Variable.ACCELERATION_FUNC] = "м/с²"
UNITS[Variable.FORCE_FUNC] = "Н"
UNITS[Variable.CURRENT_FUNC] = "А"
UNITS[Variable.MAGNETIC_FLUX_FUNC] = "Вб"
UNITS[Variable.COORD_START] = "м"
UNITS[Variable.COORD_END] = "м"
UNITS[Variable.TIME_START] = "с"
UNITS[Variable.TIME_END] = "с"


def parse_expression_input(raw_val_str: str) -> Tuple[Expr, str]:
    """
    Разбирает функциональное выражение с размерностью.
    Пример: '3*t^2 - 5*t + 2 м' -> (Expr, 'м')
            '4*x + 1 Н'          -> (Expr, 'Н')
    """
    raw = raw_val_str.strip()
    
    # Отделяем хвостовую единицу измерения
    tokens = raw.rsplit(maxsplit=1)
    if len(tokens) == 2:
        expr_candidate, potential_unit = tokens[0], tokens[1]
        u_lower = potential_unit.lower()
        if u_lower in BASE_UNITS:
            mult, si_unit = BASE_UNITS[u_lower]
            expr_obj = parse_expr(expr_candidate)
            if not math.isclose(mult, 1.0):
                expr_obj = expr_obj * mult
            return expr_obj, si_unit
            
    # Если единица не указана явно, считаем по умолчанию в СИ
    return parse_expr(raw), ""


def parse_any_input(raw_val_str: str):
    """
    Универсальный диспетчер: если в строке есть символы функций ('t', 'x')
    и операторы сложения/умножения — парсит как Expr, иначе как обычное число в СИ.
    """
    cleaned = raw_val_str.strip()
    has_symbols = any(sym in cleaned for sym in ["t", "x", "T"])
    has_operators = any(op in cleaned for op in ["*", "^", "+", "-"])

    if has_symbols and has_operators:
        return parse_expression_input(cleaned)
    else:
        # Стандартный скалярный разбор
        num, raw_u, si_val, si_u = parse_to_si(cleaned)
        return si_val, si_u