import time
from abc import ABC, abstractmethod
from exceptions import ParsingError
from utils import get_currencies
import requests
import json
from pprint import pprint


class Engine(ABC):

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass

class HeadHunter(Engine):
    pass

class SuperJob(Engine):
    url = "https://api.superjob.ru/2.0/vacancies"

    def __init__(self, keyword):
        self.params = {
            "count": 100,
            "page": None,
            "keyword": keyword,
            "archive": False,
        }
        self.headers = {
            "X-Api-App-Id": "v3.r.13024832.33705f4ab095c630798f090d8b49ed8dafc4830f.2186b01470be5a1c83d0d39874bb414924261f1a "
        }
        self.vacancies = []

    def get_request(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения вакансий! Статус: {response.status_code}")
        return response.json()["objects"]

    def formatted_vacancies(self):
        formatted_vacancies = []
        currencies = get_currencies()
        sj_currencies = {
            "rub": "RUR",
            "uah": "UAH",
            "uzs": "UZS"
        }

        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["firm_name"],
                "title": vacancy["profession"],
                "url": vacancy["link"],
                "api": "SuperJob",
                "salary_from": vacancy["payment_from"] if vacancy["payment_from"] and vacancy["payment_from"] != 0 else None,
                "salary_to": vacancy["payment_to"] if vacancy["payment_to"] and vacancy["payment_to"] != 0 else None,
            }
            if vacancy["currency"] in sj_currencies:
                formatted_vacancy["currency"] = sj_currencies[vacancy["currency"]]
                formatted_vacancy["currency_value"] = currencies[sj_currencies[vacancy["currency"]]] if sj_currencies[vacancy["currency"]] in currencies else 1
            elif vacancy["currency"]:
                formatted_vacancy["currency"] = "RUR"
                formatted_vacancy["currency_value"] = 1
            else:
                formatted_vacancy["currency"] = None
                formatted_vacancy["currency"] = None

            formatted_vacancies.append(formatted_vacancy)
        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
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
                print(f"Загружено вакансий: {page_vacancies}")
            if len(page_vacancies) == 0:
                break