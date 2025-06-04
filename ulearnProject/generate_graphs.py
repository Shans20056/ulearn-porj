import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ulearnProject.settings")

from django.conf import settings
from main.analytics import (
    load_data, preprocess_data, plot_salary_trends, plot_vacancy_trends,
    plot_analyst_vacancy_trend_by_year, plot_city_vacancy_share, plot_top_skills_overall, 
    filter_data_by_keywords, get_recent_analyst_vacancies, save_table_as_image
)


def generate_graphs():
    csv_path = os.path.join(settings.BASE_DIR, 'main', 'static', 'database', 'vacancies_2024.csv')
    
    df = load_data(csv_path)
    df = preprocess_data(df)
    filtered_df = filter_data_by_keywords(df)

    # Папка для сохранения графиков и файлов
    output_dir = os.path.join(settings.BASE_DIR, 'main', 'static', 'database')
    os.makedirs(output_dir, exist_ok=True)

    # Пути для графиков
    salary_trends_path = os.path.join(output_dir, 'salary_trends.png')
    vacancy_trends_path = os.path.join(output_dir, 'vacancy_trends.png')
    salary_by_city_path = os.path.join(output_dir, 'salary_by_city.png')
    vacancy_share_path = os.path.join(output_dir, 'vacancy_share.png')
    top_skills_path = os.path.join(output_dir, 'top_skills.png')

    # 📈 Генерация графиков
    plot_salary_trends(filtered_df, salary_trends_path)
    plot_vacancy_trends(df, filtered_df, vacancy_trends_path)
    plot_analyst_vacancy_trend_by_year(filtered_df, salary_by_city_path)
    plot_city_vacancy_share(filtered_df, vacancy_share_path)
    plot_top_skills_overall(filtered_df, top_skills_path)

    # 🆕 Сохранение последних вакансий аналитика в CSV
    recent_vacancies = get_recent_analyst_vacancies(df, top_n=15)
    recent_vacancies_path = os.path.join(output_dir, 'recent_vacancies.png')
    save_table_as_image(recent_vacancies, recent_vacancies_path)
    recent_vacancies_path = os.path.join(output_dir, 'recent_vacancies.csv')
    recent_vacancies.to_csv(recent_vacancies_path, index=False, encoding='utf-8-sig')  # для Excel и кириллицы


if __name__ == "__main__":
    generate_graphs()
