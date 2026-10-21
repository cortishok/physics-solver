from enum import Enum


class Variable(Enum):
    # --- Кинематика и Механика ---
    MASS = "m"
    MASS_1 = "m1"
    MASS_2 = "m2"
    MASS_ROD = "m_rod"
    VELOCITY = "v"
    VELOCITY_0 = "v0"
    VELOCITY_1 = "v1"
    VELOCITY_2 = "v2"
    VELOCITY_MAX = "v_max"
    U_SPEED = "u_speed"
    ACCELERATION = "a"
    TIME = "t"
    TIME_START = "t_start"
    TIME_END = "t_end"
    DISPLACEMENT = "S"
    HEIGHT = "h"
    RADIUS = "R_radius"
    ANGLE = "alpha"
    OMEGA = "omega"
    FREQUENCY_ROT = "freq_rot"
    PERIOD = "T_period"

    # --- Динамика и Векторные силы ---
    FORCE = "F"
    FORCE_PULL = "F_pull"
    FORCE_FRICTION = "F_tr"
    NORMAL_FORCE = "N_norm"
    TENSION = "T_tension"
    WEIGHT = "P_weight"
    FRICTION_COEFF = "mu"
    SPRING_K = "k"
    SPRING_X = "x_spring"
    MOMENTUM = "p"
    MOMENTUM_PHOTONS = "p_photons"
    PRESSURE = "P_press"
    DENSITY = "rho"
    VOLUME = "V"
    AREA = "S_area"
    ARCHIMEDES_FORCE = "F_arch"

    # --- Энергия, Работа, Мощность ---
    KINETIC_ENERGY = "E_k"
    POTENTIAL_ENERGY = "E_p"
    MECHANICAL_ENERGY = "E_mech"
    WORK = "A"
    POWER_MECH = "N_power"
    EFFICIENCY = "eta"

    # --- Функции матанализа ---
    X_FUNC = "x_func"
    V_FUNC = "v_func"
    A_FUNC = "a_func"
    F_FUNC = "F_func"

    # --- Термодинамика и МКТ ---
    HEAT = "Q"
    HEAT_HOT = "Q1_hot"
    HEAT_COLD = "Q2_cold"
    SPECIFIC_HEAT = "c"
    TEMP = "T"
    DELTA_TEMP = "delta_T"
    LATENT_MELT = "lambda_melt"
    LATENT_VAP = "L_vap"
    MOLAR_MASS = "M_mol"
    AMOUNT_SUBSTANCE = "nu_mol"

    # --- Электродинамика и Магнетизм ---
    CHARGE = "q"
    CURRENT = "I"
    VOLTAGE = "U"
    RESISTANCE = "R"
    POWER_EL = "P_el"
    Q_JOULE = "Q_joule"
    MAGNETIC_B = "B"
    WIRE_LENGTH = "l"
    MAGNETIC_FLUX = "Phi"
    EMF_IND = "E_ind"
    EMF_SOURCE = "E_emf"
    CAPACITANCE = "C"
    INDUCTANCE = "L_ind"
    THOMSON_PERIOD = "T_thomson"

    # --- Квантовая и Ядерная физика ---
    FREQ_LIGHT = "nu_freq"
    WAVELENGTH = "lambda_wave"
    WORK_FUNCTION = "A_vyh"
    STOPPING_VOLTAGE = "U_stop"
    PHOTON_ENERGY = "E_ph"
    PARTICLES_COUNT = "N_particles"
    DECAY_CONSTANT = "lambda_decay"
    ACTIVITY = "A_act"

    # --- Константы ---
    G_ACCEL = "g"
    SPEED_OF_LIGHT = "c_light"
    PLANCK = "h_planck"
    ELEM_CHARGE = "e_charge"
    GAS_CONSTANT = "R_gas"


# Канонические отображаемые имена
VARIABLE_DISPLAY_NAMES = {var: var.value for var in Variable}
VARIABLE_DISPLAY_NAMES.update({
    Variable.X_FUNC: "x(t)",
    Variable.V_FUNC: "v(t)",
    Variable.A_FUNC: "a(t)",
    Variable.F_FUNC: "F(t)",
})

