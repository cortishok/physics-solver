import re
import flet as ft
import solver
from variables import UI_SUGGESTIONS

def main(page: ft.Page):
    page.title = "Физический Солвер ЕГЭ"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 450
    page.window_height = 800
    page.scroll = "adaptive"

    # --- СОСТОЯНИЕ АВТОКОМПЛИТА ---
    active_input_type = None  # 'given' или 'target'
    active_textfield = None

    def show_suggestions(e, input_type):
        nonlocal active_input_type, active_textfield
        active_input_type = input_type
        active_textfield = e.control
        
        text = active_textfield.value
        if not text:
            suggestions_card.visible = False
            page.update()
            return

        current_line = text.split('\n')[-1]
        
        if input_type == 'given' and '=' in current_line:
            suggestions_card.visible = False
            page.update()
            return

        match = re.search(r'\S+$', text)
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
                    on_click=lambda e, k=key: apply_suggestion(k)
                )
            )

        suggestions_card.visible = True
        page.update()

    def apply_suggestion(key):
        if not active_textfield:
            return

        insert_text = f"{key} = " if active_input_type == 'given' else f"{key} "
        current_text = active_textfield.value

        match = re.search(r'\S+$', current_text)
        if match:
            new_text = current_text[:match.start()] + insert_text
        else:
            new_text = current_text + insert_text

        active_textfield.value = new_text
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
        on_change=lambda e: show_suggestions(e, 'given')
    )

    target_input = ft.TextField(
        label="Найти",
        hint_text="Например: начните писать 'скор...'",
        text_size=16,
        on_change=lambda e: show_suggestions(e, 'target')
    )

    suggestions_list = ft.Column(spacing=0)
    suggestions_card = ft.Card(
        content=suggestions_list,
        visible=False,
        elevation=8,
        margin=ft.margin.only(top=-10, bottom=10)
    )

    output_text = ft.Text(selectable=True, size=16)

    def solve_clicked(e):
        suggestions_card.visible = False
        output_text.value = "⏳ Решаю..."
        page.update()

        given_dict = {}
        for line in given_input.value.strip().split('\n'):
            if '=' in line:
                k, v = line.split('=', 1)
                # Умная автозамена запятой на точку
                clean_v = v.strip().replace(',', '.')
                given_dict[k.strip()] = clean_v

        target = target_input.value.strip()

        if not target:
            output_text.value = "❌ Ошибка: Укажите переменную 'Найти'."
            page.update()
            return

        res = solver.solve_and_calculate(given_dict, target)

        if res.get("error"):
            output_text.value = f"❌ Ошибка:\n{res['error']}"
        else:
            steps = "\n".join(res["steps"])
            output_text.value = f"✅ ОТВЕТ: {res['final_answer_str']}\n\nШАГИ:\n{steps}"

        page.update()

    solve_btn = ft.ElevatedButton(
        "Решить", 
        icon=ft.icons.CALCULATE, 
        on_click=solve_clicked,
        height=50,
        width=float('inf')
    )

    # Обернули всё в SafeArea, чтобы статус-бар больше не перекрывал интерфейс
    page.add(
        ft.SafeArea(
            ft.Column(
                [
                    ft.Text("Физический Солвер ЕГЭ", size=24, weight="bold"),
                    given_input,
                    target_input,
                    suggestions_card,
                    solve_btn,
                    ft.Divider(height=30),
                    output_text,
                ],
                expand=True,
            )
        )
    )

ft.app(target=main)