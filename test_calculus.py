# test_calculus.py
import math
import unittest

from math_engine import parse_expr
from solver import solve_and_calculate


class TestCalculusIsolated(unittest.TestCase):
    """Изолированные тесты математического ядра math_engine.py."""

    def test_polynomial_derivatives(self):
        expr = parse_expr("3*t^2 - 5*t + 2")
        v_expr = expr.diff("t")
        self.assertTrue(math.isclose(v_expr.eval({"t": 0}), -5.0))
        self.assertTrue(math.isclose(v_expr.eval({"t": 2}), 7.0))
        self.assertTrue(math.isclose(v_expr.eval({"t": 3}), 13.0))

        a_expr = v_expr.diff("t")
        self.assertTrue(math.isclose(a_expr.eval({"t": 0}), 6.0))
        self.assertTrue(math.isclose(a_expr.eval({"t": 10}), 6.0))

    def test_trigonometric_derivative(self):
        expr = parse_expr("sin(2*t)")
        v_expr = expr.diff("t")
        expected_at_0 = 2.0 * math.cos(0.0)
        self.assertTrue(math.isclose(v_expr.eval({"t": 0}), expected_at_0, rel_tol=1e-5))

    def test_definite_integral_work(self):
        F = parse_expr("4*x + 1")
        work = F.definite_integral("x", 0.0, 2.0)
        self.assertTrue(math.isclose(work, 10.0, rel_tol=1e-5))

    def test_definite_integral_elastic_work(self):
        F = parse_expr("200*x")
        work = F.definite_integral("x", 0.0, 0.1)
        self.assertTrue(math.isclose(work, 1.0, rel_tol=1e-5))

    def test_definite_integral_charge(self):
        current = parse_expr("3*t^2 + 2*t")
        q = current.definite_integral("t", 1.0, 3.0)
        self.assertTrue(math.isclose(q, 34.0, rel_tol=1e-5))


class TestCalculusSolverPipeline(unittest.TestCase):
    """Сквозные тесты графового солвера со связками матанализа."""

    def test_solver_diff_pipeline(self):
        print("\n\n=== ТЕСТ 1: Поиск импульса через производную координаты ===")
        given = {
            "x(t)": "3*t^2 - 5*t + 2 м",
            "t": "3 с",
            "m": "2 кг",
        }
        res = solve_and_calculate(given, "p", verbose=True)
        self.assertIsNotNone(res)
        self.assertTrue(math.isclose(float(res), 26.0, rel_tol=1e-4))

    def test_solver_integral_work_pipeline(self):
        print("\n\n=== ТЕСТ 2: Интеграл переменной силы ===")
        given = {
            "F(x)": "4*x + 1 Н",
            "x1": "0 м",
            "x2": "2 м",
        }
        res = solve_and_calculate(given, "A", verbose=True)
        self.assertIsNotNone(res)
        self.assertTrue(math.isclose(float(res), 10.0, rel_tol=1e-4))

    def test_solver_integral_charge_pipeline(self):
        print("\n\n=== ТЕСТ 3: Заряд через интеграл тока ===")
        given = {
            "i(t)": "3*t^2 + 2*t А",
            "t1": "1 с",
            "t2": "3 с",
        }
        res = solve_and_calculate(given, "q", verbose=True)
        self.assertIsNotNone(res)
        self.assertTrue(math.isclose(float(res), 34.0, rel_tol=1e-4))


if __name__ == "__main__":
    unittest.main()