# Единицы измерения СИ для вывода ответа
VARIABLE_UNITS = {
    Variable.MASS: "кг",
    Variable.MASS_1: "кг",
    Variable.MASS_2: "кг",
    Variable.MASS_ROD: "кг",
    Variable.VELOCITY: "м/с",
    Variable.VELOCITY_0: "м/с",
    Variable.VELOCITY_1: "м/с",
    Variable.VELOCITY_2: "м/с",
    Variable.VELOCITY_MAX: "м/с",
    Variable.U_SPEED: "м/с",
    Variable.ACCELERATION: "м/с²",
    Variable.TIME: "с",
    Variable.TIME_START: "с",
    Variable.TIME_END: "с",
    Variable.DISPLACEMENT: "м",
    Variable.HEIGHT: "м",
    Variable.RADIUS: "м",
    Variable.ANGLE: "°",
    Variable.OMEGA: "рад/с",
    Variable.FREQUENCY_ROT: "Гц",
    Variable.PERIOD: "с",
    Variable.FORCE: "Н",
    Variable.FORCE_PULL: "Н",
    Variable.FORCE_FRICTION: "Н",
    Variable.NORMAL_FORCE: "Н",
    Variable.TENSION: "Н",
    Variable.WEIGHT: "Н",
    Variable.FRICTION_COEFF: "",
    Variable.SPRING_K: "Н/м",
    Variable.SPRING_X: "м",
    Variable.MOMENTUM: "кг·м/с",
    Variable.MOMENTUM_PHOTONS: "кг·м/с",
    Variable.PRESSURE: "Па",
    Variable.DENSITY: "кг/м³",
    Variable.VOLUME: "м³",
    Variable.AREA: "м²",
    Variable.ARCHIMEDES_FORCE: "Н",
    Variable.KINETIC_ENERGY: "Дж",
    Variable.POTENTIAL_ENERGY: "Дж",
    Variable.MECHANICAL_ENERGY: "Дж",
    Variable.WORK: "Дж",
    Variable.POWER_MECH: "Вт",
    Variable.EFFICIENCY: "",
    Variable.HEAT: "Дж",
    Variable.HEAT_HOT: "Дж",
    Variable.HEAT_COLD: "Дж",
    Variable.SPECIFIC_HEAT: "Дж/(кг·К)",
    Variable.TEMP: "К",
    Variable.DELTA_TEMP: "К",
    Variable.LATENT_MELT: "Дж/кг",
    Variable.LATENT_VAP: "Дж/кг",
    Variable.MOLAR_MASS: "кг/моль",
    Variable.AMOUNT_SUBSTANCE: "моль",
    Variable.CHARGE: "Кл",
    Variable.CURRENT: "А",
    Variable.VOLTAGE: "В",
    Variable.RESISTANCE: "Ом",
    Variable.POWER_EL: "Вт",
    Variable.Q_JOULE: "Дж",
    Variable.MAGNETIC_B: "Тл",
    Variable.WIRE_LENGTH: "м",
    Variable.MAGNETIC_FLUX: "Вб",
    Variable.EMF_IND: "В",
    Variable.EMF_SOURCE: "В",
    Variable.CAPACITANCE: "Ф",
    Variable.INDUCTANCE: "Гн",
    Variable.THOMSON_PERIOD: "с",
    Variable.FREQ_LIGHT: "Гц",
    Variable.WAVELENGTH: "м",
    Variable.WORK_FUNCTION: "Дж",
    Variable.STOPPING_VOLTAGE: "В",
    Variable.PHOTON_ENERGY: "Дж",
    Variable.PARTICLES_COUNT: "",
    Variable.DECAY_CONSTANT: "с⁻¹",
    Variable.ACTIVITY: "Бк",
}

# Словарь синонимов и алиасов для ввода пользователя
STRING_TO_VARIABLE = {}
for _v in Variable:
    STRING_TO_VARIABLE[_v.value] = _v
    STRING_TO_VARIABLE[_v.name] = _v

STRING_TO_VARIABLE.update({
    # Функции
    "R_rad": Variable.RADIUS,
    "r": Variable.RADIUS,
    "x(t)": Variable.X_FUNC,
    "v(t)": Variable.V_FUNC,
    "a(t)": Variable.A_FUNC,
    "F(t)": Variable.F_FUNC,
    # Индексы и синонимы механики
    "m_1": Variable.MASS_1,
    "m_2": Variable.MASS_2,
    "m_vapor": Variable.MASS,
    "v_0": Variable.VELOCITY_0,
    "v_1": Variable.VELOCITY_1,
    "v_2": Variable.VELOCITY_2,
    "u": Variable.U_SPEED,
    "delta_x": Variable.SPRING_X,
    "x": Variable.SPRING_X,
    "F_tp": Variable.FORCE_FRICTION,
    "F_fr": Variable.FORCE_FRICTION,
    "N": Variable.NORMAL_FORCE,
    "T_nit": Variable.TENSION,
    "P": Variable.WEIGHT,
    "p_ph": Variable.MOMENTUM_PHOTONS,
    # Термодинамика
    "c_heat": Variable.SPECIFIC_HEAT,
    "L": Variable.LATENT_VAP,
    # Электродинамика и Кванты
    "U_volt": Variable.VOLTAGE,
    "nu": Variable.FREQ_LIGHT,
})