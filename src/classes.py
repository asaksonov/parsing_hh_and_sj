from abc import ABC, abstractmethod
from src.exceptions import ParsingError
from src.utils import get_currencies
import requests
import json


class Engine(ABC):

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunter(Engine):
    """
    Класс для работы с api HeadHunter
    """
    url = "https://api.hh.ru/vacancies"

    def __init__(self, keyword):
        self.params = {
            "per_page": 100,  # Количество вакансий на странице
            "page": 0,  # Страница с вакансиями
            "text": keyword,  # Поисковый запрос
        }
        self.vacancies = []

    def get_request(self):
        """
        Функция запроса к HeadHunter
        """
        response = requests.get(self.url, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения вакансий! Статус:{response.status_code}")
        return response.json()["items"]

    def get_formatted_vacancies(self):
        """
        Функция форматирования вакансий HeadHunter
        """
        formatted_vacancies = []
        currencies = get_currencies()
        hh_currencies = {
            "RUR": "RUB",
        }
        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["employer"]["name"],
                "title": vacancy["name"],
                "url": vacancy["alternate_url"],
                "api": "headhunter",
            }

            salary_info = vacancy.get("salary")  # Получаем информацию о зарплате, если она существует

            if salary_info:
                formatted_vacancy["salary_from"] = salary_info.get("from")
                formatted_vacancy["salary_to"] = salary_info.get("to")

                currency = salary_info.get("currency")
                if currency in hh_currencies:
                    formatted_vacancy["currency"] = hh_currencies[currency]
                    formatted_vacancy["currency_value"] = currencies[hh_currencies[currency]]
                else:
                    formatted_vacancy["currency"] = None
                    formatted_vacancy["currency_value"] = None
            else:
                formatted_vacancy["salary_from"] = None
                formatted_vacancy["salary_to"] = None
                formatted_vacancy["currency"] = None
                formatted_vacancy["currency_value"] = None

            formatted_vacancies.append(formatted_vacancy)
        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        """
        Функция получения вакансий с HeadHunter
        """
        self.vacancies = []
        for page in range(pages_count):
            self.params["page"] = page
            print(f"({self.__class__.__name__}) Парсинг страницы {page} -", end=" ")
            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}")



class SuperJob(Engine):
    """
    Класс для работы с api SuperJob
    """
    url = "https://api.superjob.ru/2.0/vacancies/"

    def __init__(self, keyword):
        self.params = {
            "count": 100,
            "page": None,
            "keyword": keyword,
            "archive": False,
        }
        self.headers = {
            "X-Api-App-Id": "v3.r.13024832.33705f4ab095c630798f090d8b49ed8dafc4830f.2186b01470be5a1c83d0d39874bb414924261f1a"
        }
        self.vacancies = []

    def get_request(self):
        """
        Функция запроса вакансий с Superjob
        """
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения вакансий! Статус:{response.status_code}")
        return response.json()["objects"]




    def get_formatted_vacancies(self):
        """
        Функция форматирования вакансий с Superjob
         """
        formatted_vacancies = []
        currencies = get_currencies()
        sj_currencies = {
            "rub": "RUB",
            "uah": "UAH",
            "uzs": "UZS",
        }

        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["firm_name"],
                "title": vacancy["profession"],
                "url": vacancy["link"],
                "api": "superjob",
                "salary_from": vacancy["payment_from"] if vacancy["payment_from"] and vacancy[
                    "payment_from"] != 0 else None,
                "salary_to": vacancy["payment_to"] if vacancy["payment_to"] and vacancy["payment_to"] != 0 else None,
            }

            if vacancy["currency"] in sj_currencies:
                formatted_vacancy["currency"] = sj_currencies[vacancy["currency"]]
                formatted_vacancy["currency_value"] = currencies[sj_currencies[vacancy["currency"]]] if sj_currencies[
                                                                                                                  vacancy[
                                                                                                                      "currency"]] in currencies else 1
            elif vacancy["currency"]:
                formatted_vacancy["currency"] = "RUB"
                formatted_vacancy["currency_value"] = 1
            else:
                formatted_vacancy["currency"] = None
                formatted_vacancy["currency_value"] = None

            formatted_vacancies.append(formatted_vacancy)
        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        """
        Функция получения вакансий с Superjob
        """
        self.vacancies = []
        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f"({self.__class__.__name__}) Парсинг страницы {page} -", end=" ")
            try:
                    page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}")


class Vacancy:

    def __init__(self, vacancy):
        self.employer = vacancy["employer"]
        self.title = vacancy["title"]
        self.url = vacancy["url"]
        self.api = vacancy["api"]
        self.salary_from = vacancy["salary_from"]
        self.salary_to = vacancy["salary_to"]
        self.currency = vacancy["currency"]
        self.currency_value = vacancy["currency_value"]

    def __str__(self):
        salary_str = f"Зарплата: от {self.salary_from} {self.currency}" if self.salary_from is not None else ""
        if self.salary_to is not None:
            salary_str += f" до {self.salary_to} {self.currency}" if salary_str else f"Зарплата: до {self.salary_to} {self.currency}"
        return f"""
Работодатель: \"{self.employer}\"
Вакансия: \"{self.title}\"
{salary_str}
Ссылка: \"{self.url}\"
        """



class Connector:

    def __init__(self, keyword, vacancies_json):
        self.filename = f"{keyword.title()}.json"
        self.insert(vacancies_json)

    def insert(self, vacancies_json):
        with open(self.filename, 'w') as file:
            json.dump(vacancies_json, file, indent=4, ensure_ascii=False)

    def select(self):
        with open(self.filename, 'r') as file:
            vacancies = json.load(file)

        return [Vacancy(x) for x in vacancies]
