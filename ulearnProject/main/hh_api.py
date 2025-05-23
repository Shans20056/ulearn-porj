import requests


def get_hh_vacancies(keyword, area=113, period=1, per_page=10):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": area,
        "period": period,
        "per_page": per_page,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['items']
    else:
        return []


def get_vacancy_details(vacancy_id):
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
