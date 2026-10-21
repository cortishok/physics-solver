import ast
import math
import operator

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "abs": abs,
}


def normalize_expr(expr: str) -> str:
    """Заменяет '^' на '**' и проверяет базовый синтаксис AST."""
    if not isinstance(expr, str):
        raise ValueError("Ошибка синтаксиса выражения")
    cleaned = expr.strip().replace("^", "**")
    try:
        ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Ошибка синтаксиса в формуле '{expr}': {exc}") from exc
    return cleaned


def eval_ast(expr: str, env: dict | None = None) -> float:
    """Безопасное вычисление математического выражения через AST."""
    cleaned = normalize_expr(expr)
    tree = ast.parse(cleaned, mode="eval")
    variables = env or {}

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in variables:
                return float(variables[node.id])
            if node.id == "pi":
                return math.pi
            if node.id == "e":
                return math.e
            raise ValueError(f"Неизвестная переменная '{node.id}' в выражении")
        if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Div) and abs(right) == 0.0:
                raise ZeroDivisionError("Математическая ошибка: деление на 0")
            if isinstance(node.op, ast.Pow) and left < 0 and not float(right).is_integer():
                raise ValueError("math domain error: корень из отрицательного числа")
            return float(SAFE_OPERATORS[type(node.op)](left, right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
            return float(SAFE_OPERATORS[type(node.op)](_eval(node.operand)))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in SAFE_FUNCTIONS:
                raise ValueError(f"Неизвестная функция '{func_name}'")
            args = [_eval(arg) for arg in node.args]
            return float(SAFE_FUNCTIONS[func_name](*args))
        raise ValueError("Недопустимая конструкция синтаксиса AST")

    return _eval(tree)


# --- СИМВОЛЬНОЕ ДИФФЕРЕНЦИРОВАНИЕ ---

def symbolic_derivative_str(expr: str, var: str = "t") -> str:
    """
    Аналитическое дифференцирование полиномов и тригонометрии по переменной t.
    Возвращает красивую аналитическую строку (например: '20 + 4*t + 9*t^2').
    """
    cleaned = normalize_expr(expr)
    tree = ast.parse(cleaned, mode="eval")

    def _diff(node):
        if isinstance(node, ast.Constant):
            return ast.Constant(value=0.0)
        if isinstance(node, ast.Name):
            return ast.Constant(value=1.0 if node.id == var else 0.0)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return ast.UnaryOp(op=ast.USub(), operand=_diff(node.operand))
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub)):
                return ast.BinOp(left=_diff(node.left), op=node.op, right=_diff(node.right))
            if isinstance(node.op, ast.Mult):
                # (u*v)' = u'*v + u*v'
                term1 = ast.BinOp(left=_diff(node.left), op=ast.Mult(), right=node.right)
                term2 = ast.BinOp(left=node.left, op=ast.Mult(), right=_diff(node.right))
                return ast.BinOp(left=term1, op=ast.Add(), right=term2)
            if isinstance(node.op, ast.Div):
                # (u/v)' = (u'*v - u*v') / v^2
                u_d = _diff(node.left)
                v_d = _diff(node.right)
                num = ast.BinOp(
                    left=ast.BinOp(left=u_d, op=ast.Mult(), right=node.right),
                    op=ast.Sub(),
                    right=ast.BinOp(left=node.left, op=ast.Mult(), right=v_d),
                )
                den = ast.BinOp(left=node.right, op=ast.Pow(), right=ast.Constant(value=2.0))
                return ast.BinOp(left=num, op=ast.Div(), right=den)
            if isinstance(node.op, ast.Pow) and isinstance(node.right, ast.Constant):
                # (u^n)' = n * u^(n-1) * u'
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
        raise ValueError(f"Не удалось продифференцировать выражение '{expr}'")

    diff_tree = ast.Expression(body=_simplify_ast(_diff(tree.body)))
    raw = ast.unparse(diff_tree).replace("**", "^")
    return simplify_polynomial_str(raw, var)


def _simplify_ast(node):
    """Базовое сворачивание нулей и единиц в AST-дереве."""
    if isinstance(node, ast.BinOp):
        left = _simplify_ast(node.left)
        right = _simplify_ast(node.right)
        if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
            val = SAFE_OPERATORS[type(node.op)](left.value, right.value)
            return ast.Constant(value=int(val) if float(val).is_integer() else val)
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
        if isinstance(op_node, ast.Constant) and isinstance(node.op, ast.USub):
            return ast.Constant(value=-op_node.value)
        return ast.UnaryOp(op=node.op, operand=op_node)
    return node


