import solver
from variables import Variable
from physics_formulas import FORMULAS_LIST

def run_all_tests():
    # Заголовок красивой таблицы
    print("\n" + "="*95)
    print(f"{'ФОРМУЛА (ID)':<38} | {'СЕКЦИЯ':<15} | {'СТАТУС':<8} | {'ОТВЕТ / ОШИБКА'}")
    print("="*95)

    passed = 0
    failed = 0

    for f in FORMULAS_LIST:
        given = {}
        for req_var in f.requires:
            # Умная генерация данных: подсовываем функции туда, где нужен матанализ, и числа в остальные места
            if req_var == Variable.POSITION_FUNC:
                val = "3*t^2 + 2*t м"
            elif req_var == Variable.VELOCITY_FUNC:
                val = "6*t м/с"
            elif req_var == Variable.ACCELERATION_FUNC:
                val = "6 + 0*t м/с^2" # Теперь парсер точно увидит 't' и создаст функцию Expr
            elif req_var == Variable.FORCE_FUNC:
                val = "4*x + 1 Н"
            elif req_var == Variable.CURRENT_FUNC:
                val = "2*t А"
            elif req_var == Variable.MAGNETIC_FLUX_FUNC:
                val = "5*t Вб"
            elif req_var in (Variable.TIME_START, Variable.COORD_START):
                val = "1"
            elif req_var in (Variable.TIME_END, Variable.COORD_END, Variable.TIME):
                val = "3"
            elif req_var in (Variable.TEMPERATURE, Variable.TEMP_HOT):
                val = "300"
            elif req_var == Variable.TEMP_COLD:
                val = "250"
            elif req_var == Variable.FOCAL_LENGTH:
                val = "3" # Фокус не должен быть равен d, чтобы не было деления на 0
            elif req_var == Variable.OBJECT_DISTANCE:
                val = "4"
            else:
                val = "2"

            var_name = solver.get_display_name(req_var)
            given[var_name] = val
        
        target_name = solver.get_display_name(f.result_variable)
        
        # Прогоняем формулу через твой движок
        res = solver.solve_and_calculate(given, target_name)
        
        # Форматируем строки, чтобы таблица не разъезжалась
        formula_id = f.id[:35] + "..." if len(f.id) > 38 else f.id
        section = f.section[:13] + ".." if len(f.section) > 15 else f.section
        
        if res["error"] is None:
            passed += 1
            status = "✅ OK"
            ans = res['final_answer_str']
            print(f"{formula_id:<38} | {section:<15} | {status:<8} | {ans}")
        else:
            failed += 1
            status = "❌ FAIL"
            # Обрезаем длинный текст ошибки
            err = res['error'].split('\n')[0][:25] + "..."
            print(f"{formula_id:<38} | {section:<15} | {status:<8} | {err}")

    print("="*95)
    print(f"ИТОГО ФОРМУЛ: {len(FORMULAS_LIST)} | ✅ УСПЕШНО: {passed} | ❌ ОШИБОК: {failed}")
    
    if failed == 0:
        print("🎉 Движок идеален! Все формулы работают.")
    else:
        print("⚠️ Есть ошибки! Обрати внимание на таблицу.")

if __name__ == '__main__':
    run_all_tests()