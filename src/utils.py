from ast import parse
from configparser import ParsingError

import requests


def get_currencies():
    responce = requests.get("http://www.cbr.ru/scripts/XML_daily.asp")

    try:
        if responce.status_code != 200:
            raise ParsingError(f"Ошибка получения курса валюты! Статус {responce.status_code}")
        currencies = parse(responce.content)
        formatted_currencies = {}
        for currency in currencies["ValCurs"]["Valute"]:
            value = float(currency["Value"].replace(",", "."))
            nominal = float(currency["Nominal"])
            formatted_currencies[currency["CharCode"]] = value / nominal
        formatted_currencies["RUR"] = 1
        return formatted_currencies
    except ParsingError as error:
        print(error)

cer = get_currencies()
print(cer)