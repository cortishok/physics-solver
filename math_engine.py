import ast
import math
import operator
import re
from typing import Callable, Dict, Any
from variables import Variable
from constants import CONSTANTS

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_ctg(x: float) -> float:
    t = math.tan(x)
    if abs(t) < 1e-15:
        raise ValueError("Математическая ошибка: котангенс не определён (деление на 0)")
    return 1.0 / t


SAFE_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "tg": math.tan,
    "ctg": _safe_ctg,
    "asin": math.asin,
    "arcsin": math.asin,
    "acos": math.acos,
    "arccos": math.acos,
    "atan": math.atan,
    "arctg": math.atan,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "ln": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "abs": abs,
}

# Сортируем имена функций по убыванию длины для корректной расстановки знаков '*'
_FUNC_NAMES_SORTED = sorted(SAFE_FUNCTIONS.keys(), key=len, reverse=True)
_FUNC_PATTERN = "|".join(_FUNC_NAMES_SORTED)


def _insert_implicit_multiplication(s: str) -> str:
    """
    Препроцессор неявного умножения для школьной записи:
    '2t' -> '2*t', '2sin(t)' -> '2*sin(t)', '2(t+1)' -> '2*(t+1)',
    ')(x)' -> ')*(x)', 't(t+1)' -> 't*(t+1)' (не трогая вызовы функций sin(t)).
    """
    # 1. Между цифрой и буквой или открывающей скобкой (кроме экспоненты 1e-5, 2e10)
    s = re.sub(r"(\d(?<!e)(?<!E))\s*([a-zA-Z(])", lambda m: (
        m.group(0) if m.group(2) in ("e", "E") and re.match(r"^[eE][+-]?\d", s[m.start(2):])
        else f"{m.group(1)}*{m.group(2)}"
    ), s)

    # 2. Между закрывающей скобкой и буквой, цифрой или открывающей скобкой: )( -> )*(
    s = re.sub(r"(\))\s*([a-zA-Z0-9(])", r"\1*\2", s)

    # 3. Между одиночной переменной (не именем функции!) и открывающей скобкой: t( -> t*(
    def _var_paren_repl(match: re.Match) -> str:
        word = match.group(1)
        if word in SAFE_FUNCTIONS:
            return f"{word}("
        return f"{word}*("

    s = re.sub(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", _var_paren_repl, s)
    return s


def normalize_expr(expr: str) -> str:
    """Заменяет '^' на '**', расставляет неявное умножение и проверяет синтаксис AST."""
    if not isinstance(expr, str):
        raise ValueError("Ошибка синтаксиса выражения")
    cleaned = expr.strip().replace("^", "**")
    cleaned = _insert_implicit_multiplication(cleaned)
    try:
        ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Ошибка синтаксиса в формуле '{expr}': {exc}") from exc
    return cleaned


def _real_pow(left: float, right: float) -> float:
    """Возведение в степень с поддержкой нечётных корней из отрицательных чисел: (-8)^(1/3) = -2."""
    if left == 0.0 and right < 0.0:
        raise ZeroDivisionError("Математическая ошибка: 0 в отрицательной степени")
    if left < 0.0 and not float(right).is_integer():
        # Проверяем, является ли показатель нечётным корнем вида p / q (где q нечётное)
        inv = round(1.0 / right) if abs(right) > 1e-9 else 0
        if inv != 0 and abs(right - 1.0 / inv) < 1e-7 and inv % 2 != 0:
            return -((-left) ** right)
        raise ValueError("Математическая ошибка: корень чётной степени из отрицательного числа")
    return float(left ** right)


def eval_ast(expr: str, env: dict | None = None) -> float:
    """Безопасное вычисление математического выражения через AST с поддержкой констант и проверкой ОДЗ."""
    cleaned = normalize_expr(expr)
    tree = ast.parse(cleaned, mode="eval")

    variables = dict(CONSTANTS)
    if env:
        variables.update(env)

    def _eval(node) -> float:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in variables:
                return float(variables[node.id])
            raise ValueError(f"Неизвестная переменная '{node.id}' в выражении")
        if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Div):
                if abs(right) == 0.0:
                    raise ZeroDivisionError("Математическая ошибка: деление на 0")
                return float(left / right)
            if isinstance(node.op, ast.Pow):
                return _real_pow(left, right)
            return float(SAFE_OPERATORS[type(node.op)](left, right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
            return float(SAFE_OPERATORS[type(node.op)](_eval(node.operand)))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in SAFE_FUNCTIONS:
                raise ValueError(f"Неизвестная функция '{func_name}'")
            if len(node.args) != 1:
                raise ValueError(f"Функция '{func_name}' принимает ровно 1 аргумент")
            arg_val = _eval(node.args[0])

            # Явная проверка области определения (ОДЗ) функций
            if func_name == "sqrt" and arg_val < 0:
                raise ValueError(f"Математическая ошибка: корень из отрицательного числа ({arg_val})")
            if func_name in ("asin", "arcsin", "acos", "arccos") and (arg_val < -1.0 or arg_val > 1.0):
                raise ValueError(
                    f"Математическая ошибка: аргумент {func_name}({arg_val}) вне диапазона [-1; 1]"
                )
            if func_name in ("log", "ln", "log10", "log2") and arg_val <= 0:
                raise ValueError(
                    f"Математическая ошибка: логарифм неположительного числа ({arg_val})"
                )

            try:
                return float(SAFE_FUNCTIONS[func_name](arg_val))
            except ValueError as exc:
                raise ValueError(
                    f"Математическая ошибка: недопустимый аргумент для функции '{func_name}'"
                ) from exc
        raise ValueError("Недопустимая конструкция синтаксиса AST")

    return _eval(tree)


# --- СИМВОЛЬНОЕ ДИФФЕРЕНЦИРОВАНИЕ ---

def symbolic_derivative_str(expr: str, var: str = "t") -> str:
    """
    Аналитическое дифференцирование полиномов, тригонометрии, корней,
    экспонент и логарифмов по переменной t.
    """
    cleaned = normalize_expr(expr)
    tree = ast.parse(cleaned, mode="eval")

    def _diff(node):
        if isinstance(node, ast.Constant):
            return ast.Constant(value=0.0)
        if isinstance(node, ast.Name):
            return ast.Constant(value=1.0 if node.id == var else 0.0)
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return ast.UnaryOp(op=ast.USub(), operand=_diff(node.operand))
            if isinstance(node.op, ast.UAdd):
                return _diff(node.operand)
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub)):
                return ast.BinOp(left=_diff(node.left), op=node.op, right=_diff(node.right))
            if isinstance(node.op, ast.Mult):
                term1 = ast.BinOp(left=_diff(node.left), op=ast.Mult(), right=node.right)
                term2 = ast.BinOp(left=node.left, op=ast.Mult(), right=_diff(node.right))
                return ast.BinOp(left=term1, op=ast.Add(), right=term2)
            if isinstance(node.op, ast.Div):
                u_d = _diff(node.left)
                v_d = _diff(node.right)
                num = ast.BinOp(
                    left=ast.BinOp(left=u_d, op=ast.Mult(), right=node.right),
                    op=ast.Sub(),
                    right=ast.BinOp(left=node.left, op=ast.Mult(), right=v_d),
                )
                den = ast.BinOp(left=node.right, op=ast.Pow(), right=ast.Constant(value=2.0))
                return ast.BinOp(left=num, op=ast.Div(), right=den)
            if isinstance(node.op, ast.Pow):
                # Случай u(t)^n (степенная функция с константным показателем)
                if isinstance(node.right, ast.Constant):
                    n = node.right.value
                    if n == 0:
                        return ast.Constant(value=0.0)
                    base_pow = (
                        node.left
                        if n == 2
                        else ast.BinOp(left=node.left, op=ast.Pow(), right=ast.Constant(value=n - 1))
                    )
                    coeff = ast.BinOp(left=ast.Constant(value=n), op=ast.Mult(), right=base_pow)
                    return ast.BinOp(left=coeff, op=ast.Mult(), right=_diff(node.left))
                # Случай a^u(t) (показательная функция с константным основанием)
                if isinstance(node.left, ast.Constant) and node.left.value > 0:
                    ln_a = ast.Constant(value=round(math.log(node.left.value), 6))
                    pow_term = ast.BinOp(left=node, op=ast.Mult(), right=ln_a)
                    return ast.BinOp(left=pow_term, op=ast.Mult(), right=_diff(node.right))

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn = node.func.id
            arg = node.args[0]
            arg_d = _diff(arg)
            if fn == "sin":
                cos_call = ast.Call(func=ast.Name(id="cos", ctx=ast.Load()), args=[arg], keywords=[])
                return ast.BinOp(left=cos_call, op=ast.Mult(), right=arg_d)
            if fn == "cos":
                sin_call = ast.Call(func=ast.Name(id="sin", ctx=ast.Load()), args=[arg], keywords=[])
                neg_sin = ast.UnaryOp(op=ast.USub(), operand=sin_call)
                return ast.BinOp(left=neg_sin, op=ast.Mult(), right=arg_d)
            if fn in ("tan", "tg"):
                cos_call = ast.Call(func=ast.Name(id="cos", ctx=ast.Load()), args=[arg], keywords=[])
                cos_sq = ast.BinOp(left=cos_call, op=ast.Pow(), right=ast.Constant(value=2.0))
                return ast.BinOp(left=arg_d, op=ast.Div(), right=cos_sq)
            if fn == "sqrt":
                sqrt_call = ast.Call(func=ast.Name(id="sqrt", ctx=ast.Load()), args=[arg], keywords=[])
                denom = ast.BinOp(left=ast.Constant(value=2.0), op=ast.Mult(), right=sqrt_call)
                return ast.BinOp(left=arg_d, op=ast.Div(), right=denom)
            if fn == "exp":
                exp_call = ast.Call(func=ast.Name(id="exp", ctx=ast.Load()), args=[arg], keywords=[])
                return ast.BinOp(left=exp_call, op=ast.Mult(), right=arg_d)
            if fn in ("log", "ln"):
                return ast.BinOp(left=arg_d, op=ast.Div(), right=arg)
            if fn in ("atan", "arctg"):
                arg_sq = ast.BinOp(left=arg, op=ast.Pow(), right=ast.Constant(value=2.0))
                denom = ast.BinOp(left=ast.Constant(value=1.0), op=ast.Add(), right=arg_sq)
                return ast.BinOp(left=arg_d, op=ast.Div(), right=denom)

        raise ValueError(f"Не удалось продифференцировать выражение '{expr}'")

    diff_tree = ast.Expression(body=_simplify_ast(_diff(tree.body)))
    raw = ast.unparse(diff_tree).replace("**", "^")
    return simplify_polynomial_str(raw, var)


