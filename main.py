from src.classes import SuperJob, Connector, HeadHunter
from src.utils import filter_by_keyword, filter_by_platform


def main():
    hh_vacancies_json = []  # Отдельный список для вакансий с HeadHunter
    sj_vacancies_json = []  # Отдельный список для вакансий с SuperJob

    keyword = input('Введите ключевое слово для поиска вакансий: ')
    hh = HeadHunter(keyword)
    sj = SuperJob(keyword)

    for api in (sj, hh):
        api.get_vacancies(pages_count=5)
        if isinstance(api, HeadHunter):
            hh_vacancies_json.extend(api.get_formatted_vacancies())
        elif isinstance(api, SuperJob):
            sj_vacancies_json.extend(api.get_formatted_vacancies())

    # Объединяем вакансии из обоих источников
    vacancies_json = hh_vacancies_json + sj_vacancies_json

    connector = Connector(keyword=keyword, vacancies_json=vacancies_json)

    vacancies = connector.select()
    # Цикл работы функцкий для пользователя
    while True:
        command = input(
            "1 - Вывести список вакансий; \n"
            "2 - Поиск по ключевому слову; \n"
            "3 - ТОП вакансий по зарплате; \n"
            "4 - Фильтр по платформе(HH or SuperJob); \n"
            ">>> \n"
            "exit - для выхода"
        )
        if command.lower() == 'exit':
            break
        elif command == "1":
            vacancies = connector.select()
        elif command == "2":
            keyword = input("Введите ключевое слово для фильтрации: ")
            vacancies = filter_by_keyword(vacancies, keyword)
            if not vacancies:
                print("Нет вакансий, соответствующих ключевому слову.")
            else:
                for vacancy in vacancies:
                    print(vacancy, end='\n')
        elif command == "3":
            try:
                n = int(input("Введите количество вакансий для отображения: "))
                if n > 0:
                    top_n_highest_paid = sorted(
                        [v for v in vacancies if v.salary_to is not None],
                        key=lambda x: x.salary_to,
                        reverse=True)[:n]
                    if not top_n_highest_paid:
                        print("Нет вакансий с указанной зарплатой.")
                    else:
                        print(f"Топ {n} вакансий с самой крупной зарплатой:")
                        for vacancy in top_n_highest_paid:
                            print(vacancy, end='\n')
                else:
                    print("Введите положительное число.")
            except ValueError:
                print("Введите корректное число.")
        elif command == "4":
            platform = input("Введите платформу (hh или superjob) для фильтрации: ")
            vacancies = filter_by_platform(vacancies, platform)
            for vacancy in vacancies:
                print(vacancy, end='\n')


if __name__ == "__main__":
    main()
