# math_engine.py
from __future__ import annotations
import ast
import math
from typing import Dict, Union


class Expr:
    """Базовый абстрактный класс математического выражения."""

    def diff(self, var: str) -> Expr:
        raise NotImplementedError

    def integrate(self, var: str) -> Expr:
        raise NotImplementedError

    def eval(self, env: Dict[str, float]) -> float:
        raise NotImplementedError

    def definite_integral(self, var: str, a: float, b: float) -> float:
        """Определенный интеграл по формуле Ньютона-Лейбница: F(b) - F(a)."""
        antiderivative = self.integrate(var)
        env_b = {var: b}
        env_a = {var: a}
        return antiderivative.eval(env_b) - antiderivative.eval(env_a)

    def __add__(self, other: Union[Expr, float, int]) -> Expr:
        return make_add(self, to_expr(other))

    def __radd__(self, other: Union[Expr, float, int]) -> Expr:
        return make_add(to_expr(other), self)

    def __sub__(self, other: Union[Expr, float, int]) -> Expr:
        return make_sub(self, to_expr(other))

    def __rsub__(self, other: Union[Expr, float, int]) -> Expr:
        return make_sub(to_expr(other), self)

    def __mul__(self, other: Union[Expr, float, int]) -> Expr:
        return make_mul(self, to_expr(other))

    def __rmul__(self, other: Union[Expr, float, int]) -> Expr:
        return make_mul(to_expr(other), self)

    def __truediv__(self, other: Union[Expr, float, int]) -> Expr:
        return make_div(self, to_expr(other))

    def __pow__(self, power: Union[Expr, float, int]) -> Expr:
        return make_pow(self, to_expr(power))

    def __neg__(self) -> Expr:
        return make_mul(Const(-1), self)


def to_expr(val: Union[Expr, float, int]) -> Expr:
    if isinstance(val, Expr):
        return val
    if isinstance(val, (int, float)):
        return Const(float(val))
    raise TypeError(f"Невозможно преобразовать тип {type(val)} в Expr")


# --- Конкретные узлы дерева ---

class Const(Expr):
    def __init__(self, value: float):
        self.value = float(value)

    def diff(self, var: str) -> Expr:
        return Const(0.0)

    def integrate(self, var: str) -> Expr:
        # ∫ c dt = c * t
        return make_mul(Const(self.value), Symbol(var))

    def eval(self, env: Dict[str, float]) -> float:
        return self.value

    def __str__(self) -> str:
        if self.value.is_integer():
            return str(int(self.value))
        return f"{self.value:.4g}"

    def __repr__(self) -> str:
        return f"Const({self.value})"


class Symbol(Expr):
    def __init__(self, name: str):
        self.name = name

    def diff(self, var: str) -> Expr:
        # dt/dt = 1, dx/dt = 0
        return Const(1.0) if self.name == var else Const(0.0)

    def integrate(self, var: str) -> Expr:
        if self.name == var:
            # ∫ t dt = t^2 / 2
            return make_div(make_pow(Symbol(var), Const(2.0)), Const(2.0))
        # ∫ x dt = x * t
        return make_mul(self, Symbol(var))

    def eval(self, env: Dict[str, float]) -> float:
        if self.name not in env:
            raise KeyError(f"Переменная '{self.name}' не задана для вычисления")
        return float(env[self.name])

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Symbol('{self.name}')"


class Power(Expr):
    def __init__(self, base: Expr, exp: Expr):
        self.base = base
        self.exp = exp

    def diff(self, var: str) -> Expr:
        # (u^n)' = n * u^(n-1) * u' (для константной степени)
        if isinstance(self.exp, Const):
            n = self.exp.value
            return make_mul(
                make_mul(Const(n), make_pow(self.base, Const(n - 1))),
                self.base.diff(var)
            )
        raise NotImplementedError("Производная f(x)^g(x) общего вида пока не требуется")

    def integrate(self, var: str) -> Expr:
        # ∫ t^n dt = t^(n+1) / (n+1)
        if isinstance(self.base, Symbol) and self.base.name == var and isinstance(self.exp, Const):
            n = self.exp.value
            if math.isclose(n, -1.0):
                raise ValueError("Интеграл 1/t дает ln(t) — пока вне базовой школьной программы")
            return make_div(make_pow(Symbol(var), Const(n + 1)), Const(n + 1))
        raise NotImplementedError(f"Аналитический интеграл для {self} пока не поддержан")

    def eval(self, env: Dict[str, float]) -> float:
        return self.base.eval(env) ** self.exp.eval(env)

    def __str__(self) -> str:
        return f"({self.base}^{self.exp})"