def _simplify_ast(node):
    """Безопасное сворачивание констант, нулей и единиц в AST-дереве."""
    if isinstance(node, ast.BinOp):
        left = _simplify_ast(node.left)
        right = _simplify_ast(node.right)
        if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
            try:
                # Защита от зависания на гигантских степенях
                if isinstance(node.op, ast.Pow) and abs(right.value) > 100:
                    return ast.BinOp(left=left, op=node.op, right=right)
                val = SAFE_OPERATORS[type(node.op)](left.value, right.value)
                if isinstance(val, complex) or not math.isfinite(float(val)):
                    return ast.BinOp(left=left, op=node.op, right=right)
                return ast.Constant(value=int(val) if float(val).is_integer() else val)
            except Exception:
                return ast.BinOp(left=left, op=node.op, right=right)
        if isinstance(node.op, ast.Mult):
            if (isinstance(left, ast.Constant) and left.value == 0) or (
                isinstance(right, ast.Constant) and right.value == 0
            ):
                return ast.Constant(value=0)
            if isinstance(left, ast.Constant) and left.value == 1:
                return right
            if isinstance(right, ast.Constant) and right.value == 1:
                return left
        if isinstance(node.op, ast.Add):
            if isinstance(left, ast.Constant) and left.value == 0:
                return right
            if isinstance(right, ast.Constant) and right.value == 0:
                return left
        if isinstance(node.op, ast.Sub) and isinstance(right, ast.Constant) and right.value == 0:
            return left
        return ast.BinOp(left=left, op=node.op, right=right)
    if isinstance(node, ast.UnaryOp):
        op_node = _simplify_ast(node.operand)
        if isinstance(op_node, ast.Constant):
            if isinstance(node.op, ast.USub):
                return ast.Constant(value=-op_node.value)
            if isinstance(node.op, ast.UAdd):
                return op_node
        return ast.UnaryOp(op=node.op, operand=op_node)
    return node


