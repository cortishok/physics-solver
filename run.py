# run.py
from solver import solve_and_calculate


def print_solution(response: dict):
    """Красиво выводит результат решения в консоль."""
    if response["error"]:
        print(f"\n❌ ОШИБКА: {response['error']}\n")
        return

    print("\n" + "=" * 60)
    print(f"🎯 ЦЕЛЬ: Найти '{response['target']}'")
    print("=" * 60)
    print("ПОШАГОВЫЙ ХОД РЕШЕНИЯ:")

    for step in response["steps"]:
        idx = step["step"]
        formula = step["formula"]
        res_str = step["result_str"]
        print(f"  {idx}. {formula:<26} => {res_str}")

    print("=" * 60)
    print(f"✅ ОТВЕТ: {response['target']} = {response['final_answer_str']}\n")


if __name__ == "__main__":
    # Тестовая задача: x(t) = 3t^2 - 5t + 2, найти импульс p в момент времени t = 3 с при m = 2 кг
    given = {
        "x(t)": "3*t^2 - 5*t + 2 м",
        "t": "3 с",
        "m": "2 кг",
    }
    target = "p"

    result = solve_and_calculate(given, target)
    print_solution(result)