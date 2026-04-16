import pandas as pd
from fuzzywuzzy import fuzz

# 1. Загрузка данных в DataFrame
# Для примера создадим демонстрационные DataFrame
data_a = {'name': ['Вконтакте', 'Манчестер Юнайтед', 'Аббревиатура', 'Снег'], 'value_a': [100, 200, 300, 400]}
data_b = {'name': ['В контакте', 'Манчестер Сити', 'Аббривеатура', 'Снежинка'],
          'value_b': [150, 250, 350, 450]}
df_a = pd.DataFrame(data_a)
df_b = pd.DataFrame(data_b)


# 2. Очистка названий
def clean_names(df, column_name):
    df[column_name] = df[column_name].str.strip().str.lower()
    return df


df_a = clean_names(df_a, 'name')
df_b = clean_names(df_b, 'name')

# 3. Точный поиск (merge)
# Используем inner join для получения точных совпадений
exact_matches = pd.merge(df_a, df_b, on='name', how='inner')
exact_matches['match_type'] = 'exact'

# 4. Подготовка к нечеткому поиску
# Находим записи из A, которые не нашли пару в точном поиске
# Используем merge с how='left' и индикатором, чтобы найти несовпавшие
merged_left = pd.merge(df_a, df_b, on='name', how='left', indicator=True)
leftovers_a = merged_left[merged_left['_merge'] == 'left_only']['name']

# 5. Нечеткий поиск
fuzzy_matches_list = []
# Цикл по оставшимся записям из A
for name_a in leftovers_a:
    best_match = None
    best_score = 0
    # Пробегаемся по списку B для каждой записи из A
    for name_b in df_b['name']:
        score = fuzz.ratio(name_a, name_b)
        if score > best_score:
            best_score = score
            best_match = name_b

    # Если сходство > 80%, добавляем в список "Варианты"
    if best_score >= 80:
        # Получаем полную строку из df_a для совпавшей записи
        original_row_a = df_a[df_a['name'] == name_a].iloc[0].to_dict()
        # Получаем полную строку из df_b для лучшего совпадения
        original_row_b = df_b[df_b['name'] == best_match].iloc[0].to_dict()

        # Объединяем информацию
        matched_row = {**original_row_a, **original_row_b}
        matched_row['match_type'] = 'fuzzy'
        matched_row['similarity_score'] = best_score
        fuzzy_matches_list.append(matched_row)

# Преобразуем список нечетких совпадений в DataFrame
fuzzy_matches = pd.DataFrame(fuzzy_matches_list)

# 6. Объединение результатов
# Склеиваем результаты точного и нечеткого поиска
final_results = pd.concat([exact_matches, fuzzy_matches], ignore_index=True)

# 7. Сохранение отчета
# Сохраняем итоговый DataFrame в файл CSV
final_results.to_csv('matching_report.csv', index=False)

print("Отчет сохранен в 'matching_report.csv'")
print(final_results)