def simplify_polynomial_str(expr: str, var: str = "t") -> str:
    """
    Приводит полиномиальные выражения до 4-й степени вида '20 + 2*2*t + 3*3*t^2' к '20 + 4*t + 9*t^2'.
    Для тригонометрических, показательных или дробных функций возвращает аккуратное AST-выражение.
    """
    if any(fn in expr for fn in ("sin", "cos", "tan", "tg", "ctg", "sqrt", "exp", "log", "ln", "/")):
        return expr
    try:
        pts = [0.0, 1.0, 2.0, 3.0, 4.0]
        vals = [eval_ast(expr, {var: p}) for p in pts]
        coeffs = [
            vals[0],
            (-25 * vals[0] + 48 * vals[1] - 36 * vals[2] + 16 * vals[3] - 3 * vals[4]) / 12.0,
            (35 * vals[0] - 104 * vals[1] + 114 * vals[2] - 56 * vals[3] + 11 * vals[4]) / 24.0,
            (-5 * vals[0] + 18 * vals[1] - 24 * vals[2] + 14 * vals[3] - 3 * vals[4]) / 12.0,
            (vals[0] - 4 * vals[1] + 6 * vals[2] - 4 * vals[3] + vals[4]) / 24.0,
        ]
        test_t = 1.5
        poly_val = sum(coeffs[i] * (test_t**i) for i in range(5))
        if abs(poly_val - eval_ast(expr, {var: test_t})) > 1e-6:
            return expr

        terms = []
        for deg, c in enumerate(coeffs):
            if abs(c) < 1e-9:
                continue
            c_clean = int(round(c)) if abs(c - round(c)) < 1e-7 else round(c, 6)
            if deg == 0:
                terms.append(f"{c_clean}")
            elif deg == 1:
                if c_clean == 1:
                    terms.append(f"{var}")
                elif c_clean == -1:
                    terms.append(f"-{var}")
                else:
                    terms.append(f"{c_clean}*{var}")
            else:
                if c_clean == 1:
                    terms.append(f"{var}^{deg}")
                elif c_clean == -1:
                    terms.append(f"-{var}^{deg}")
                else:
                    terms.append(f"{c_clean}*{var}^{deg}")
        if not terms:
            return "0"
        res = terms[0]
        for term in terms[1:]:
            if term.startswith("-"):
                res += f" - {term[1:]}"
            else:
                res += f" + {term}"
        return res
    except Exception:
        return expr