def simplify_polynomial_str(expr: str, var: str = "t") -> str:
    """
    Приводит полиномиальные выражения вида '20 + 2*2*t + 3*3*t^2' к '20 + 4*t + 9*t^2'.
    Для тригонометрических или дробных функций возвращает аккуратное AST-выражение.
    """
    if any(fn in expr for fn in ("sin", "cos", "tan", "sqrt", "exp", "log", "/")):
        return expr
    try:
        # Восстанавливаем коэффициенты полинома до 4-й степени методом конечных разностей
        pts = [0.0, 1.0, 2.0, 3.0, 4.0]
        vals = [eval_ast(expr, {var: p}) for p in pts]
        # Решаем систему для c0 + c1*t + c2*t^2 + c3*t^3 + c4*t^4
        coeffs = [
            vals[0],
            (-25 * vals[0] + 48 * vals[1] - 36 * vals[2] + 16 * vals[3] - 3 * vals[4]) / 12.0,
            (35 * vals[0] - 104 * vals[1] + 114 * vals[2] - 56 * vals[3] + 11 * vals[4]) / 24.0,
            (-5 * vals[0] + 18 * vals[1] - 24 * vals[2] + 14 * vals[3] - 3 * vals[4]) / 12.0,
            (vals[0] - 4 * vals[1] + 6 * vals[2] - 4 * vals[3] + vals[4]) / 24.0,
        ]
        # Проверяем точность полиномиальной аппроксимации в контрольной точке
        test_t = 1.5
        poly_val = sum(coeffs[i] * (test_t**i) for i in range(5))
        if abs(poly_val - eval_ast(expr, {var: test_t})) > 1e-6:
            return expr

        terms = []
        for deg, c in enumerate(coeffs):
            if abs(c) < 1e-9:
                continue
            c_clean = int(round(c)) if abs(c - round(c)) < 1e-7 else round(c, 4)
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
    """Численное интегрирование методом Симпсона с проверкой синтаксиса."""
    normalize_expr(expr)
    if math.isclose(t_start, t_end):
        return 0.0
    h = (t_end - t_start) / steps
    total = eval_ast(expr, {"t": t_start}) + eval_ast(expr, {"t": t_end})
    for i in range(1, steps):
        t_val = t_start + i * h
        weight = 4.0 if i % 2 == 1 else 2.0
        total += weight * eval_ast(expr, {"t": t_val})
    return total * h / 3.0


# --- РЕШАТЕЛЬ ЛИНЕЙНЫХ СИСТЕМ 2x2 И УРАВНЕНИЙ ---

def solve_linear_2x2(a1: float, b1: float, c1: float, a2: float, b2: float, c2: float) -> tuple[float, float]:
    """
    Решает систему линейных уравнений методом Крамера:
    a1*x + b1*y = c1
    a2*x + b2*y = c2
    """
    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-12:
        raise ValueError("Система уравнений вырождена (определитель равен 0)")
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return x, y


def solve_implicit_for_var(calc_fn, known_args: dict, target_var, expected_res: float) -> float:
    """
    Численно-аналитическое обращение формулы:
    находит значение target_var, при котором calc_fn(**known_args, target_var=x) == expected_res.
    Используется для автоматического обращения формул без ручного дублирования.
    """
    def f(x):
        env = dict(known_args)
        env[target_var] = x
        return calc_fn(env) - expected_res

    # Проверяем линейность / монотонность на положительной полуоси (основная область физики)
    guesses = [1.0, 2.0, 10.0, 0.1, 100.0]
    for g0 in guesses:
        try:
            x0 = g0
            for _ in range(40):
                y0 = f(x0)
                if abs(y0) < 1e-9:
                    return x0
                dx = max(abs(x0) * 1e-6, 1e-8)
                dy = (f(x0 + dx) - y0) / dx
                if abs(dy) < 1e-15:
                    break
                x1 = x0 - y0 / dy
                if abs(x1 - x0) < 1e-9 and abs(f(x1)) < 1e-7:
                    return x1
                x0 = x1
        except Exception:
            continue
    raise ValueError("Не удалось однозначно обратить уравнение")