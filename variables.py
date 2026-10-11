# variables.py
from enum import Enum


class Variable(Enum):
    # --- Механика: кинематика и динамика ---
    DISTANCE = "distance"
    VELOCITY = "velocity"
    INITIAL_VELOCITY = "initial_velocity"
    ACCELERATION = "acceleration"
    CENTRIPETAL_ACC = "centripetal_acceleration"
    TIME = "time"
    TIME_DELTA = "time_delta"
    MASS = "mass"
    MASS_1 = "mass_1"
    MASS_2 = "mass_2"
    FORCE = "force"
    FRICTION_FORCE = "friction_force"
    GRAVITY_FORCE = "gravity_force"
    GRAVITATIONAL_FORCE = "gravitational_force"
    FIRST_COSMIC_VEL = "first_cosmic_velocity"
    ELASTIC_FORCE = "elastic_force"
    STIFFNESS = "stiffness"
    ELONGATION = "elongation"
    HEIGHT = "height"
    FRICTION_COEFF = "friction_coeff"
    LENGTH = "length"
    RADIUS = "radius"
    MOMENTUM = "momentum"
    WORK = "work"
    USEFUL_WORK = "useful_work"
    TOTAL_WORK = "total_work"
    POWER = "power"
    KINETIC_ENERGY = "kinetic_energy"
    POTENTIAL_ENERGY = "potential_energy"
    MECHANICAL_ENERGY = "mechanical_energy"
    TORQUE = "torque"
    EFFICIENCY = "efficiency"
    CARNOT_EFFICIENCY = "carnot_efficiency"
    PERIOD = "period"
    FREQUENCY = "frequency"
    ANGULAR_VELOCITY = "angular_velocity"

    # --- Гидростатика ---
    ARCHIMEDES_FORCE = "archimedes_force"
    HYDROSTATIC_PRESSURE = "hydrostatic_pressure"

    # --- Новые функциональные переменные (матанализ) ---
    POSITION_FUNC = "position_func"          # x(t)
    VELOCITY_FUNC = "velocity_func"          # v(t)
    ACCELERATION_FUNC = "acceleration_func"  # a(t)
    FORCE_FUNC = "force_func"                # F(x) или F(t)
    CURRENT_FUNC = "current_func"            # i(t)
    MAGNETIC_FLUX_FUNC = "flux_func"         # Phi(t)
    COORD_START = "coord_start"              # x1
    COORD_END = "coord_end"                  # x2
    TIME_START = "time_start"                # t1
    TIME_END = "time_end"                    # t2

    # --- МКТ и термодинамика ---
    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    TEMP_HOT = "temp_hot"
    TEMP_COLD = "temp_cold"
    VOLUME = "volume"
    DENSITY = "density"
    MOLE_AMOUNT = "mole_amount"
    INTERNAL_ENERGY = "internal_energy"
    HEAT = "heat"
    HEAT_HOT = "heat_hot"
    HEAT_COLD = "heat_cold"
    SPECIFIC_HEAT = "specific_heat"
    FUSION_HEAT = "fusion_heat"
    VAPOR_HEAT = "vapor_heat"
    CONCENTRATION = "concentration"
    MOLECULE_KINETIC = "molecule_kinetic"
    HUMIDITY = "humidity"
    VAPOR_PRESSURE = "vapor_pressure"
    SATURATED_VAPOR_PRESSURE = "saturated_vapor_pressure"
    VAPOR_DENSITY = "vapor_density"
    SATURATED_VAPOR_DENSITY = "saturated_vapor_density"

    # --- Электродинамика и цепи ---
    CURRENT = "current"
    SHORT_CIRCUIT_CURRENT = "short_circuit_current"
    VOLTAGE = "voltage"
    RESISTANCE = "resistance"
    INTERNAL_RESISTANCE = "internal_resistance"
    EMF = "emf"
    CHARGE = "charge"
    CHARGE_1 = "charge_1"
    CHARGE_2 = "charge_2"
    CAPACITANCE = "capacitance"
    ELECTRIC_FIELD = "electric_field"
    ELECTRIC_ENERGY = "electric_energy"
    ELECTRIC_POWER = "electric_power"
    JOULE_HEAT = "joule_heat"
    RESISTIVITY = "resistivity"
    WIRE_AREA = "wire_area"

    # --- Магнетизм и колебания ---
    MAGNETIC_FIELD = "magnetic_field"
    MAGNETIC_FLUX = "magnetic_flux"
    FLUX_DELTA = "flux_delta"
    INDUCTANCE = "inductance"
    INDUCED_EMF = "induced_emf"
    MAGNETIC_ENERGY = "magnetic_energy"
    AMPERE_FORCE = "ampere_force"
    LORENTZ_FORCE = "lorentz_force"
    COULOMB_FORCE = "coulomb_force"
    THOMSON_PERIOD = "thomson_period"
    WAVE_SPEED = "wave_speed"

    # --- Оптика ---
    WAVELENGTH = "wavelength"
    OBJECT_DISTANCE = "object_distance"
    IMAGE_DISTANCE = "image_distance"
    FOCAL_LENGTH = "focal_length"
    OPTICAL_POWER = "optical_power"
    MAGNIFICATION = "magnification"
    DIFFRACTION_D = "diffraction_d"
    DIFFRACTION_ORDER = "diffraction_order"
    REFRACTIVE_INDEX = "refractive_index"
    LIGHT_SPEED_MEDIUM = "light_speed_medium"

    # --- Квантовая и ядерная физика ---
    WORK_FUNCTION = "work_function"
    PHOTON_ENERGY = "photon_energy"
    PHOTON_MOMENTUM = "photon_momentum"
    ELECTRON_KINETIC = "electron_kinetic"
    STOPPING_VOLTAGE = "stopping_voltage"
    RED_LIMIT_FREQ = "red_limit_freq"
    HALF_LIFE = "half_life"
    INITIAL_PARTICLES = "initial_particles"
    PARTICLE_COUNT = "particle_count"
    ACTIVITY = "activity"
    DECAY_CONSTANT = "decay_constant"
    REST_ENERGY = "rest_energy"
    MASS_DEFECT = "mass_defect"
    ENERGY_DEFECT = "energy_defect"
    AREA = "area"