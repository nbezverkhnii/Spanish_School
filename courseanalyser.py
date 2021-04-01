"""
Реализован класс для анализа частотности испанских слов в тексте уроков.
Класс осуществляет препроцессинг и процессинг слов, позволяет увидеить гистограмму частотности урока,
вывести данные в различных формах: list, set, pd.Series.
Данные сохраняются в формате .xls.
"""
from functools import reduce
from typing import Any

import pandas as pd

from wordanalyser import WordAnalyser


class CourseAnalyser:
    """
    Класс для работы с курсом (состоящим из нескольких уроков)
    Каждый отдельный курок ный урок представлен классом WordAnalyser
    """

    def __init__(self):
        self._list_of_files = []
        self.list_of_analyser = []
        self.list_of_sets = []
        self.list_of_series = []
        self.list_of_dicts = []

    @property
    def list_of_files(self):
        return self._list_of_files

    @list_of_files.setter
    def list_of_files(self, input_list: list):
        self._list_of_files = input_list
        self.build_another_lists()

    def build_another_lists(self) -> None:
        """
        Метод инициализирует аттрибуты экземпляра класса, после объявления списков файлов уроков
        Создаются аттрибуты list_of_analyser, list_of_sets, list_of_series, list_of_dicts
        :return: None
        """
        # Список объектов WordAnalyser для каждого из файлов (уроков) из lesson_file_list
        self.list_of_analyser = [WordAnalyser(value) for value in self._list_of_files]
        # Множеств (уникальных слов) всех уроков из list_of_analyser
        self.list_of_sets = [value.get_words_set() for value in self.list_of_analyser]
        # Список pd.Series всех уроков
        self.list_of_series = [value.get_pd_series() for value in self.list_of_analyser]
        # Список словарей уникальных слов
        self.list_of_dicts = [value.freq_words_dict() for value in self.list_of_analyser]

    def series_to_exel(self) -> None:
        """
        Собираем все pd.Series из list_of_series в одну таблицу и сохраняем в таблицу
        """
        if not self.list_of_series:
            print('list_of_files а пуст. Пожалуйста, задайте list_of_files')
            return None

        result = pd.concat(self.list_of_series, axis=1)
        result.to_excel('lessons.xls', index=False)

    def create_unic_tup(self) -> list:
        """
        Функция заполняет список output_list множествами слов.
        Это такие слова, которые встречаются только в этом уроке,
        и не встречаются ни в одном другом.

        :return: None
        """
        output_list = []
        for i, v in enumerate(self.list_of_sets):
            output_list.append(
                v.difference(reduce(lambda x, y: x | y, self.list_of_sets[:i] + self.list_of_sets[i + 1:])))

        return output_list

    def u_c_w(self):
        """
        Теперь получим уникальные (в рамках курса) для каждого урока слова
        """
        unic_words_df = pd.DataFrame(self.create_unic_tup()).T
        unic_words_df.columns = [name.split('/')[-1] for name in self._list_of_files]
        unic_words_df.to_excel('unic_lessons.xls', index=False)

    @staticmethod
    def is_it_str(word: Any) -> None:
        if not isinstance(word, str):
            raise TypeError('Тут должна быть строка')

    def search_word(self, word: str) -> list:
        """
        Метод определяет в каких уроках (порядковые номера) встречается слово word

        :param word: str
            Слоло для поиска
        :return: list
            Список порядковых номеров уроков в котрых встречется слово
        """
        self.is_it_str(word)
        result = [item + 1 for item, lesson in enumerate(self.list_of_sets) if word in lesson]
        return result

    def word_count(self, word: str) -> list:
        """
        На самом деле слова уже подсчитаны ранее
        Метод подготовливает список для создания pd.DataFrame

        :param word: str
            Слово для анлиза
        :return: list
            Список, содержащий tuples: (порядковы номер урока, количество повторений слова word)
        """
        self.is_it_str(word)
        # Можно было сделать через list comprehension, но получается нечитаемо
        result = []
        for item, lesson in enumerate(self.list_of_dicts):
            if word in lesson:
                result.append((item + 1, lesson[word]))
            else:
                result.append((item + 1, 0))

        return result

    def stat_about_word(self, word: str) -> None:
        """
        Метод записывает статистику отдельно взятого слова в текстовый файл

        :param word: str
            Слово о котором хочешь узнать статистику
        :return: None
        """
        self.is_it_str(word)

        result_str = ''
        result_str += f'Слово {word}\n'
        for val in self.word_count(word):
            result_str += f'В {val[0]} уроке: {val[1]}\n'
        result_str += '\n'

        with open(f'word_statistic.txt', 'a') as file:
            file.write(result_str)

    def stat_of_set(self, set_: set) -> None:
        """
        Метод подсчитывает сатистику слова для отднльного множества слов
        Такое множество может быть отдебно взятьм уроком
        К каждом слову такого урока применяется метод stat_about_word

        :param set_:
            Множество
        :return: None
        """
        for word in set_:
            self.stat_about_word(word)

    def full_statistic_table(self) -> None:
        """
        Метод, создающий таблицу, содержащую всю статистику слов за курс.
        Создается файл формата .xls, в котором содержится информация о повторяемости слов в курсе
        По строкам таблицы: слова, по столбцам - уроки (порядковые номера уроков), в ячейках - количество повторений
        слова в уроке.

        :return: None
        """
        if not self.list_of_sets:
            print('list_of_files а пуст. Пожалуйста, задайте list_of_files')
            return None

        full_words_set = set.union(*self.list_of_sets)
        table = [[number for lesson, number in self.word_count(word)] for word in full_words_set]
        df = pd.DataFrame(list(full_words_set), columns=['Слова'])
        df2 = pd.DataFrame(table, columns=[i for i in range(1, len(self.list_of_sets)+1)])
        result = pd.concat([df, df2], axis=1)

        # Если вдруг в столбец Слова попались не слова,а что-нибудь еще, то удаляем эти строки
        result = result[result['Слова'].apply(lambda x: x.isalpha())]
        # Сохраняем таблицу в Exel
        result.to_excel('full_statistics.xlsx', index=False)