def scale_function_str(expr: str, factor: float, var: str = "t") -> str:
    """Умножает аналитическую функцию на скаляр (например, F(t) = m * a(t))."""
    f_clean = int(round(factor)) if abs(factor - round(factor)) < 1e-7 else factor
    scaled_raw = f"({f_clean}) * ({expr})"
    return simplify_polynomial_str(scaled_raw, var)


def definite_integral(expr: str, t_start: float, t_end: float, steps: int = 200) -> float:
    """Численное интегрирование методом Симпсона с гарантией чётности числа шагов."""
    normalize_expr(expr)
    if math.isclose(t_start, t_end):
        return 0.0
    if steps < 2:
        steps = 2
    if steps % 2 != 0:
        steps += 1
    h = (t_end - t_start) / steps
    total = eval_ast(expr, {"t": t_start}) + eval_ast(expr, {"t": t_end})
    for i in range(1, steps):
        t_val = t_start + i * h
        weight = 4.0 if i % 2 == 1 else 2.0
        total += weight * eval_ast(expr, {"t": t_val})
    return total * h / 3.0


# --- РЕШАТЕЛЬ ЛИНЕЙНЫХ СИСТЕМ 2x2 И НЕЯВНЫХ УРАВНЕНИЙ ---

def solve_linear_2x2(a1: float, b1: float, c1: float, a2: float, b2: float, c2: float) -> tuple[float, float]:
    """
    Решает систему линейных уравнений методом Крамера с относительным порогом:
    a1*x + b1*y = c1
    a2*x + b2*y = c2
    """
    det = a1 * b2 - a2 * b1
    scale = max(abs(a1), abs(b1), abs(a2), abs(b2), 1.0)
    if abs(det) < 1e-12 * (scale ** 2):
        raise ValueError("Система уравнений вырождена (определитель равен 0)")
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return x, y


