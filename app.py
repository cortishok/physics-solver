import re
import flet as ft
import solver
from variables import UI_SUGGESTIONS


def main(page: ft.Page):
    page.title = "Физический Солвер ЕГЭ"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.scroll = ft.ScrollMode.ADAPTIVE

    # --- СОСТОЯНИЕ АВТОКОМПЛИТА ---
    active_input_type = None  # 'given' или 'target'
    active_textfield = None

    def show_suggestions(e, input_type):
        nonlocal active_input_type, active_textfield
        active_input_type = input_type
        active_textfield = e.control

        text = active_textfield.value or ""
        if not text.strip():
            suggestions_card.visible = False
            page.update()
            return

        current_line = text.split("\n")[-1]

        # Если в строке "Дано" уже есть "=", значит вводится значение — прячем подсказки
        if input_type == "given" and "=" in current_line:
            suggestions_card.visible = False
            page.update()
            return

        # Ищем последнее слово строго в текущей строке (исправление п. 4.3 ревью)
        match = re.search(r"\S+$", current_line)
        if not match:
            suggestions_card.visible = False
            page.update()
            return

        last_word = match.group().lower()

        matches = []
        for key, desc in UI_SUGGESTIONS.items():
            if last_word in key.lower() or last_word in desc.lower():
                matches.append((key, desc))

        if not matches:
            suggestions_card.visible = False
            page.update()
            return

        suggestions_list.controls.clear()
        for key, desc in matches[:5]:
            suggestions_list.controls.append(
                ft.ListTile(
                    title=ft.Text(desc, size=14),
                    leading=ft.Icon(ft.icons.BOLT, color=ft.colors.BLUE_400),
                    on_click=lambda e, k=key: apply_suggestion(k),
                )
            )

        suggestions_card.visible = True
        page.update()

    def apply_suggestion(key):
        if not active_textfield:
            return

        insert_text = f"{key} = " if active_input_type == "given" else f"{key}"
        current_text = active_textfield.value or ""

        lines = current_text.split("\n")
        last_line = lines[-1]
        match = re.search(r"\S+$", last_line)
        if match:
            lines[-1] = last_line[: match.start()] + insert_text
        else:
            lines[-1] = last_line + insert_text

        active_textfield.value = "\n".join(lines)
        active_textfield.focus()
        suggestions_card.visible = False
        page.update()

    # --- ЭЛЕМЕНТЫ ИНТЕРФЕЙСА ---
    given_input = ft.TextField(
        label="Дано (вводите каждую величину с новой строки)",
        hint_text="Например: начните писать 'масс...'",
        multiline=True,
        min_lines=4,
        text_size=16,
        on_change=lambda e: show_suggestions(e, "given"),
    )

    target_input = ft.TextField(
        label="Найти",
        hint_text="Например: начните писать 'скор...'",
        text_size=16,
        on_change=lambda e: show_suggestions(e, "target"),
    )

    suggestions_list = ft.Column(spacing=0)
    suggestions_card = ft.Card(
        content=suggestions_list,
        visible=False,
        elevation=8,
        margin=ft.margin.only(top=-10, bottom=10),
    )

    output_text = ft.Text(selectable=True, size=16)

    def solve_clicked(e):
        suggestions_card.visible = False
        raw_given = (given_input.value or "").strip()
        target = (target_input.value or "").strip()

        if not raw_given:
            output_text.value = "❌ Ошибка: Заполните поле 'Дано'."
            page.update()
            return

        if not target:
            output_text.value = "❌ Ошибка: Укажите переменную 'Найти'."
            page.update()
            return

        output_text.value = "⏳ Решаю..."
        page.update()

        given_dict = {}
        for line in raw_given.split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                clean_v = v.strip().replace(",", ".")
                given_dict[k.strip()] = clean_v

        if not given_dict:
            output_text.value = "❌ Ошибка: В поле 'Дано' используйте формат 'буква = число'."
            page.update()
            return

        try:
            res = solver.solve_and_calculate(given_dict, target)
            if res.get("error"):
                output_text.value = f"❌ Ошибка:\n{res['error']}"
            else:
                steps = "\n".join(res["steps"])
                output_text.value = f"✅ ОТВЕТ: {res['final_answer_str']}\n\nШАГИ:\n{steps}"
        except Exception as exc:
            output_text.value = f"❌ Непредвиденная ошибка расчёта:\n{exc}"

        page.update()

    solve_btn = ft.ElevatedButton(
        "Решить",
        icon=ft.icons.CALCULATE,
        on_click=solve_clicked,
        height=50,
    )

    # SafeArea и прокручиваемая колонка для удобного чтения длинных цепочек шагов
    page.add(
        ft.SafeArea(
            ft.Column(
                [
                    ft.Text("Физический Солвер ЕГЭ", size=24, weight="bold"),
                    given_input,
                    target_input,
                    suggestions_card,
                    ft.Row([solve_btn], expand=True),
                    ft.Divider(height=30),
                    output_text,
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )
    )


ft.app(target=main)
