import requests
import xml.etree.ElementTree as ET
from src.exceptions import ParsingError


def get_currencies():
    """
    Функция парсинга курса валюты с сайта ЦБ
    """
    try:
        response = requests.get("https://www.cbr.ru/scripts/XML_daily.asp")
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения курса валют! Статус:{response.status_code}")

        root = ET.fromstring(response.content)
        formatted_currencies = {}
        for valute in root.findall('Valute'):
            char_code = valute.find('CharCode').text
            value = float(valute.find('Value').text.replace(',', '.'))
            nominal = int(valute.find('Nominal').text)
            rate = value / nominal
            formatted_currencies[char_code] = rate

        formatted_currencies['RUB'] = 1.0
        return formatted_currencies
    except ParsingError as error:
        print(error)


def filter_by_keyword(vacancies, keyword):
    """
    Функция поиска по введенному пользователю слову
    """
    filtered_vacancies = []
    keyword = keyword.lower()

    for vacancy in vacancies:
        if keyword in vacancy.title.lower() or keyword in vacancy.employer.lower():
            filtered_vacancies.append(vacancy)

    return filtered_vacancies


def filter_by_platform(vacancies, platform):
    """
    Функция фильтрации вакансий по платформе
    """
    return [vacancy for vacancy in vacancies if vacancy.api.lower() == platform.lower()]

