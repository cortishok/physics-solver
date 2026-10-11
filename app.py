import flet as ft
import solver


def main(page: ft.Page):
    page.title = "Физический Солвер"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.BOLT, color=ft.colors.ORANGE_500),
        title=ft.Text("Физический Солвер", weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.colors.SURFACE_VARIANT,
    )

    input_given = ft.TextField(
        label="Дано (каждая величина с новой строки)",
        multiline=True,
        min_lines=4,
        hint_text="m = 10\nv = 55\nS = 100",
    )
    input_find = ft.TextField(label="Что найти?", hint_text="t или E_k")
    results_col = ft.Column(spacing=8)

    # Кнопки быстрого ввода
    def on_quick_btn_click(e):
        val = input_given.value or ""
        if val and not val.endswith("\n"):
            val += "\n"
        input_given.value = val + f"{e.control.text} = "
        input_given.focus()
        page.update()

    quick_buttons = ft.Row(
        controls=[
            ft.OutlinedButton(text=btn, on_click=on_quick_btn_click)
            for btn in ["m", "v", "t", "F", "p", "S", "h", "a", "x(t)"]
        ],
        scroll=ft.ScrollMode.AUTO,
    )

    # Автоподстановка по подсказкам
    def on_hint_click(e):
        variable = e.control.data
        val = input_given.value or ""
        if val and not val.endswith("\n"):
            val += "\n"
        input_given.value = val + f"{variable} = "
        results_col.controls.clear()
        input_given.focus()
        page.update()

    def on_input_change(e):
        text = (e.control.value or "").strip().lower()
        if not text:
            return

        last_line = text.split("\n")[-1].strip()
        results_col.controls.clear()

        hints_dict = {
            "им": ("Импульс (p)", "p"),
            "си": ("Сила (F)", "F"),
            "ск": ("Скорость (v)", "v"),
            "вр": ("Время (t)", "t"),
            "ма": ("Масса (m)", "m"),
            "ус": ("Ускорение (a)", "a"),
            "пу": ("Путь/Расстояние (S)", "S"),
            "вы": ("Высота (h)", "h"),
        }

        for prefix, (title_text, var_key) in hints_dict.items():
            if last_line.startswith(prefix) or last_line == prefix:
                results_col.controls.append(
                    ft.ListTile(
                        title=ft.Text(title_text),
                        leading=ft.Icon(ft.icons.ADD, color=ft.colors.PURPLE_400),
                        data=var_key,
                        on_click=on_hint_click,
                    )
                )
                break
        page.update()

    input_given.on_change = on_input_change

    # РЕАЛЬНЫЙ РАСЧЕТ БЕЗ ЗАГЛУШЕК
    def calculate(e):
        results_col.controls.clear()

        raw_given_text = input_given.value or ""
        target_raw = (input_find.value or "").strip()

        if not target_raw:
            results_col.controls.append(
                ft.Text("Укажите, какую величину нужно найти!", color=ft.colors.RED_400)
            )
            page.update()
            return

        # Парсим входные строки вида 'm = 10'
        given_dict = {}
        for line in raw_given_text.splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            given_dict[k.strip()] = v.strip()

        if not given_dict:
            results_col.controls.append(
                ft.Text("Заполните поле 'Дано' (например: m = 10)", color=ft.colors.RED_400)
            )
            page.update()
            return

        # Запуск движка
        res = solver.solve_and_calculate(given_dict, target_raw)

        if res.get("error"):
            results_col.controls.append(
                ft.Text(f"Ошибка: {res['error']}", color=ft.colors.RED_400, weight=ft.FontWeight.BOLD)
            )
        else:
            if res.get("steps"):
                results_col.controls.append(ft.Text("Шаги решения:", weight=ft.FontWeight.BOLD))
                for step in res["steps"]:
                    results_col.controls.append(
                        ft.Text(
                            f"{step['step']}. {step['formula']} ➔ {step['result_str']}",
                            size=14,
                        )
                    )
                results_col.controls.append(ft.Divider())

            final_str = res.get("final_answer_str") or str(res.get("result"))
            results_col.controls.append(
                ft.Text(
                    f"Ответ: {target_raw} = {final_str}",
                    color=ft.colors.GREEN_400,
                    weight=ft.FontWeight.BOLD,
                    size=18,
                )
            )

        page.update()

    calc_btn = ft.ElevatedButton(
        "Рассчитать",
        icon=ft.icons.PLAY_ARROW,
        on_click=calculate,
        bgcolor=ft.colors.BLUE_600,
        color=ft.colors.WHITE,
    )

    page.add(
        ft.Text("Быстрый ввод:"),
        quick_buttons,
        input_given,
        input_find,
        calc_btn,
        ft.Divider(),
        results_col,
    )


if __name__ == "__main__":
    ft.app(target=main)