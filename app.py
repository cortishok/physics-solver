import flet as ft
import solver # Подключаем твой математический движок

def main(page: ft.Page):
    page.title = "Физический Солвер"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Исправление 1: Центрирование заголовка для мобильных экранов
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.BOLT, color=ft.colors.ORANGE_500),
        title=ft.Text("Физический Солвер", weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.colors.SURFACE_VARIANT
    )

    input_given = ft.TextField(label="Дано (каждая величина с новой строки)", multiline=True, min_lines=3)
    input_find = ft.TextField(label="Что найти?")
    results_col = ft.Column()

    # Исправление 2: Рабочие кнопки быстрого ввода
    def on_quick_btn_click(e):
        val = input_given.value if input_given.value else ""
        if val and not val.endswith("\n"):
            val += "\n"
        input_given.value = val + f"{e.control.text} = "
        input_given.focus() # Возвращаем курсор в поле
        page.update()

    quick_buttons = ft.Row(
        controls=[
            ft.OutlinedButton(text=btn, on_click=on_quick_btn_click)
            for btn in ["m", "v", "t", "F", "p", "A", "x(t)"]
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # Исправление 3: Кликабельные подсказки с автоподстановкой
    def on_hint_click(e):
        variable = e.control.data # Берем скрытую величину (например, 'F')
        val = input_given.value if input_given.value else ""
        if val and not val.endswith("\n"):
            val += "\n"
        input_given.value = val + f"{variable} = "
        
        results_col.controls.clear() # Убираем список подсказок после выбора
        input_given.focus()
        page.update()

    # Функция для вывода подсказок (привязана к изменению поля input_given)
    def on_input_change(e):
        text = e.control.value.lower()
        results_col.controls.clear()
        
        # Пример логики: если ввели "им", предлагаем "Импульс (p)"
        if text.endswith("им"):
            results_col.controls.append(
                ft.ListTile(
                    title=ft.Text("Импульс (p)"), 
                    leading=ft.Icon(ft.icons.ADD, color=ft.colors.PURPLE_400),
                    data="p", 
                    on_click=on_hint_click
                )
            )
        page.update()

    input_given.on_change = on_input_change

    def calculate(e):
        results_col.controls.clear()
        # Здесь мы передаем данные в solver.py
        # req = {"given": input_given.value, "find": input_find.value}
        # res = solver.solve(req)
        
        # Вывод шагов (пример структуры)
        results_col.controls.append(ft.Text("Шаги решения:", weight=ft.FontWeight.BOLD))
        results_col.controls.append(ft.Text("1. v(t) = x'(t) ➔ ((3 * (2 * t)) - 5) [м/с]"))
        results_col.controls.append(ft.Text("2. v = v(t) ➔ 13 м/с"))
        results_col.controls.append(ft.Text("3. p = m·v ➔ 26"))
        results_col.controls.append(ft.Divider())
        results_col.controls.append(ft.Text("Ответ: p = 26", color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD, size=16))
        page.update()

    calc_btn = ft.ElevatedButton(
        "Рассчитать", 
        icon=ft.icons.PLAY_ARROW, 
        on_click=calculate, 
        bgcolor=ft.colors.BLUE_600, 
        color=ft.colors.WHITE
    )

    page.add(
        ft.Text("Быстрый ввод:"),
        quick_buttons,
        input_given,
        input_find,
        calc_btn,
        ft.Divider(),
        results_col
    )

if __name__ == "__main__":
    ft.app(target=main)