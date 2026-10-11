# app.py
import flet as ft
from solver import solve_and_calculate, STRING_TO_VARIABLE


# Словарь понятных названий для автокомплита
HINT_DICT = [
    ("Масса (m)", "m"),
    ("Скорость (v)", "v"),
    ("Начальная скорость (v0)", "v0"),
    ("Ускорение (a)", "a"),
    ("Время (t)", "t"),
    ("Сила (F)", "F"),
    ("Сила трения (F_tr)", "F_tr"),
    ("Импульс (p)", "p"),
    ("Давление (P)", "P"),
    ("Работа (A)", "A"),
    ("Мощность (N)", "N"),
    ("Кинетическая энергия (E_k)", "E_k"),
    ("Потенциальная энергия (E_p)", "E_p"),
    ("Жесткость пружины (k)", "k"),
    ("Координата x(t)", "x(t)"),
    ("Скорость v(t)", "v(t)"),
    ("Сила F(x)", "F(x)"),
    ("Ток i(t)", "i(t)"),
    ("Температура (T)", "T"),
    ("Объем (V)", "V"),
    ("Плотность (rho)", "rho"),
    ("Сила тока (I)", "I"),
    ("Напряжение (U)", "U_volt"),
    ("Сопротивление (R)", "R"),
    ("Заряд (q)", "q"),
    ("ЭДС (eps)", "eps"),
]


def parse_multiline_given(text: str) -> dict:
    """Парсит строки вида 'x(t) = 3*t^2\nm = 2 кг' или через запятую."""
    given = {}
    normalized = text.replace(",", "\n")
    for line in normalized.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        given[key.strip()] = val.strip()
    return given


def main(page: ft.Page):
    page.title = "Physics Solver"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 16
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Поля ввода
    given_input = ft.TextField(
        label="Дано (каждая величина с новой строки)",
        hint_text="x(t) = 3*t^2 - 5*t + 2 м\nt = 3 с\nm = 2 кг",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_radius=10,
    )

    target_input = ft.TextField(
        label="Что найти?",
        hint_text="p",
        border_radius=10,
    )

    hints_column = ft.Column(spacing=4)
    results_column = ft.Column(spacing=8)

    def insert_token(alias: str):
        """Вставляет алиас в активное поле."""
        target_field = target_input if target_input.focused else given_input
        if target_field == target_input:
            target_field.value = alias
        else:
            current = target_field.value or ""
            prefix = "" if (not current or current.endswith("\n")) else "\n"
            target_field.value = f"{current}{prefix}{alias} = "
        page.update()

    def update_hints(e):
        """Фильтрует подсказки на основе введённого текста."""
        query = (e.control.value or "").strip().lower()
        hints_column.controls.clear()
        if not query:
            page.update()
            return

        last_token = query.split()[-1] if query else ""
        matched = [
            (label, alias)
            for label, alias in HINT_DICT
            if last_token in label.lower() or last_token in alias.lower()
        ][:4]

        for label, alias in matched:
            hints_column.controls.append(
                ft.TextButton(
                    text=f"➕ {label}",
                    on_click=lambda _, a=alias: insert_token(a),
                )
            )
        page.update()

    given_input.on_change = update_hints
    target_input.on_change = update_hints

    # Панель быстрых клавиш
    quick_buttons = ft.Row(
        wrap=True,
        spacing=6,
        controls=[
            ft.OutlinedButton("m", on_click=lambda _: insert_token("m")),
            ft.OutlinedButton("v", on_click=lambda _: insert_token("v")),
            ft.OutlinedButton("t", on_click=lambda _: insert_token("t")),
            ft.OutlinedButton("F", on_click=lambda _: insert_token("F")),
            ft.OutlinedButton("p", on_click=lambda _: insert_token("p")),
            ft.OutlinedButton("A", on_click=lambda _: insert_token("A")),
            ft.OutlinedButton("x(t)", on_click=lambda _: insert_token("x(t)")),
        ],
    )

    def on_solve_click(_):
        results_column.controls.clear()

        raw_given = parse_multiline_given(given_input.value or "")
        raw_target = (target_input.value or "").strip()

        if not raw_given or not raw_target:
            results_column.controls.append(
                ft.Text("⚠️ Заполните 'Дано' и 'Что найти'.", color=ft.colors.AMBER)
            )
            page.update()
            return

        res = solve_and_calculate(raw_given, raw_target)

        if res.get("error"):
            results_column.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Text(f"❌ {res['error']}", color=ft.colors.RED_200),
                        padding=12,
                    )
                )
            )
        else:
            steps_controls = []
            for s in res["steps"]:
                steps_controls.append(
                    ft.Text(f"{s['step']}. {s['formula']}  ➜  {s['result_str']}")
                )

            # Карточка решения
            results_column.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column(
                            controls=[
                                ft.Text("Шаги решения:", weight=ft.FontWeight.BOLD),
                                *steps_controls,
                                ft.Divider(),
                                ft.Text(
                                    f"Ответ: {res['target']} = {res['final_answer_str']}",
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                    color=ft.colors.GREEN_400,
                                ),
                            ]
                        ),
                    )
                )
            )
        page.update()

    solve_button = ft.ElevatedButton(
        "Рассчитать",
        icon=ft.icons.PLAY_ARROW,
        on_click=on_solve_click,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_600,
            padding=14,
        ),
    )

    # Главная компоновка страницы
    page.add(
        ft.Text("⚡ Физический Солвер", size=22, weight=ft.FontWeight.BOLD),
        ft.Text("Быстрый ввод:", size=12, color=ft.colors.GREY_400),
        quick_buttons,
        given_input,
        target_input,
        hints_column,
        solve_button,
        ft.Divider(),
        results_column,
    )


if __name__ == "__main__":
    ft.app(target=main)