# Переменные, которые по законам физики строго не могут быть отрицательными
# (VELOCITY, VELOCITY_0 и DISPLACEMENT исключены, т.к. проекции могут быть < 0)
NON_NEGATIVE_VARS = {
    Variable.TIME,
    Variable.MASS,
    Variable.MASS_1,
    Variable.MASS_2,
    Variable.RADIUS,
    Variable.HEIGHT,
    Variable.WIRE_LENGTH,
    Variable.WAVELENGTH,
    Variable.FREQ_LIGHT,
    Variable.FREQUENCY_ROT,
    Variable.PERIOD,
    Variable.PARTICLES_COUNT,
}


def solve_implicit_for_var(
    calc_func: Callable[[Dict[Variable, Any]], float],
    known_vars: Dict[Variable, Any],
    target_var: Variable,
    expected_result: float,
) -> float:
    """
    Выражает неизвестную переменную target_var из формулы calc_func.
    Сначала проверяет точное аналитическое решение (для линейных и квадратных зависимостей),
    а затем использует метод Ньютона с контролем конечности и области допустимых значений.
    """
    must_be_positive = target_var in NON_NEGATIVE_VARS

    def f(x: float) -> float:
        test_env = dict(known_vars)
        test_env[target_var] = x
        return float(calc_func(test_env)) - expected_result

    # 1. Проверка на чистый ноль (защита от машинного мусора вида -1.7e-12 при v = v0)
    try:
        val_at_zero = f(0.0)
        scale = max(1.0, abs(expected_result))
        if abs(val_at_zero) <= 1e-11 * scale:
            return 0.0
    except Exception:
        pass

    # 2. Точный аналитический решатель для линейных и квадратных уравнений: A*x^2 + B*x + C = 0
    try:
        y0 = f(0.0)
        y1 = f(1.0)
        y2 = f(2.0)
        y3 = f(3.0)
        # Если третья конечная разность равна 0, функция — точный полином степени <= 2
        d3 = y3 - 3.0 * y2 + 3.0 * y1 - y0
        scale_poly = max(abs(y0), abs(y1), abs(y2), abs(expected_result), 1e-30)
        if abs(d3) <= 1e-9 * scale_poly:
            c_coeff = y0
            a_coeff = 0.5 * (y2 - 2.0 * y1 + y0)
            b_coeff = y1 - y0 - a_coeff

            # Проверка в дробной точке x = 0.5 (отсекаем функции с корнями и синусами)
            y_half_expected = a_coeff * 0.25 + b_coeff * 0.5 + c_coeff
            if abs(f(0.5) - y_half_expected) <= 1e-8 * scale_poly:
                if abs(a_coeff) <= 1e-12 * scale_poly and abs(b_coeff) > 0:
                    # Линейное уравнение B*x + C = 0
                    root = -c_coeff / b_coeff
                    if math.isfinite(root) and (not must_be_positive or root >= -1e-11):
                        return 0.0 if abs(root) < 1e-11 else root
                elif abs(a_coeff) > 1e-12 * scale_poly:
                    # Квадратное уравнение A*x^2 + B*x + C = 0 через дискриминант
                    disc = b_coeff * b_coeff - 4.0 * a_coeff * c_coeff
                    if disc >= -1e-11 * (scale_poly ** 2):
                        sqrt_d = math.sqrt(max(0.0, disc))
                        r1 = (-b_coeff - sqrt_d) / (2.0 * a_coeff)
                        r2 = (-b_coeff + sqrt_d) / (2.0 * a_coeff)
                        roots = sorted([r1, r2])
                        if must_be_positive:
                            pos_roots = [r for r in roots if r >= -1e-11]
                            if pos_roots:
                                chosen = max(0.0, pos_roots[-1] if pos_roots[0] <= 0 else pos_roots[0])
                                return 0.0 if abs(chosen) < 1e-11 else chosen
                        else:
                            # Для скоростей в квадрате (E_k = m*v^2/2) по умолчанию берём положительный модуль
                            pos_roots = [r for r in roots if r >= 0]
                            chosen = pos_roots[-1] if pos_roots else roots[0]
                            return 0.0 if abs(chosen) < 1e-11 else chosen
    except Exception:
        pass

    # 3. Запасной численный метод Ньютона (для дробных, тригонометрических и корневых формул)
    if must_be_positive:
        guesses = [1.0, 10.0, 0.1, 100.0, 1e-5, 1e5, 1e-15, 1e15, 1e-27]
    else:
        guesses = [1.0, 10.0, 0.1, -1.0, -10.0, 100.0, 1e-5, 1e5, 1e-18, 1e15]

    for start_x in guesses:
        x = start_x
        for _ in range(80):
            if not math.isfinite(x):
                break
            try:
                y = f(x)
            except Exception:
                break
            if not math.isfinite(y):
                break

            tol = max(1e-12 * abs(expected_result), 1e-30)
            if abs(y) <= tol:
                if must_be_positive and x < 0:
                    try:
                        if abs(f(abs(x))) <= tol:
                            return abs(x)
                    except Exception:
                        pass
                    break
                if abs(x) < 1e-11 and abs(expected_result) >= 1.0:
                    try:
                        if abs(f(0.0)) <= 1e-9 * abs(expected_result):
                            return 0.0
                    except Exception:
                        pass
                return x

            h = max(abs(x) * 1e-7, 1e-15)
            try:
                y_plus = f(x + h)
                df = (y_plus - y) / h
            except Exception:
                break

            if not math.isfinite(df) or abs(df) == 0.0:
                break

            x_next = x - y / df
            if not math.isfinite(x_next):
                break

            if must_be_positive and x_next < 0:
                x_next = abs(x) * 0.5 if x > 0 else 0.1

            if abs(x_next - x) <= max(1e-12 * abs(x), 1e-30):
                try:
                    if abs(f(x_next)) <= max(1e-9 * abs(expected_result), 1e-26):
                        return max(0.0, x_next) if must_be_positive else x_next
                except Exception:
                    pass
                break
            x = x_next

    raise ValueError(f"Не удалось численно выразить {target_var.value} (возможно, нет физического корня)")
