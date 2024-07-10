import json

import requests
from bs4 import BeautifulSoup as bs


def get_web_page(page: int, vacancies_on_page: int) -> tuple[list[bs], int]:
    url = (f"https://spb.hh.ru/search/vacancy?L_save_area=true"
           f"&search_field=name"
           f"&search_field=description&area=1&area=2"
           f"&items_on_page={vacancies_on_page}"
           f"&enable_snippets=false"
           f"&currency_code=USD&text=Python+django+flask&only_with_salary=true"
           f"&page={page}")
    try:
        hh = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if hh.status_code != 200:
            raise requests.exceptions.ConnectionError
    except requests.exceptions.ConnectionError:
        print("Нет соединения с сайтом")
        exit()
    soup = bs(hh.text, "html.parser")
    all_vacancies = soup.find_all("div", class_="vacancy-card--z_UXteNo7bRGzxWVcL7y")
    page += 1
    return all_vacancies, page


def write_vacancies_to_list(all_vacancies: list[bs], vacancy_list: list[dict]):
    for vacancy in all_vacancies:
        vacancy_data = {
            "title":
                vacancy.find("span", class_="serp-item__title-link").text,
            "link":
                vacancy.find("a", class_="bloko-link").get("href"),
            "salary":
                vacancy.find("span", class_="separate-line-on-xs--mtby5gO4J0ixtqzW38wh")
                .text.replace("\u202f", "").replace("\xa0", " "),
            "company":
                vacancy.find("span", class_="company-info-text--vgvZouLtf8jwBmaD1xgp")
                .text.replace("\xa0", " "),
            "city":
                vacancy.find("span", {'data-qa': 'vacancy-serp__vacancy-address'}).text,
        }
        vacancy_list.append(vacancy_data)


def write_to_file(data: list[dict], file_name: str):
    with open(f"{file_name}", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    page = 0
    vacancies_on_page = 20
    json_file_name = "vacancies.json"
    vacancy_list = []
    while True:
        all_vacancies, page = get_web_page(page, vacancies_on_page)
        if not all_vacancies:
            break
        print(f"Страница {page} получена, всего вакансий на странице: {len(all_vacancies)}")
        write_vacancies_to_list(all_vacancies, vacancy_list)
        if len(all_vacancies) < vacancies_on_page:
            break
    print(f"Всего вакансий найдено: {len(vacancy_list)}")
    write_to_file(vacancy_list, json_file_name)
    print(f"Вакансии записаны в файл {json_file_name}")


if __name__ == '__main__':
    main()