class Add(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def diff(self, var: str) -> Expr:
        return make_add(self.left.diff(var), self.right.diff(var))

    def integrate(self, var: str) -> Expr:
        return make_add(self.left.integrate(var), self.right.integrate(var))

    def eval(self, env: Dict[str, float]) -> float:
        return self.left.eval(env) + self.right.eval(env)

    def __str__(self) -> str:
        return f"({self.left} + {self.right})"


class Sub(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def diff(self, var: str) -> Expr:
        return make_sub(self.left.diff(var), self.right.diff(var))

    def integrate(self, var: str) -> Expr:
        return make_sub(self.left.integrate(var), self.right.integrate(var))

    def eval(self, env: Dict[str, float]) -> float:
        return self.left.eval(env) - self.right.eval(env)

    def __str__(self) -> str:
        return f"({self.left} - {self.right})"


class Mul(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def diff(self, var: str) -> Expr:
        # (u * v)' = u'v + uv'
        return make_add(
            make_mul(self.left.diff(var), self.right),
            make_mul(self.left, self.right.diff(var))
        )

    def integrate(self, var: str) -> Expr:
        # Если левый сомножитель - константа: ∫ c*f(t) dt = c * ∫ f(t) dt
        if isinstance(self.left, Const):
            return make_mul(self.left, self.right.integrate(var))
        if isinstance(self.right, Const):
            return make_mul(self.right, self.left.integrate(var))
        raise NotImplementedError("Интегрирование произведений u(t)*v(t) по частям пока не поддержано")

    def eval(self, env: Dict[str, float]) -> float:
        return self.left.eval(env) * self.right.eval(env)

    def __str__(self) -> str:
        return f"({self.left} * {self.right})"


class Div(Expr):
    def __init__(self, num: Expr, den: Expr):
        self.num = num
        self.den = den

    def diff(self, var: str) -> Expr:
        # Если знаменатель - число: (u / c)' = u' / c
        if isinstance(self.den, Const):
            return make_div(self.num.diff(var), self.den)
        # (u / v)' = (u'v - uv') / v^2
        return make_div(
            make_sub(make_mul(self.num.diff(var), self.den), make_mul(self.num, self.den.diff(var))),
            make_pow(self.den, Const(2.0))
        )

    def integrate(self, var: str) -> Expr:
        if isinstance(self.den, Const):
            return make_div(self.num.integrate(var), self.den)
        raise NotImplementedError(f"Интегрирование дробей общего вида {self} пока не поддержано")

    def eval(self, env: Dict[str, float]) -> float:
        d = self.den.eval(env)
        if math.isclose(d, 0.0, abs_tol=1e-12):
            raise ZeroDivisionError("Деление на 0 при вычислении выражения")
        return self.num.eval(env) / d

    def __str__(self) -> str:
        return f"({self.num} / {self.den})"


class Sin(Expr):
    def __init__(self, arg: Expr):
        self.arg = arg

    def diff(self, var: str) -> Expr:
        # (sin(u))' = cos(u) * u'
        return make_mul(Cos(self.arg), self.arg.diff(var))

    def integrate(self, var: str) -> Expr:
        # ∫ sin(ω*t) dt = -cos(ω*t) / ω (для линейного аргумента)
        if isinstance(self.arg, Mul) and isinstance(self.arg.left, Const) and isinstance(self.arg.right, Symbol) and self.arg.right.name == var:
            w = self.arg.left
            return make_div(make_mul(Const(-1.0), Cos(self.arg)), w)
        if isinstance(self.arg, Symbol) and self.arg.name == var:
            return make_mul(Const(-1.0), Cos(self.arg))
        raise NotImplementedError("Сложный интеграл от sin(u) пока не поддержан")

    def eval(self, env: Dict[str, float]) -> float:
        return math.sin(self.arg.eval(env))

    def __str__(self) -> str:
        return f"sin({self.arg})"


class Cos(Expr):
    def __init__(self, arg: Expr):
        self.arg = arg

    def diff(self, var: str) -> Expr:
        # (cos(u))' = -sin(u) * u'
        return make_mul(make_mul(Const(-1.0), Sin(self.arg)), self.arg.diff(var))

    def integrate(self, var: str) -> Expr:
        # ∫ cos(ω*t) dt = sin(ω*t) / ω
        if isinstance(self.arg, Mul) and isinstance(self.arg.left, Const) and isinstance(self.arg.right, Symbol) and self.arg.right.name == var:
            w = self.arg.left
            return make_div(Sin(self.arg), w)
        if isinstance(self.arg, Symbol) and self.arg.name == var:
            return Sin(self.arg)
        raise NotImplementedError("Сложный интеграл от cos(u) пока не поддержан")

    def eval(self, env: Dict[str, float]) -> float:
        return math.cos(self.arg.eval(env))

    def __str__(self) -> str:
        return f"cos({self.arg})"


# --- Упростители (Smart Constructors) ---

def make_add(a: Expr, b: Expr) -> Expr:
    if isinstance(a, Const) and isinstance(b, Const):
        return Const(a.value + b.value)
    if isinstance(a, Const) and math.isclose(a.value, 0.0):
        return b
    if isinstance(b, Const) and math.isclose(b.value, 0.0):
        return a
    return Add(a, b)


def make_sub(a: Expr, b: Expr) -> Expr:
    if isinstance(a, Const) and isinstance(b, Const):
        return Const(a.value - b.value)
    if isinstance(b, Const) and math.isclose(b.value, 0.0):
        return a
    return Sub(a, b)


def make_mul(a: Expr, b: Expr) -> Expr:
    if isinstance(a, Const) and isinstance(b, Const):
        return Const(a.value * b.value)
    if (isinstance(a, Const) and math.isclose(a.value, 0.0)) or (isinstance(b, Const) and math.isclose(b.value, 0.0)):
        return Const(0.0)
    if isinstance(a, Const) and math.isclose(a.value, 1.0):
        return b
    if isinstance(b, Const) and math.isclose(b.value, 1.0):
        return a
    return Mul(a, b)


def make_div(a: Expr, b: Expr) -> Expr:
    if isinstance(a, Const) and isinstance(b, Const):
        return Const(a.value / b.value)
    if isinstance(a, Const) and math.isclose(a.value, 0.0):
        return Const(0.0)
    if isinstance(b, Const) and math.isclose(b.value, 1.0):
        return a
    return Div(a, b)


def make_pow(base: Expr, exp: Expr) -> Expr:
    if isinstance(exp, Const):
        if math.isclose(exp.value, 0.0):
            return Const(1.0)
        if math.isclose(exp.value, 1.0):
            return base
    if isinstance(base, Const) and isinstance(exp, Const):
        return Const(base.value ** exp.value)
    return Power(base, exp)


# --- Парсер строк в дерево выражений ---

def _ast_to_expr(node: ast.AST) -> Expr:
    if isinstance(node, ast.Constant):
        return Const(float(node.value))
    elif isinstance(node, ast.Name):
        return Symbol(node.id)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return make_mul(Const(-1.0), _ast_to_expr(node.operand))
    elif isinstance(node, ast.BinOp):
        left = _ast_to_expr(node.left)
        right = _ast_to_expr(node.right)
        if isinstance(node.op, ast.Add):
            return make_add(left, right)
        elif isinstance(node.op, ast.Sub):
            return make_sub(left, right)
        elif isinstance(node.op, ast.Mult):
            return make_mul(left, right)
        elif isinstance(node.op, ast.Div):
            return make_div(left, right)
        elif isinstance(node.op, ast.Pow):
            return make_pow(left, right)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        func_name = node.func.id.lower()
        arg = _ast_to_expr(node.args[0])
        if func_name == "sin":
            return Sin(arg)
        elif func_name == "cos":
            return Cos(arg)
    raise ValueError(f"Неподдерживаемый синтаксический узел: {ast.dump(node)}")


def parse_expr(expr_str: str) -> Expr:
    """Парсит человекочитаемую строку вида '3*t^2 - 5*t + 2' в дерево Expr."""
    normalized = expr_str.strip().replace("^", "**")
    parsed_ast = ast.parse(normalized, mode="eval")
    return _ast_to_expr(parsed_ast.body)

