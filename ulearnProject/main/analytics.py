import requests
from collections import Counter
from xml.etree import ElementTree
import matplotlib.pyplot as plt
import pandas as pd
from itertools import islice
import textwrap


# --------------------------------------------------------------------------------------------------Functions for data processing

def load_data(csv_path):
    df = pd.read_csv(csv_path, low_memory=False)
    return df

# Предобработка данных: обработка пропусков, расчет средней зарплаты, конвертация валют, фильтрация по дате
def preprocess_data(df):
    # Если нет столбца с валютой, добавляем его и заполняем значением 'RUR'
    if 'salary_currency' not in df.columns:
        df['salary_currency'] = 'RUR'
    df['salary_currency'] = df['salary_currency'].fillna('RUR')
    # Удаляем строки без данных о зарплате
    df = df.dropna(subset=['salary_from', 'salary_to'])
    # Считаем среднюю зарплату
    df.loc[:, 'average_salary'] = df[['salary_from', 'salary_to']].mean(axis=1)
    df = df.dropna(subset=['average_salary'])
    # Получаем курсы валют
    currency_to_rub = get_all_exchange_rates()

    # Функция для конвертации зарплаты в рубли
    def convert_to_rub(row):
        currency = row['salary_currency']
        original_salary = row['average_salary']
        if currency in currency_to_rub:
            return original_salary * currency_to_rub[currency]
        return original_salary

    # Применяем конвертацию
    df['average_salary'] = df.apply(convert_to_rub, axis=1)
    # Удаляем аномально большие значения
    df = df[df['average_salary'] <= 10_000_000]
    # Преобразуем дату публикации в datetime
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce', utc=True)
    df = df.dropna(subset=['published_at'])
    # Добавляем столбец с годом публикации
    df['year'] = df['published_at'].dt.year
    return df

# Расчет средней зарплаты по отфильтрованным данным
def calculate_average_salary(df):
    filtered_df = filter_data_by_keywords(df)
    valid_salaries = filtered_df['average_salary'].dropna()
    if valid_salaries.empty:
        return 0
    return int(valid_salaries.mean())

# Фильтрация данных по ключевым словам (analytic)
def filter_data_by_keywords(df):
    keywords = ['аналитик', 'analyst', 'analytic', 'аналітик', 'business intelligence', 'bi']
    pattern = '|'.join(keywords)

    return df[
        df['name'].str.lower().str.contains(pattern, na=False) |
        df['area_name'].str.lower().str.contains(pattern, na=False) |
        df['key_skills'].str.lower().str.contains(pattern, na=False)
    ]
# --------------------------------------------------------------------------------------------------------General_stats

def plot_vacancy_trends(df_all, df_analyst, output_path):
    all_vacancies_by_year = df_all.groupby('year').size()
    analyst_vacancies_by_year = df_analyst.groupby('year').size()

    plt.figure(figsize=(12, 7))
    plt.bar(all_vacancies_by_year.index, all_vacancies_by_year.values, 
            label='Все вакансии', alpha=0.5, color='skyblue')

    plt.plot(analyst_vacancies_by_year.index, analyst_vacancies_by_year.values,
            color='red', marker='o', label='Аналитик')

    plt.title("Сравнение количества вакансий: все и аналитик")
    plt.xlabel("Год")
    plt.ylabel("Количество вакансий")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
# --------------------------------------------------------------------------------------------------------DEMAND

