# physics_formulas.py
from math_engine import Expr
from dataclasses import dataclass
from typing import List, Callable, Dict, Any
import math

from variables import Variable
from constants import CONSTANTS


@dataclass(frozen=True)
class Formula:
    id: str
    section: str
    requires: List[Variable]
    result_variable: Variable
    calc: Callable[[Dict[Variable, float]], float]
    pretty: str

    def __getitem__(self, item):
        return getattr(self, item)


FORMULAS_LIST = [
    # =========================================================
    # 1. КИНЕМАТИКА
    # =========================================================
    Formula(
        id="S = v * t", section="mechanics",
        requires=[Variable.VELOCITY, Variable.TIME],
        result_variable=Variable.DISTANCE,
        calc=lambda env: env[Variable.VELOCITY] * env[Variable.TIME],
        pretty="S = v·t"
    ),
    Formula(
        id="S = v * t (найти v)", section="mechanics",
        requires=[Variable.DISTANCE, Variable.TIME],
        result_variable=Variable.VELOCITY,
        calc=lambda env: env[Variable.DISTANCE] / env[Variable.TIME],
        pretty="v = S / t"
    ),
    Formula(
        id="S = v * t (найти t)", section="mechanics",
        requires=[Variable.DISTANCE, Variable.VELOCITY],
        result_variable=Variable.TIME,
        calc=lambda env: env[Variable.DISTANCE] / env[Variable.VELOCITY],
        pretty="t = S / v"
    ),
    Formula(
        id="S = v0*t + (a*t^2)/2", section="mechanics",
        requires=[Variable.INITIAL_VELOCITY, Variable.ACCELERATION, Variable.TIME],
        result_variable=Variable.DISTANCE,
        calc=lambda env: env[Variable.INITIAL_VELOCITY] * env[Variable.TIME] + (env[Variable.ACCELERATION] * (env[Variable.TIME] ** 2)) / 2,
        pretty="S = v₀·t + (a·t²) / 2"
    ),
    Formula(
        id="S = v0*t + (a*t^2)/2 (найти v0)", section="mechanics",
        requires=[Variable.DISTANCE, Variable.ACCELERATION, Variable.TIME],
        result_variable=Variable.INITIAL_VELOCITY,
        calc=lambda env: (env[Variable.DISTANCE] - (env[Variable.ACCELERATION] * (env[Variable.TIME] ** 2)) / 2) / env[Variable.TIME],
        pretty="v₀ = (S − a·t²/2) / t"
    ),
    Formula(
        id="S = v0*t + (a*t^2)/2 (найти a)", section="mechanics",
        requires=[Variable.DISTANCE, Variable.INITIAL_VELOCITY, Variable.TIME],
        result_variable=Variable.ACCELERATION,
        calc=lambda env: 2 * (env[Variable.DISTANCE] - env[Variable.INITIAL_VELOCITY] * env[Variable.TIME]) / (env[Variable.TIME] ** 2),
        pretty="a = 2(S − v₀·t) / t²"
    ),
    Formula(
        id="v = v0 + a * t", section="mechanics",
        requires=[Variable.INITIAL_VELOCITY, Variable.ACCELERATION, Variable.TIME],
        result_variable=Variable.VELOCITY,
        calc=lambda env: env[Variable.INITIAL_VELOCITY] + env[Variable.ACCELERATION] * env[Variable.TIME],
        pretty="v = v₀ + a·t"
    ),
    Formula(
        id="v = v0 + a * t (найти v0)", section="mechanics",
        requires=[Variable.VELOCITY, Variable.ACCELERATION, Variable.TIME],
        result_variable=Variable.INITIAL_VELOCITY,
        calc=lambda env: env[Variable.VELOCITY] - env[Variable.ACCELERATION] * env[Variable.TIME],
        pretty="v₀ = v − a·t"
    ),
    Formula(
        id="v = v0 + a * t (найти a)", section="mechanics",
        requires=[Variable.VELOCITY, Variable.INITIAL_VELOCITY, Variable.TIME],
        result_variable=Variable.ACCELERATION,
        calc=lambda env: (env[Variable.VELOCITY] - env[Variable.INITIAL_VELOCITY]) / env[Variable.TIME],
        pretty="a = (v − v₀) / t"
    ),
    Formula(
        id="v = v0 + a * t (найти t)", section="mechanics",
        requires=[Variable.VELOCITY, Variable.INITIAL_VELOCITY, Variable.ACCELERATION],
        result_variable=Variable.TIME,
        calc=lambda env: (env[Variable.VELOCITY] - env[Variable.INITIAL_VELOCITY]) / env[Variable.ACCELERATION],
        pretty="t = (v − v₀) / a"
    ),
    Formula(
        id="a = v^2 / R", section="mechanics",
        requires=[Variable.VELOCITY, Variable.RADIUS],
        result_variable=Variable.CENTRIPETAL_ACC,
        calc=lambda env: (env[Variable.VELOCITY] ** 2) / env[Variable.RADIUS],
        pretty="aц = v² / R"
    ),
    Formula(
        id="a = v^2 / R (найти v)", section="mechanics",
        requires=[Variable.CENTRIPETAL_ACC, Variable.RADIUS],
        result_variable=Variable.VELOCITY,
        calc=lambda env: math.sqrt(env[Variable.CENTRIPETAL_ACC] * env[Variable.RADIUS]),
        pretty="v = √(aц·R)"
    ),
    Formula(
        id="a = v^2 / R (найти R)", section="mechanics",
        requires=[Variable.VELOCITY, Variable.CENTRIPETAL_ACC],
        result_variable=Variable.RADIUS,
        calc=lambda env: (env[Variable.VELOCITY] ** 2) / env[Variable.CENTRIPETAL_ACC],
        pretty="R = v² / aц"
    ),
    Formula(
        id="v = omega * R", section="mechanics",
        requires=[Variable.ANGULAR_VELOCITY, Variable.RADIUS],
        result_variable=Variable.VELOCITY,
        calc=lambda env: env[Variable.ANGULAR_VELOCITY] * env[Variable.RADIUS],
        pretty="v = ω·R"
    ),
    Formula(
        id="omega = 2 * pi * nu_freq", section="mechanics",
        requires=[Variable.FREQUENCY],
        result_variable=Variable.ANGULAR_VELOCITY,
        calc=lambda env: 2 * math.pi * env[Variable.FREQUENCY],
        pretty="ω = 2π·ν"
    ),
    Formula(
        id="nu_freq = 1 / T_period", section="mechanics",
        requires=[Variable.PERIOD],
        result_variable=Variable.FREQUENCY,
        calc=lambda env: 1.0 / env[Variable.PERIOD],
        pretty="ν = 1 / T"
    ),

    # =========================================================
    # 2. ДИНАМИКА, ТЯГОТЕНИЕ, СТАТИКА
    # =========================================================
    Formula(
        id="a = (F - mu*m*g) / m", section="mechanics",
        requires=[Variable.FORCE, Variable.MASS, Variable.FRICTION_COEFF],
        result_variable=Variable.ACCELERATION,
        calc=lambda env: (env[Variable.FORCE] - env[Variable.FRICTION_COEFF] * env[Variable.MASS] * CONSTANTS["g"]) / env[Variable.MASS],
        pretty="a = (F − μ·m·g) / m"
    ),
    Formula(
        id="F = a*m + mu*m*g", section="mechanics",
        requires=[Variable.ACCELERATION, Variable.MASS, Variable.FRICTION_COEFF],
        result_variable=Variable.FORCE,
        calc=lambda env: env[Variable.ACCELERATION] * env[Variable.MASS] + env[Variable.FRICTION_COEFF] * env[Variable.MASS] * CONSTANTS["g"],
        pretty="F = m·(a + μ·g)"
    ),
    Formula(
        id="a = F / m", section="mechanics",
        requires=[Variable.FORCE, Variable.MASS],
        result_variable=Variable.ACCELERATION,
        calc=lambda env: env[Variable.FORCE] / env[Variable.MASS],
        pretty="a = F / m"
    ),
    Formula(
        id="F = m * a", section="mechanics",
        requires=[Variable.MASS, Variable.ACCELERATION],
        result_variable=Variable.FORCE,
        calc=lambda env: env[Variable.MASS] * env[Variable.ACCELERATION],
        pretty="F = m·a"
    ),
    Formula(
        id="Fтр = mu * m * g", section="mechanics",
        requires=[Variable.FRICTION_COEFF, Variable.MASS],
        result_variable=Variable.FRICTION_FORCE,
        calc=lambda env: env[Variable.FRICTION_COEFF] * env[Variable.MASS] * CONSTANTS["g"],
        pretty="Fтр = μ·m·g"
    ),
    Formula(
        id="Fупр = k * x", section="mechanics",
        requires=[Variable.STIFFNESS, Variable.ELONGATION],
        result_variable=Variable.ELASTIC_FORCE,
        calc=lambda env: env[Variable.STIFFNESS] * env[Variable.ELONGATION],
        pretty="Fупр = k·x"
    ),
    Formula(
        id="Fупр = k * x (найти k)", section="mechanics",
        requires=[Variable.ELASTIC_FORCE, Variable.ELONGATION],
        result_variable=Variable.STIFFNESS,
        calc=lambda env: env[Variable.ELASTIC_FORCE] / env[Variable.ELONGATION],
        pretty="k = Fупр / x"
    ),
    Formula(
        id="Fупр = k * x (найти x)", section="mechanics",
        requires=[Variable.ELASTIC_FORCE, Variable.STIFFNESS],
        result_variable=Variable.ELONGATION,
        calc=lambda env: env[Variable.ELASTIC_FORCE] / env[Variable.STIFFNESS],
        pretty="x = Fупр / k"
    ),
    Formula(
        id="Fтяж = m * g", section="mechanics",
        requires=[Variable.MASS],
        result_variable=Variable.GRAVITY_FORCE,
        calc=lambda env: env[Variable.MASS] * CONSTANTS["g"],
        pretty="Fтяж = m·g"
    ),
    Formula(
        id="F_grav = G_grav * m1 * m2 / R^2", section="mechanics",
        requires=[Variable.MASS_1, Variable.MASS_2, Variable.RADIUS],
        result_variable=Variable.GRAVITATIONAL_FORCE,
        calc=lambda env: CONSTANTS["G_grav"] * env[Variable.MASS_1] * env[Variable.MASS_2] / (env[Variable.RADIUS] ** 2),
        pretty="F = G·(m₁·m₂) / R²"
    ),
    Formula(
        id="v_cosmic_1 = sqrt(G_grav * M_earth / R_earth)", section="mechanics",
        requires=[],
        result_variable=Variable.FIRST_COSMIC_VEL,
        calc=lambda env: math.sqrt(CONSTANTS["G_grav"] * CONSTANTS["M_earth"] / CONSTANTS["R_earth"]),
        pretty="v₁ = √(G·M / R)"
    ),
    Formula(
        id="P = Fтяж / S", section="mechanics",
        requires=[Variable.GRAVITY_FORCE, Variable.AREA],
        result_variable=Variable.PRESSURE,
        calc=lambda env: env[Variable.GRAVITY_FORCE] / env[Variable.AREA],
        pretty="P = Fтяж / S"
    ),
    Formula(
        id="P = F / S", section="mechanics",
        requires=[Variable.FORCE, Variable.AREA],
        result_variable=Variable.PRESSURE,
        calc=lambda env: env[Variable.FORCE] / env[Variable.AREA],
        pretty="P = F / S"
    ),
    Formula(
        id="M_moment = F * l", section="mechanics",
        requires=[Variable.FORCE, Variable.LENGTH],
        result_variable=Variable.TORQUE,
        calc=lambda env: env[Variable.FORCE] * env[Variable.LENGTH],
        pretty="M = F·l"
    ),

    # Связка видов работы (полезная работа -> общая работа механизма)
    Formula(
        id="A = A_polez", section="mechanics",
        requires=[Variable.USEFUL_WORK],
        result_variable=Variable.WORK,
        calc=lambda env: env[Variable.USEFUL_WORK],
        pretty="A = Aпол"
    ),
    # Выражение потенциальной энергии через работу
    Formula(
        id="E_p = A", section="mechanics",
        requires=[Variable.WORK],
        result_variable=Variable.POTENTIAL_ENERGY,
        calc=lambda env: env[Variable.WORK],
        pretty="Eп = A"
    ),
    # Выражение высоты подъема h = Eп / (m·g)
    Formula(
        id="h = E_p / (m * g)", section="mechanics",
        requires=[Variable.POTENTIAL_ENERGY, Variable.MASS],
        result_variable=Variable.HEIGHT,
        calc=lambda env: env[Variable.POTENTIAL_ENERGY] / (env[Variable.MASS] * CONSTANTS["g"]),
        pretty="h = Eп / (m·g)"
    ),

    # =========================================================
    # 3. ЗАКОНЫ СОХРАНЕНИЯ, РАБОТА, МОЩНОСТЬ
    # =========================================================
    Formula(
        id="p = m * v", section="mechanics",
        requires=[Variable.MASS, Variable.VELOCITY],
        result_variable=Variable.MOMENTUM,
        calc=lambda env: env[Variable.MASS] * env[Variable.VELOCITY],
        pretty="p = m·v"
    ),
    Formula(
        id="E_k = m * v^2 / 2", section="mechanics",
        requires=[Variable.MASS, Variable.VELOCITY],
        result_variable=Variable.KINETIC_ENERGY,
        calc=lambda env: (env[Variable.MASS] * (env[Variable.VELOCITY] ** 2)) / 2,
        pretty="Eк = (m·v²) / 2"
    ),
    Formula(
        id="E_p = m * g * h_height", section="mechanics",
        requires=[Variable.MASS, Variable.HEIGHT],
        result_variable=Variable.POTENTIAL_ENERGY,
        calc=lambda env: env[Variable.MASS] * CONSTANTS["g"] * env[Variable.HEIGHT],
        pretty="Eп = m·g·h"
    ),
    Formula(
        id="E_p_spring = k * x^2 / 2", section="mechanics",
        requires=[Variable.STIFFNESS, Variable.ELONGATION],
        result_variable=Variable.POTENTIAL_ENERGY,
        calc=lambda env: (env[Variable.STIFFNESS] * (env[Variable.ELONGATION] ** 2)) / 2,
        pretty="Eп = (k·x²) / 2"
    ),
    Formula(
        id="E_mech = E_k_mech + E_p", section="mechanics",
        requires=[Variable.KINETIC_ENERGY, Variable.POTENTIAL_ENERGY],
        result_variable=Variable.MECHANICAL_ENERGY,
        calc=lambda env: env[Variable.KINETIC_ENERGY] + env[Variable.POTENTIAL_ENERGY],
        pretty="E = Eк + Eп"
    ),
    Formula(
        id="A = F * S", section="mechanics",
        requires=[Variable.FORCE, Variable.DISTANCE],
        result_variable=Variable.WORK,
        calc=lambda env: env[Variable.FORCE] * env[Variable.DISTANCE],
        pretty="A = F·S"
    ),
    Formula(
        id="A = E_p", section="mechanics",
        requires=[Variable.POTENTIAL_ENERGY],
        result_variable=Variable.WORK,
        calc=lambda env: env[Variable.POTENTIAL_ENERGY],
        pretty="A = Eп"
    ),
    Formula(
        id="N_power = A / t", section="mechanics",
        requires=[Variable.WORK, Variable.TIME],
        result_variable=Variable.POWER,
        calc=lambda env: env[Variable.WORK] / env[Variable.TIME],
        pretty="N = A / t"
    ),
    Formula(
        id="N_power = F * v", section="mechanics",
        requires=[Variable.FORCE, Variable.VELOCITY],
        result_variable=Variable.POWER,
        calc=lambda env: env[Variable.FORCE] * env[Variable.VELOCITY],
        pretty="N = F·v"
    ),

    # =========================================================
    # 4. ГИДРОСТАТИКА И КПД
    # =========================================================
    Formula(
        id="m = rho_liquid * V", section="hydrostatics",
        requires=[Variable.DENSITY, Variable.VOLUME],
        result_variable=Variable.MASS,
        calc=lambda env: env[Variable.DENSITY] * env[Variable.VOLUME],
        pretty="m = ρ·V"
    ),
    Formula(
        id="V = m / rho_liquid", section="hydrostatics",
        requires=[Variable.MASS, Variable.DENSITY],
        result_variable=Variable.VOLUME,
        calc=lambda env: env[Variable.MASS] / env[Variable.DENSITY],
        pretty="V = m / ρ"
    ),
    Formula(
        id="P_hydro = rho_liquid * g * h_height", section="hydrostatics",
        requires=[Variable.DENSITY, Variable.HEIGHT],
        result_variable=Variable.HYDROSTATIC_PRESSURE,
        calc=lambda env: env[Variable.DENSITY] * CONSTANTS["g"] * env[Variable.HEIGHT],
        pretty="P = ρ·g·h"
    ),
    Formula(
        id="h_height = P_hydro / (rho_liquid * g)", section="hydrostatics",
        requires=[Variable.HYDROSTATIC_PRESSURE, Variable.DENSITY],
        result_variable=Variable.HEIGHT,
        calc=lambda env: env[Variable.HYDROSTATIC_PRESSURE] / (env[Variable.DENSITY] * CONSTANTS["g"]),
        pretty="h = P / (ρ·g)"
    ),
    Formula(
        id="F_archimedes = rho_liquid * g * V", section="hydrostatics",
        requires=[Variable.DENSITY, Variable.VOLUME],
        result_variable=Variable.ARCHIMEDES_FORCE,
        calc=lambda env: env[Variable.DENSITY] * CONSTANTS["g"] * env[Variable.VOLUME],
        pretty="Fа = ρ·g·V"
    ),
    Formula(
        id="V = F_archimedes / (rho_liquid * g)", section="hydrostatics",
        requires=[Variable.ARCHIMEDES_FORCE, Variable.DENSITY],
        result_variable=Variable.VOLUME,
        calc=lambda env: env[Variable.ARCHIMEDES_FORCE] / (env[Variable.DENSITY] * CONSTANTS["g"]),
        pretty="V = Fа / (ρ·g)"
    ),
    Formula(
        id="eta = A_polez / A_poln", section="efficiency",
        requires=[Variable.USEFUL_WORK, Variable.TOTAL_WORK],
        result_variable=Variable.EFFICIENCY,
        calc=lambda env: env[Variable.USEFUL_WORK] / env[Variable.TOTAL_WORK],
        pretty="η = Aпол / Aполн"
    ),
    Formula(
        id="A_polez = eta * A_poln", section="efficiency",
        requires=[Variable.EFFICIENCY, Variable.TOTAL_WORK],
        result_variable=Variable.USEFUL_WORK,
        calc=lambda env: env[Variable.EFFICIENCY] * env[Variable.TOTAL_WORK],
        pretty="Aпол = η·Aполн"
    ),
    Formula(
        id="A_poln = A_polez / eta", section="efficiency",
        requires=[Variable.USEFUL_WORK, Variable.EFFICIENCY],
        result_variable=Variable.TOTAL_WORK,
        calc=lambda env: env[Variable.USEFUL_WORK] / env[Variable.EFFICIENCY],
        pretty="Aполн = Aпол / η"
    ),
    Formula(
        id="eta = (Q1_hot - Q2_cold) / Q1_hot", section="efficiency",
        requires=[Variable.HEAT_HOT, Variable.HEAT_COLD],
        result_variable=Variable.EFFICIENCY,
        calc=lambda env: (env[Variable.HEAT_HOT] - env[Variable.HEAT_COLD]) / env[Variable.HEAT_HOT],
        pretty="η = (Q₁ − Q₂) / Q₁"
    ),
    Formula(
        id="eta_carnot = (T1_hot - T2_cold) / T1_hot", section="efficiency",
        requires=[Variable.TEMP_HOT, Variable.TEMP_COLD],
        result_variable=Variable.CARNOT_EFFICIENCY,
        calc=lambda env: (env[Variable.TEMP_HOT] - env[Variable.TEMP_COLD]) / env[Variable.TEMP_HOT],
        pretty="η = (T₁ − T₂) / T₁"
    ),
    Formula(
        id="A_polez = Q1_hot - Q2_cold", section="efficiency",
        requires=[Variable.HEAT_HOT, Variable.HEAT_COLD],
        result_variable=Variable.USEFUL_WORK,
        calc=lambda env: env[Variable.HEAT_HOT] - env[Variable.HEAT_COLD],
        pretty="A = Q₁ − Q₂"
    ),
    Formula(
        id="Q2_cold = Q1_hot * (1 - eta)", section="efficiency",
        requires=[Variable.HEAT_HOT, Variable.EFFICIENCY],
        result_variable=Variable.HEAT_COLD,
        calc=lambda env: env[Variable.HEAT_HOT] * (1.0 - env[Variable.EFFICIENCY]),
        pretty="Q₂ = Q₁·(1 − η)"
    ),

    # =========================================================
    # 5. МКТ И ТЕРМОДИНАМИКА
    # =========================================================
    Formula(
        id="PV = νRT (найти P)", section="mkt_thermo",
        requires=[Variable.MOLE_AMOUNT, Variable.VOLUME, Variable.TEMPERATURE],
        result_variable=Variable.PRESSURE,
        calc=lambda env: (env[Variable.MOLE_AMOUNT] * CONSTANTS["R_univ"] * env[Variable.TEMPERATURE]) / env[Variable.VOLUME],
        pretty="P = (ν·R·T) / V"
    ),
    Formula(
        id="A_polez = eta * Q1_hot", section="efficiency",
        requires=[Variable.EFFICIENCY, Variable.HEAT_HOT],
        result_variable=Variable.USEFUL_WORK,
        calc=lambda env: env[Variable.EFFICIENCY] * env[Variable.HEAT_HOT],
        pretty="Aпол = η·Q₁"
    ),
    Formula(
        id="PV = νRT (найти V)", section="mkt_thermo",
        requires=[Variable.PRESSURE, Variable.MOLE_AMOUNT, Variable.TEMPERATURE],
        result_variable=Variable.VOLUME,
        calc=lambda env: (env[Variable.MOLE_AMOUNT] * CONSTANTS["R_univ"] * env[Variable.TEMPERATURE]) / env[Variable.PRESSURE],
        pretty="V = (ν·R·T) / P"
    ),
    Formula(
        id="rho_liquid = m / V", section="hydrostatics",
        requires=[Variable.MASS, Variable.VOLUME],
        result_variable=Variable.DENSITY,
        calc=lambda env: env[Variable.MASS] / env[Variable.VOLUME],
        pretty="ρ = m / V"
    ),
    Formula(
        id="PV = νRT (найти T_temp)", section="mkt_thermo",
        requires=[Variable.PRESSURE, Variable.VOLUME, Variable.MOLE_AMOUNT],
        result_variable=Variable.TEMPERATURE,
        calc=lambda env: (env[Variable.PRESSURE] * env[Variable.VOLUME]) / (env[Variable.MOLE_AMOUNT] * CONSTANTS["R_univ"]),
        pretty="T = (P·V) / (ν·R)"
    ),
    Formula(
        id="PV = νRT (найти nu)", section="mkt_thermo",
        requires=[Variable.PRESSURE, Variable.VOLUME, Variable.TEMPERATURE],
        result_variable=Variable.MOLE_AMOUNT,
        calc=lambda env: (env[Variable.PRESSURE] * env[Variable.VOLUME]) / (CONSTANTS["R_univ"] * env[Variable.TEMPERATURE]),
        pretty="ν = (P·V) / (R·T)"
    ),
    Formula(
        id="P = n_conc * k_boltzmann * T_temp", section="mkt_thermo",
        requires=[Variable.CONCENTRATION, Variable.TEMPERATURE],
        result_variable=Variable.PRESSURE,
        calc=lambda env: env[Variable.CONCENTRATION] * CONSTANTS["k_boltzmann"] * env[Variable.TEMPERATURE],
        pretty="P = n·k·T"
    ),
    Formula(
        id="E_k_molecule = 3/2 * k_boltzmann * T_temp", section="mkt_thermo",
        requires=[Variable.TEMPERATURE],
        result_variable=Variable.MOLECULE_KINETIC,
        calc=lambda env: 1.5 * CONSTANTS["k_boltzmann"] * env[Variable.TEMPERATURE],
        pretty="Eк = 1.5·k·T"
    ),
    Formula(
        id="P = 2/3 * n_conc * E_k_molecule", section="mkt_thermo",
        requires=[Variable.CONCENTRATION, Variable.MOLECULE_KINETIC],
        result_variable=Variable.PRESSURE,
        calc=lambda env: (2.0 / 3.0) * env[Variable.CONCENTRATION] * env[Variable.MOLECULE_KINETIC],
        pretty="P = ⅔·n·Eк"
    ),
    Formula(
        id="Q = cmΔT", section="mkt_thermo",
        requires=[Variable.SPECIFIC_HEAT, Variable.MASS, Variable.TEMPERATURE],
        result_variable=Variable.HEAT,
        calc=lambda env: env[Variable.SPECIFIC_HEAT] * env[Variable.MASS] * env[Variable.TEMPERATURE],
        pretty="Q = c·m·ΔT"
    ),
    Formula(
        id="Q = λm", section="mkt_thermo",
        requires=[Variable.FUSION_HEAT, Variable.MASS],
        result_variable=Variable.HEAT,
        calc=lambda env: env[Variable.FUSION_HEAT] * env[Variable.MASS],
        pretty="Q = λ·m"
    ),
    Formula(
        id="Q = Lm", section="mkt_thermo",
        requires=[Variable.VAPOR_HEAT, Variable.MASS],
        result_variable=Variable.HEAT,
        calc=lambda env: env[Variable.VAPOR_HEAT] * env[Variable.MASS],
        pretty="Q = L·m"
    ),
    Formula(
        id="A = P * V", section="mkt_thermo",
        requires=[Variable.PRESSURE, Variable.VOLUME],
        result_variable=Variable.WORK,
        calc=lambda env: env[Variable.PRESSURE] * env[Variable.VOLUME],
        pretty="A = P·ΔV"
    ),
    Formula(
        id="U_thermo = 3/2 * nu * R_univ * T_temp", section="mkt_thermo",
        requires=[Variable.MOLE_AMOUNT, Variable.TEMPERATURE],
        result_variable=Variable.INTERNAL_ENERGY,
        calc=lambda env: 1.5 * env[Variable.MOLE_AMOUNT] * CONSTANTS["R_univ"] * env[Variable.TEMPERATURE],
        pretty="ΔU = 1.5·ν·R·T"
    ),
    Formula(
        id="Q = U_thermo + A", section="mkt_thermo",
        requires=[Variable.INTERNAL_ENERGY, Variable.WORK],
        result_variable=Variable.HEAT,
        calc=lambda env: env[Variable.INTERNAL_ENERGY] + env[Variable.WORK],
        pretty="Q = ΔU + A"
    ),
    Formula(
        id="U_thermo = Q - A", section="mkt_thermo",
        requires=[Variable.HEAT, Variable.WORK],
        result_variable=Variable.INTERNAL_ENERGY,
        calc=lambda env: env[Variable.HEAT] - env[Variable.WORK],
        pretty="ΔU = Q − A"
    ),
    Formula(
        id="Q = 2.5 * P * V", section="mkt_thermo",
        requires=[Variable.PRESSURE, Variable.VOLUME],
        result_variable=Variable.HEAT,
        calc=lambda env: 2.5 * env[Variable.PRESSURE] * env[Variable.VOLUME],
        pretty="Q = 2.5·P·ΔV"
    ),
    Formula(
        id="Q = 2.5 * A", section="mkt_thermo",
        requires=[Variable.WORK],
        result_variable=Variable.HEAT,
        calc=lambda env: 2.5 * env[Variable.WORK],
        pretty="Q = 2.5·A"
    ),
    Formula(
        id="U_thermo = 1.5 * P * V", section="mkt_thermo",
        requires=[Variable.PRESSURE, Variable.VOLUME],
        result_variable=Variable.INTERNAL_ENERGY,
        calc=lambda env: 1.5 * env[Variable.PRESSURE] * env[Variable.VOLUME],
        pretty="ΔU = 1.5·P·ΔV"
    ),
    Formula(
        id="U_thermo = 1.5 * A", section="mkt_thermo",
        requires=[Variable.WORK],
        result_variable=Variable.INTERNAL_ENERGY,
        calc=lambda env: 1.5 * env[Variable.WORK],
        pretty="ΔU = 1.5·A"
    ),

    # =========================================================
    # 6. ЭЛЕКТРОДИНАМИКА И ЦЕПИ
    # =========================================================
    Formula(
        id="I = U / R", section="electro_dynamics",
        requires=[Variable.VOLTAGE, Variable.RESISTANCE],
        result_variable=Variable.CURRENT,
        calc=lambda env: env[Variable.VOLTAGE] / env[Variable.RESISTANCE],
        pretty="I = U / R"
    ),
    Formula(
        id="U = I * R", section="electro_dynamics",
        requires=[Variable.CURRENT, Variable.RESISTANCE],
        result_variable=Variable.VOLTAGE,
        calc=lambda env: env[Variable.CURRENT] * env[Variable.RESISTANCE],
        pretty="U = I·R"
    ),
    Formula(
        id="R = U / I", section="electro_dynamics",
        requires=[Variable.VOLTAGE, Variable.CURRENT],
        result_variable=Variable.RESISTANCE,
        calc=lambda env: env[Variable.VOLTAGE] / env[Variable.CURRENT],
        pretty="R = U / I"
    ),
    Formula(
        id="I = E_emf / (R_electro + r_internal)", section="electro_dynamics",
        requires=[Variable.EMF, Variable.RESISTANCE, Variable.INTERNAL_RESISTANCE],
        result_variable=Variable.CURRENT,
        calc=lambda env: env[Variable.EMF] / (env[Variable.RESISTANCE] + env[Variable.INTERNAL_RESISTANCE]),
        pretty="I = ℰ / (R + r)"
    ),
    Formula(
        id="E_emf = I * (R_electro + r_internal)", section="electro_dynamics",
        requires=[Variable.CURRENT, Variable.RESISTANCE, Variable.INTERNAL_RESISTANCE],
        result_variable=Variable.EMF,
        calc=lambda env: env[Variable.CURRENT] * (env[Variable.RESISTANCE] + env[Variable.INTERNAL_RESISTANCE]),
        pretty="ℰ = I·(R + r)"
    ),
    Formula(
        id="I_sc = E_emf / r_internal", section="electro_dynamics",
        requires=[Variable.EMF, Variable.INTERNAL_RESISTANCE],
        result_variable=Variable.SHORT_CIRCUIT_CURRENT,
        calc=lambda env: env[Variable.EMF] / env[Variable.INTERNAL_RESISTANCE],
        pretty="Iкз = ℰ / r"
    ),
    Formula(
        id="eta = R_electro / (R_electro + r_internal)", section="efficiency",
        requires=[Variable.RESISTANCE, Variable.INTERNAL_RESISTANCE],
        result_variable=Variable.EFFICIENCY,
        calc=lambda env: env[Variable.RESISTANCE] / (env[Variable.RESISTANCE] + env[Variable.INTERNAL_RESISTANCE]),
        pretty="η = R / (R + r)"
    ),
    Formula(
        id="R = rho * l / S", section="electro_dynamics",
        requires=[Variable.RESISTIVITY, Variable.LENGTH, Variable.WIRE_AREA],
        result_variable=Variable.RESISTANCE,
        calc=lambda env: env[Variable.RESISTIVITY] * env[Variable.LENGTH] / env[Variable.WIRE_AREA],
        pretty="R = (ρ·l) / S"
    ),
    Formula(
        id="F = k * q1 * q2 / r^2", section="electro_dynamics",
        requires=[Variable.CHARGE_1, Variable.CHARGE_2, Variable.RADIUS],
        result_variable=Variable.COULOMB_FORCE,
        calc=lambda env: CONSTANTS["k_coulomb"] * env[Variable.CHARGE_1] * env[Variable.CHARGE_2] / (env[Variable.RADIUS] ** 2),
        pretty="F = k·(q₁·q₂) / r²"
    ),
    Formula(
        id="E = F / q", section="electro_dynamics",
        requires=[Variable.COULOMB_FORCE, Variable.CHARGE],
        result_variable=Variable.ELECTRIC_FIELD,
        calc=lambda env: env[Variable.COULOMB_FORCE] / env[Variable.CHARGE],
        pretty="E = F / q"
    ),
    Formula(
        id="C = q / U", section="electro_dynamics",
        requires=[Variable.CHARGE, Variable.VOLTAGE],
        result_variable=Variable.CAPACITANCE,
        calc=lambda env: env[Variable.CHARGE] / env[Variable.VOLTAGE],
        pretty="C = q / U"
    ),
    Formula(
        id="W = C * U^2 / 2", section="electro_dynamics",
        requires=[Variable.CAPACITANCE, Variable.VOLTAGE],
        result_variable=Variable.ELECTRIC_ENERGY,
        calc=lambda env: (env[Variable.CAPACITANCE] * (env[Variable.VOLTAGE] ** 2)) / 2,
        pretty="W = (C·U²) / 2"
    ),
    Formula(
        id="P_electro = I^2 * R_electro", section="electro_dynamics",
        requires=[Variable.CURRENT, Variable.RESISTANCE],
        result_variable=Variable.ELECTRIC_POWER,
        calc=lambda env: (env[Variable.CURRENT] ** 2) * env[Variable.RESISTANCE],
        pretty="P = I²·R"
    ),
    Formula(
        id="P_electro = I * U", section="electro_dynamics",
        requires=[Variable.CURRENT, Variable.VOLTAGE],
        result_variable=Variable.ELECTRIC_POWER,
        calc=lambda env: env[Variable.CURRENT] * env[Variable.VOLTAGE],
        pretty="P = I·U"
    ),
    Formula(
        id="Q_joule = I^2 * R_electro * t", section="electro_dynamics",
        requires=[Variable.CURRENT, Variable.RESISTANCE, Variable.TIME],
        result_variable=Variable.JOULE_HEAT,
        calc=lambda env: (env[Variable.CURRENT] ** 2) * env[Variable.RESISTANCE] * env[Variable.TIME],
        pretty="Q = I²·R·t"
    ),

    # =========================================================
    # 7. МАГНЕТИЗМ И СВЯЗЬ С МЕХАНИКОЙ
    # =========================================================
    Formula(
        id="a = F_A / m", section="magnetism",
        requires=[Variable.AMPERE_FORCE, Variable.MASS],
        result_variable=Variable.ACCELERATION,
        calc=lambda env: env[Variable.AMPERE_FORCE] / env[Variable.MASS],
        pretty="a = Fа / m"
    ),
    Formula(
        id="F_A = I * B * l", section="magnetism",
        requires=[Variable.CURRENT, Variable.MAGNETIC_FIELD, Variable.LENGTH],
        result_variable=Variable.AMPERE_FORCE,
        calc=lambda env: env[Variable.CURRENT] * env[Variable.MAGNETIC_FIELD] * env[Variable.LENGTH],
        pretty="Fа = I·B·l"
    ),
    Formula(
        id="F = F_A", section="magnetism",
        requires=[Variable.AMPERE_FORCE],
        result_variable=Variable.FORCE,
        calc=lambda env: env[Variable.AMPERE_FORCE],
        pretty="F = Fа"
    ),
    Formula(
        id="F_L = q * v * B", section="magnetism",
        requires=[Variable.CHARGE, Variable.VELOCITY, Variable.MAGNETIC_FIELD],
        result_variable=Variable.LORENTZ_FORCE,
        calc=lambda env: env[Variable.CHARGE] * env[Variable.VELOCITY] * env[Variable.MAGNETIC_FIELD],
        pretty="Fл = q·v·B"
    ),
    Formula(
        id="R = m * v / (q * B)", section="magnetism",
        requires=[Variable.MASS, Variable.VELOCITY, Variable.CHARGE, Variable.MAGNETIC_FIELD],
        result_variable=Variable.RADIUS,
        calc=lambda env: (env[Variable.MASS] * env[Variable.VELOCITY]) / (env[Variable.CHARGE] * env[Variable.MAGNETIC_FIELD]),
        pretty="R = (m·v) / (q·B)"
    ),
    Formula(
        id="T_period = 2 * pi * R / v", section="mechanics",
        requires=[Variable.RADIUS, Variable.VELOCITY],
        result_variable=Variable.PERIOD,
        calc=lambda env: (2 * math.pi * env[Variable.RADIUS]) / env[Variable.VELOCITY],
        pretty="T = (2π·R) / v"
    ),
    Formula(
        id="T_period = 2 * pi * m / (q * B)", section="magnetism",
        requires=[Variable.MASS, Variable.CHARGE, Variable.MAGNETIC_FIELD],
        result_variable=Variable.PERIOD,
        calc=lambda env: (2 * math.pi * env[Variable.MASS]) / (env[Variable.CHARGE] * env[Variable.MAGNETIC_FIELD]),
        pretty="T = (2π·m) / (q·B)"
    ),
    Formula(
        id="Phi = B * S_area", section="magnetism",
        requires=[Variable.MAGNETIC_FIELD, Variable.AREA],
        result_variable=Variable.MAGNETIC_FLUX,
        calc=lambda env: env[Variable.MAGNETIC_FIELD] * env[Variable.AREA],
        pretty="Φ = B·S"
    ),
    Formula(
        id="B = Phi / S_area", section="magnetism",
        requires=[Variable.MAGNETIC_FLUX, Variable.AREA],
        result_variable=Variable.MAGNETIC_FIELD,
        calc=lambda env: env[Variable.MAGNETIC_FLUX] / env[Variable.AREA],
        pretty="B = Φ / S"
    ),
    Formula(
        id="E_ind = delta_Phi / delta_t", section="magnetism",
        requires=[Variable.FLUX_DELTA, Variable.TIME_DELTA],
        result_variable=Variable.INDUCED_EMF,
        calc=lambda env: env[Variable.FLUX_DELTA] / env[Variable.TIME_DELTA],
        pretty="ℰ = ΔΦ / Δt"
    ),
    Formula(
        id="W_mag = L_ind * I^2 / 2", section="magnetism",
        requires=[Variable.INDUCTANCE, Variable.CURRENT],
        result_variable=Variable.MAGNETIC_ENERGY,
        calc=lambda env: (env[Variable.INDUCTANCE] * (env[Variable.CURRENT] ** 2)) / 2,
        pretty="W = (L·I²) / 2"
    ),
    Formula(
        id="T = 2 * pi * sqrt(L_ind * C)", section="oscillations",
        requires=[Variable.INDUCTANCE, Variable.CAPACITANCE],
        result_variable=Variable.THOMSON_PERIOD,
        calc=lambda env: 2 * math.pi * math.sqrt(env[Variable.INDUCTANCE] * env[Variable.CAPACITANCE]),
        pretty="T = 2π·√(L·C)"
    ),
    Formula(
        id="T = 2 * pi * sqrt(m / k)", section="oscillations",
        requires=[Variable.MASS, Variable.STIFFNESS],
        result_variable=Variable.PERIOD,
        calc=lambda env: 2 * math.pi * math.sqrt(env[Variable.MASS] / env[Variable.STIFFNESS]),
        pretty="T = 2π·√(m / k)"
    ),
    Formula(
        id="T = 2 * pi * sqrt(l / g)", section="oscillations",
        requires=[Variable.LENGTH],
        result_variable=Variable.PERIOD,
        calc=lambda env: 2 * math.pi * math.sqrt(env[Variable.LENGTH] / CONSTANTS["g"]),
        pretty="T = 2π·√(l / g)"
    ),
    Formula(
        id="v_wave = lambda_wave * nu_freq", section="oscillations",
        requires=[Variable.WAVELENGTH, Variable.FREQUENCY],
        result_variable=Variable.WAVE_SPEED,
        calc=lambda env: env[Variable.WAVELENGTH] * env[Variable.FREQUENCY],
        pretty="v = λ·ν"
    ),

    # =========================================================
    # 8. ОПТИКА И КВАНТЫ
    # =========================================================
    Formula(
        id="n = c / v", section="optics",
        requires=[Variable.LIGHT_SPEED_MEDIUM],
        result_variable=Variable.REFRACTIVE_INDEX,
        calc=lambda env: CONSTANTS["c_light"] / env[Variable.LIGHT_SPEED_MEDIUM],
        pretty="n = c / v"
    ),
    Formula(
        id="v_light = c / n", section="optics",
        requires=[Variable.REFRACTIVE_INDEX],
        result_variable=Variable.LIGHT_SPEED_MEDIUM,
        calc=lambda env: CONSTANTS["c_light"] / env[Variable.REFRACTIVE_INDEX],
        pretty="v = c / n"
    ),
    Formula(
        id="1 / F = 1 / d + 1 / f", section="optics",
        requires=[Variable.OBJECT_DISTANCE, Variable.IMAGE_DISTANCE],
        result_variable=Variable.FOCAL_LENGTH,
        calc=lambda env: 1.0 / ((1.0 / env[Variable.OBJECT_DISTANCE]) + (1.0 / env[Variable.IMAGE_DISTANCE])),
        pretty="1/F = 1/d + 1/f"
    ),
    Formula(
        id="D = 1 / F", section="optics",
        requires=[Variable.FOCAL_LENGTH],
        result_variable=Variable.OPTICAL_POWER,
        calc=lambda env: 1.0 / env[Variable.FOCAL_LENGTH],
        pretty="D = 1 / F"
    ),
    Formula(
        id="F_opt = 1 / D", section="optics",
        requires=[Variable.OPTICAL_POWER],
        result_variable=Variable.FOCAL_LENGTH,
        calc=lambda env: 1.0 / env[Variable.OPTICAL_POWER],
        pretty="F = 1 / D"
    ),
    Formula(
        id="f = d * F_opt / (d - F_opt)", section="optics",
        requires=[Variable.OBJECT_DISTANCE, Variable.FOCAL_LENGTH],
        result_variable=Variable.IMAGE_DISTANCE,
        calc=lambda env: (env[Variable.OBJECT_DISTANCE] * env[Variable.FOCAL_LENGTH]) / (env[Variable.OBJECT_DISTANCE] - env[Variable.FOCAL_LENGTH]),
        pretty="f = (d·F) / (d − F)"
    ),
    Formula(
        id="Gamma = f / d", section="optics",
        requires=[Variable.IMAGE_DISTANCE, Variable.OBJECT_DISTANCE],
        result_variable=Variable.MAGNIFICATION,
        calc=lambda env: env[Variable.IMAGE_DISTANCE] / env[Variable.OBJECT_DISTANCE],
        pretty="Γ = f / d"
    ),
    Formula(
        id="d_lattice * sin(alpha) = k_order * lambda_wave", section="optics",
        requires=[Variable.DIFFRACTION_D, Variable.DIFFRACTION_ORDER],  # угол альфа вычисляется в расширенной тригонометрии
        result_variable=Variable.WAVELENGTH,
        calc=lambda env: env[Variable.DIFFRACTION_D] / env[Variable.DIFFRACTION_ORDER],
        pretty="d·sin(α) = k·λ"
    ),
    Formula(
        id="E = h * nu_freq", section="quantum",
        requires=[Variable.FREQUENCY],
        result_variable=Variable.PHOTON_ENERGY,
        calc=lambda env: CONSTANTS["h"] * env[Variable.FREQUENCY],
        pretty="E = h·ν"
    ),
    Formula(
        id="E_k = h * nu_freq - A_vyh", section="quantum",
        requires=[Variable.FREQUENCY, Variable.WORK_FUNCTION],
        result_variable=Variable.ELECTRON_KINETIC,
        calc=lambda env: CONSTANTS["h"] * env[Variable.FREQUENCY] - env[Variable.WORK_FUNCTION],
        pretty="Eк = h·ν − Aвых"
    ),
    Formula(
        id="p = h / lambda_wave", section="quantum",
        requires=[Variable.WAVELENGTH],
        result_variable=Variable.PHOTON_MOMENTUM,
        calc=lambda env: CONSTANTS["h"] / env[Variable.WAVELENGTH],
        pretty="p = h / λ"
    ),
    Formula(
        id="N = N0 * 2^(-t / T_half)", section="quantum",
        requires=[Variable.INITIAL_PARTICLES, Variable.TIME, Variable.HALF_LIFE],
        result_variable=Variable.PARTICLE_COUNT,
        calc=lambda env: env[Variable.INITIAL_PARTICLES] * (2.0 ** (-env[Variable.TIME] / env[Variable.HALF_LIFE])),
        pretty="N = N₀·2^(−t / T½)"
    ),
    Formula(
        id="E = m * c^2", section="quantum",
        requires=[Variable.MASS],
        result_variable=Variable.REST_ENERGY,
        calc=lambda env: env[Variable.MASS] * (CONSTANTS["c_light"] ** 2),
        pretty="E = m·c²"
    ),
    Formula(
        id="Delta_E = Delta_m * c^2", section="quantum",
        requires=[Variable.MASS_DEFECT],
        result_variable=Variable.ENERGY_DEFECT,
        calc=lambda env: env[Variable.MASS_DEFECT] * (CONSTANTS["c_light"] ** 2),
        pretty="ΔE = Δm·c²"
    ),

    # =========================================================
    # ВЛАЖНОСТЬ ВОЗДУХА
    # =========================================================
    Formula(
        id="phi = (p / p_sat) * 100", section="mkt_thermo",
        requires=[Variable.VAPOR_PRESSURE, Variable.SATURATED_VAPOR_PRESSURE],
        result_variable=Variable.HUMIDITY,
        calc=lambda env: env[Variable.VAPOR_PRESSURE] / env[Variable.SATURATED_VAPOR_PRESSURE],
        pretty="φ = p / pнас"
    ),
    Formula(
        id="p = (phi * p_sat)", section="mkt_thermo",
        requires=[Variable.HUMIDITY, Variable.SATURATED_VAPOR_PRESSURE],
        result_variable=Variable.VAPOR_PRESSURE,
        calc=lambda env: env[Variable.HUMIDITY] * env[Variable.SATURATED_VAPOR_PRESSURE],
        pretty="p = φ·pнас"
    ),
    Formula(
        id="phi = (rho / rho_sat) * 100", section="mkt_thermo",
        requires=[Variable.VAPOR_DENSITY, Variable.SATURATED_VAPOR_DENSITY],
        result_variable=Variable.HUMIDITY,
        calc=lambda env: env[Variable.VAPOR_DENSITY] / env[Variable.SATURATED_VAPOR_DENSITY],
        pretty="φ = ρ / ρнас"
    ),

    # =========================================================
    # ДВИЖЕНИЕ ПРОВОДНИКА В МАГНИТНОМ ПОЛЕ
    # =========================================================
    Formula(
        id="E_ind = B * v * l", section="magnetism",
        requires=[Variable.MAGNETIC_FIELD, Variable.VELOCITY, Variable.LENGTH],
        result_variable=Variable.INDUCED_EMF,
        calc=lambda env: env[Variable.MAGNETIC_FIELD] * env[Variable.VELOCITY] * env[Variable.LENGTH],
        pretty="ℰ = B·v·l"
    ),

    # =========================================================
    # ФОТОЭФФЕКТ: ЗАДЕРЖИВАЮЩЕЕ НАПРЯЖЕНИЕ И КРАСНАЯ ГРАНИЦА
    # =========================================================
    Formula(
        id="E_k = e * U_stop", section="quantum",
        requires=[Variable.STOPPING_VOLTAGE],
        result_variable=Variable.ELECTRON_KINETIC,
        calc=lambda env: CONSTANTS.get("e_charge", CONSTANTS.get("e", 1.602176634e-19)) * env[Variable.STOPPING_VOLTAGE],
        pretty="Eк = e·Uзад"
    ),
    Formula(
        id="U_stop = E_k / e", section="quantum",
        requires=[Variable.ELECTRON_KINETIC],
        result_variable=Variable.STOPPING_VOLTAGE,
        calc=lambda env: env[Variable.ELECTRON_KINETIC] / CONSTANTS.get("e_charge", CONSTANTS.get("e", 1.602176634e-19)),
        pretty="Uзад = Eк / e"
    ),
    Formula(
        id="nu_red = A_vyh / h", section="quantum",
        requires=[Variable.WORK_FUNCTION],
        result_variable=Variable.RED_LIMIT_FREQ,
        calc=lambda env: env[Variable.WORK_FUNCTION] / CONSTANTS["h"],
        pretty="νкр = Aвых / h"
    ),

    # =========================================================
    # АКТИВНОСТЬ И РАСПАД
    # =========================================================
    Formula(
        id="activity = lambda_decay * N", section="quantum",
        requires=[Variable.DECAY_CONSTANT, Variable.PARTICLE_COUNT],
        result_variable=Variable.ACTIVITY,
        calc=lambda env: env[Variable.DECAY_CONSTANT] * env[Variable.PARTICLE_COUNT],
        pretty="A = λ·N"
    ),

    # =========================================================================
    # МАТЕМАТИЧЕСКИЙ АНАЛИЗ В ФИЗИКЕ (ПРОИЗВОДНЫЕ И ИНТЕГРАЛЫ)
    # =========================================================================

    # 1. Символьное дифференцирование: v(t) = dx/dt
    Formula(
        id="v(t) = diff(x(t), t)",
        section="calculus",
        requires=[Variable.POSITION_FUNC],
        result_variable=Variable.VELOCITY_FUNC,
        calc=lambda env: env[Variable.POSITION_FUNC].diff("t"),
        pretty="v(t) = x'(t)"
    ),

    # 2. Символьное дифференцирование: a(t) = dv/dt
    Formula(
        id="a(t) = diff(v(t), t)",
        section="calculus",
        requires=[Variable.VELOCITY_FUNC],
        result_variable=Variable.ACCELERATION_FUNC,
        calc=lambda env: env[Variable.VELOCITY_FUNC].diff("t"),
        pretty="a(t) = v'(t)"
    ),

    # 3. Символьное дифференцирование: E_ind(t) = -dPhi/dt
    Formula(
        id="E_ind(t) = -diff(Phi(t), t)",
        section="calculus",
        requires=[Variable.MAGNETIC_FLUX_FUNC],
        result_variable=Variable.EMF,
        calc=lambda env: -env[Variable.MAGNETIC_FLUX_FUNC].diff("t"),
        pretty="ℰ(t) = -Φ'(t)"
    ),

    # 4. Вычисление координаты в момент времени t: x = x(t)
    Formula(
        id="x = x(t)_eval",
        section="calculus",
        requires=[Variable.POSITION_FUNC, Variable.TIME],
        result_variable=Variable.DISTANCE,
        calc=lambda env: env[Variable.POSITION_FUNC].eval({"t": env[Variable.TIME]}),
        pretty="x = x(t)"
    ),

    # 5. Вычисление скорости в момент времени t: v = v(t)
    Formula(
        id="v = v(t)_eval",
        section="calculus",
        requires=[Variable.VELOCITY_FUNC, Variable.TIME],
        result_variable=Variable.VELOCITY,
        calc=lambda env: env[Variable.VELOCITY_FUNC].eval({"t": env[Variable.TIME]}),
        pretty="v = v(t)"
    ),

    # 6. Вычисление ускорения в момент времени t: a = a(t)
    Formula(
        id="a = a(t)_eval",
        section="calculus",
        requires=[Variable.ACCELERATION_FUNC, Variable.TIME],
        result_variable=Variable.ACCELERATION,
        calc=lambda env: env[Variable.ACCELERATION_FUNC].eval({"t": env[Variable.TIME]}),
        pretty="a = a(t)"
    ),

    # 7. Интеграл переменной силы: Работа A = ∫ F(x) dx от x1 до x2
    Formula(
        id="A = int(F(x), x1, x2)",
        section="calculus",
        requires=[Variable.FORCE_FUNC, Variable.COORD_START, Variable.COORD_END],
        result_variable=Variable.WORK,
        calc=lambda env: env[Variable.FORCE_FUNC].definite_integral(
            "x", env[Variable.COORD_START], env[Variable.COORD_END]
        ),
        pretty="A = ∫ F(x) dx [x₁ → x₂]"
    ),

    # 8. Интеграл переменного тока: Заряд q = ∫ i(t) dt от t1 до t2
    Formula(
        id="q = int(i(t), t1, t2)",
        section="calculus",
        requires=[Variable.CURRENT_FUNC, Variable.TIME_START, Variable.TIME_END],
        result_variable=Variable.CHARGE,
        calc=lambda env: env[Variable.CURRENT_FUNC].definite_integral(
            "t", env[Variable.TIME_START], env[Variable.TIME_END]
        ),
        pretty="q = ∫ i(t) dt [t₁ → t₂]"
    ),
    # =========================================================
    # МОСТЫ И ОБРАТНЫЕ ФОРМУЛЫ ДЛЯ ЦЕПОЧЕК
    # =========================================================

    # 1. Мосты эквивалентности потенциалов и напряжений
    Formula(
        id="U = E_ind", section="electro_dynamics",
        requires=[Variable.INDUCED_EMF],
        result_variable=Variable.VOLTAGE,
        calc=lambda env: env[Variable.INDUCED_EMF],
        pretty="U = ℰ"
    ),
    Formula(
        id="U = E_emf", section="electro_dynamics",
        requires=[Variable.EMF],
        result_variable=Variable.VOLTAGE,
        calc=lambda env: env[Variable.EMF],
        pretty="U = ℰ"
    ),
    Formula(
        id="U = U_stop", section="quantum",
        requires=[Variable.STOPPING_VOLTAGE],
        result_variable=Variable.VOLTAGE,
        calc=lambda env: env[Variable.STOPPING_VOLTAGE],
        pretty="U = Uзад"
    ),

    # 2. Мосты теплоты (термодинамика -> тепловые машины)
    Formula(
        id="Q1_hot = Q", section="efficiency",
        requires=[Variable.HEAT],
        result_variable=Variable.HEAT_HOT,
        calc=lambda env: env[Variable.HEAT],
        pretty="Q₁ = Q"
    ),
    Formula(
        id="Q_joule = Q", section="electro_dynamics",
        requires=[Variable.HEAT],
        result_variable=Variable.JOULE_HEAT,
        calc=lambda env: env[Variable.HEAT],
        pretty="Qдж = Q"
    ),
    Formula(
        id="Q = Q_joule", section="electro_dynamics",
        requires=[Variable.JOULE_HEAT],
        result_variable=Variable.HEAT,
        calc=lambda env: env[Variable.JOULE_HEAT],
        pretty="Q = Qдж"
    ),

    # 3. Обратная формула скорости в магнитном поле: v = q*B*R / m
    Formula(
        id="v = q * B * R / m", section="magnetism",
        requires=[Variable.CHARGE, Variable.MAGNETIC_FIELD, Variable.RADIUS, Variable.MASS],
        result_variable=Variable.VELOCITY,
        calc=lambda env: (env[Variable.CHARGE] * env[Variable.MAGNETIC_FIELD] * env[Variable.RADIUS]) / env[Variable.MASS],
        pretty="v = (q·B·R) / m"
    ),

    # 4. Мост работы и энергии: A = Delta_Ek
    Formula(
        id="A = E_k", section="mechanics",
        requires=[Variable.KINETIC_ENERGY],
        result_variable=Variable.WORK,
        calc=lambda env: env[Variable.KINETIC_ENERGY],
        pretty="A = Eк"
    ),

    # 5. Интеграл ускорения: v = ∫ a(t) dt от t1 до t2
    Formula(
        id="v = int(a(t), t1, t2)",
        section="calculus",
        requires=[Variable.ACCELERATION_FUNC, Variable.TIME_START, Variable.TIME_END],
        result_variable=Variable.VELOCITY,
        calc=lambda env: env[Variable.ACCELERATION_FUNC].definite_integral(
            "t", env[Variable.TIME_START], env[Variable.TIME_END]
        ),
        pretty="v = ∫ a(t) dt [t₁ → t₂]"
    ),
]

FORMULAS: Dict[str, Formula] = {f.id: f for f in FORMULAS_LIST}