def plot_salary_trends(df, output_path):
    df = filter_data_by_keywords(df)
    salary_trends = df.groupby('year')['average_salary'].mean().sort_index()
    plt.figure(figsize=(10, 6))
    salary_trends.plot(kind='line', marker='o', color='blue')
    plt.title('Динамика уровня зарплат по годам для аналитика')
    plt.xlabel('Год')
    plt.ylabel('Средняя зарплата (RUB)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# --------------------------------------------------------------------------------------------------------Geography

def plot_city_vacancy_share(df, output_path):
    df_copy = df.copy()
    # Сводная таблица по городам
    df_copy_salary_level_all = df_copy.pivot_table(
        index='area_name',
        values=['average_salary', 'name'],
        aggfunc={'average_salary': 'mean', 'name': 'count'}
    ).reset_index().sort_values(by=['name', 'average_salary'], ascending=False)

    # Топ-9 городов + "Другие"
    df_copy_salary_level_head = df_copy_salary_level_all.head(9)
    other_cities_count = df_copy_salary_level_all['name'].iloc[9:].sum()
    other_city = pd.DataFrame({'area_name': ['Другие'], 'name': [other_cities_count]})
    final_df = pd.concat([df_copy_salary_level_head, other_city], axis=0).reset_index(drop=True)

    # Построение круговой диаграммы
    fig, ax = plt.subplots(figsize=(15, 13))
    ax.set_facecolor('#F1F1F1')
    plt.gcf().set_facecolor('#F1F1F1')
    plt.pie(final_df['name'], autopct='%1.1f%%', startangle=40)
    plt.title("Доля вакансий 'Аналитик' по городам")
    plt.legend(labels=final_df['area_name'])
    plt.savefig(output_path)
    plt.close()

# ----------------- Построение графика по годам -----------------
def plot_analyst_vacancy_trend_by_year(df, output_path):
    df_copy = df.copy()
    # Сводная таблица по годам
    df_copy_count_pivot = df_copy.pivot_table(index='year', values='name', aggfunc='count').reset_index()

    # График динамики по годам
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_facecolor('#F1F1F1')
    plt.gcf().set_facecolor('#F1F1F1')
    plt.bar(df_copy_count_pivot['year'], df_copy_count_pivot['name'])
    plt.plot(df_copy_count_pivot['year'], df_copy_count_pivot['name'], color='red', marker='.')
    plt.xticks(df_copy_count_pivot['year'])
    plt.title("Динамика количества вакансий аналитика по годам")
    plt.grid(axis='y')
    plt.savefig(output_path)
    plt.close()


# -------------------------------------------------------------------------------------------------------Skills

# Построение графика топ-N навыков для аналитика
def plot_top_skills_overall(df, output_path, top_n=20):
    # Оставляем только строки с ненулевыми и непустыми ключевыми навыками
    all_skills = df[df['key_skills'].notna()]['key_skills']
    all_skills = all_skills.str.cat(sep='\n').split('\n')

    # Подсчёт частоты
    skill_freq = Counter(all_skills)
    top_skills = dict(islice(sorted(skill_freq.items(), key=lambda x: x[1], reverse=True), top_n))

    # Построение DataFrame
    skills_frame = pd.DataFrame.from_dict(top_skills, orient='index', columns=['freq']).reset_index()
    skills_frame.columns = ['Навык', 'Частота']
    skills_frame = skills_frame.sort_values(by='Частота', ascending=False).reset_index(drop=True)
    skills_frame.index = skills_frame.index + 1

    # Построение графика
    plt.figure(figsize=(17, 13))
    plt.barh(skills_frame['Навык'], skills_frame['Частота'], color='mediumpurple')
    plt.title(f'ТОП-{top_n} навыков (все годы)')
    plt.xlabel('Частота')
    plt.grid(axis='x')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

# -------------------------------------------------------------------------------------------------------Recent Vacancies

def get_recent_analyst_vacancies(df, top_n=20):
    """
    Возвращает таблицу из top_n последних аналитических вакансий.
    """
    df = filter_data_by_keywords(df)
    df = df.sort_values(by='published_at', ascending=False)
    
    # Выбираем нужные столбцы (можно расширить по желанию)
    columns = ['published_at', 'name', 'area_name', 'employer_name', 'average_salary', 'alternate_url']
    existing_columns = [col for col in columns if col in df.columns]
    return df[existing_columns].head(top_n)



# -------------------------------------------------------------------------------------------------------ConvertRub.

# Функция для получения всех курсов валют с сайта ЦБ РФ
def get_all_exchange_rates():
    url = "https://cbr.ru/scripts/XML_daily.asp"
    response = requests.get(url)
    if response.status_code == 200:
        tree = ElementTree.fromstring(response.content)
        rates = {"RUR": 1.0}  # Базовая валюта — рубль
        for currency in tree.findall("Valute"):
            char_code = currency.find("CharCode").text
            # Преобразуем код валюты, если есть в маппинге
            char_code = currency_mapping.get(char_code, char_code)
            value = float(currency.find("Value").text.replace(",", "."))
            nominal = int(currency.find("Nominal").text)
            rates[char_code] = value / nominal  # Курс за одну единицу валюты
        return rates
    return {}

# Сопоставление некоторых валют с их названиями
currency_mapping = {
    "Манаты": "Азербайджанский манат",
    "Белорусские рубли": "Белорусский рубль",
    "Евро": "Евро",
    "Грузинский лари": "Лари",
    "Киргизский сом": "Сомов",
    "Тенге": "Тенге",
    "Гривны": "Гривен",
    "Доллары": "Доллар США",
    "Узбекский сум": "Узбекских сумов",
}

# Функция для конвертации зарплаты в рубли по курсу
def convert_to_rub(row, currency_to_rub):
    currency = row['currency']
    # Если валюта есть в маппинге и среди курсов, конвертируем
    if currency in currency_mapping and currency_mapping[currency] in currency_to_rub:
        return row['average_salary'] * currency_to_rub[currency_mapping[currency]]
    return row['average_salary']


# -------------------------------------------------------------------------------------------------------save_table_as_image


def save_table_as_image(df, output_path):
    max_col_width = 35
    df_wrapped = df.copy()

    # Перенос длинных текстов
    for col in df_wrapped.columns:
        df_wrapped[col] = df_wrapped[col].apply(
            lambda x: '\n'.join(textwrap.wrap(str(x), max_col_width)) if pd.notnull(x) else ''
        )

    # Вычисление размеров
    row_height = 0.5
    font_size = 8
    fig_height = max(2, row_height * len(df_wrapped) + 1.5)
    fig_width = 2 + len(df.columns) * 2
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')

    # Построение таблицы
    table = ax.table(
        cellText=df_wrapped.values,
        colLabels=df_wrapped.columns,
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    table.scale(1.2, 3.2)

    # Сохраняем
    try:
        plt.tight_layout()
        plt.savefig(output_path, dpi=200, bbox_inches='tight')
    except Exception as e:
        print(f"Ошибка при сохранении изображения: {e}")
    finally:
        plt.close(fig)
