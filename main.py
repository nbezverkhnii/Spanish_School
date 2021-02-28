"""
Этот скрипт реализует решение задачи о поиске уникальных для каждого урока курса слова.
Текущая версия работает с фалйми формата .txt, но может быть легко доработана для работы с другими
фаорматами текстовых файлов.
Реализован класс для анализа частотности испанских слов в тексте уроков.
Класс осуществляет препроцессинг и процессинг слов, позволяет увидеить гистограмму частотности урока,
вывести данные в различных формах: list, set, pd.Series.
Данные сохраняются в формате .xls.
"""
import os
import re
from typing import Optional
from functools import reduce
from operator import itemgetter
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords


class WordAnalyser:
    """
    Класс для работы каждого урока курса.
    Содержит логику обработки текста и набор уникальных слов.
    Имеются методы для работы и вывода слов в различной форме, а также орисовки диаграмы частотности.
    """
    URL = re.compile(r'(http|ftp|https)://([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-.,@?^=%&:/~+#]*[\w\-@?^=%&/~+#])?',
                     flags=re.MULTILINE)
    RU = re.compile("[1-9]+|[а-яА-Я]+")
    UNDERSCORES = re.compile(r'\b_{1,40}\b', flags=re.MULTILINE)
    SINGLE_CHARS = [chr(i) for i in range(97, 123)] + [chr(0x00F1)]  # Буквы латинского алфавита

    def __init__(self, lesson_filename: str) -> None:
        """
        Конструктор классаWordAnalyser

        :param lesson_filename: str
            Имя файла, содержащего текст урока
        """
        self.__filename = self.set_filename(lesson_filename)
        self.__text = self.read_text(self.__filename)
        self.__all_words = self.get_all_words(self.__text)

    @staticmethod
    def set_filename(filename_of_lesson: str) -> Optional[str]:
        """
        Осуществляет проверку сущестования файла.

        :param filename_of_lesson: str
            Имя файла, содержащего текст урока
        :return:
            Имя файла
        """
        if not os.path.exists(filename_of_lesson):
            raise FileNotFoundError('Файл не найден')

        return filename_of_lesson

    @staticmethod
    def read_text(filename: str) -> str:
        """
        Чтение текста из файла в одну стоку

        :param filename:
            Имя файла
        :return:
            Строка, содержащая весь текст урока
        """
        with open(filename) as file:
            data = file.read()

        return data

    def get_all_words(self, text: str) -> list:
        """
        Метод производит предобработку и обработку текста.
        Используя регулярные выражения из текста исключаются гиперссылки,
        удаляются слова на русском языке, одиночные буквы, а также различные
        атрибуты, например, последовательность нижних подчеркиваний.

        text: str
            Строка содержащая весь текст урока
        return: list
            Список всех слова на испанском языке
        """
        text = self.URL.sub('', text)

        tokenizer = nltk.tokenize.RegexpTokenizer('\w+')
        tokens = tokenizer.tokenize(text.lower())

        ru_words = [w for w in filter(self.RU.match, tokens)]
        underscores_words = [w for w in filter(self.UNDERSCORES.match, tokens)]
        sw = stopwords.words('spanish') + stopwords.words('russian') + self.SINGLE_CHARS
        set_of_exclusion_words = set(ru_words + underscores_words + sw)

        words = [word.lower() for word in tokens if word not in set_of_exclusion_words]

        return words

    def get_words_set(self) -> set:
        """
        Возвращает множество уникальных слов урока

        :return: set
            Множество уникальных слов урока
        """
        return set(self.__all_words)

    def n_freq_words(self, n_of_words: int) -> dict:
        """
        Метод создает словарь в котором в качестве ключа - слова,
        а в качестве значения - количество повторений этого слова в тексте

        :param n_of_words:
            Количество слов в топе частотности
        :return: dict
            Словарь, содержащий n_of_words слов в порядке убывания их частотности
        """
        freqdist = nltk.FreqDist(self.__all_words)
        sort_dic = {k: v for k, v in sorted(freqdist.items(), key=lambda item: item[1], reverse=True)[:n_of_words]}

        return sort_dic

    def draw_hist_freq(self, n_of_words: int) -> None:
        """
        Метод строит гистограмму частотности.
        В гистограммы n_of_words слов

        :param n_of_words: int
            Количество слов в гистограмме
        :return: None
        """
        sort_dic = self.n_freq_words(n_of_words)

        plt.rcParams.update({'font.size': 16})
        plt.figure(figsize=(10, 6))

        plt.bar(*zip(*sort_dic.items()))
        plt.xticks(rotation=70)

        plt.ylabel('Повторений в тексте')
        plt.title(f'{n_of_words} самых часто повторяемых слов')
        plt.grid()
        plt.show()

    def get_pd_series(self) -> pd.Series:
        """
        Возвращает pd.Series уникальных слова урока
        Можно будет собрать несколько pd.Series в один pd.DataFrame

        :return: pd.Series
            Столбец уникальных слов урока
        """
        series_name = self.__filename.split('/')[-1]

        freqdist = dict(nltk.FreqDist(self.__all_words))
        freqdist = sorted(freqdist.items(), key=itemgetter(1), reverse=True)
        list_of_unic_sorted_words = [value[0] for value in freqdist]

        return pd.Series(list_of_unic_sorted_words, name=series_name)


def create_unic_tup(list_of_sets: list, output_list: list) -> None:
    """
    Функция заполняет список output_list множествами слов.
    Это такие слова, которые встречаются только в этом уроке,
    и не встречаются ни в одном другом.

    :param list_of_sets: list
        Список, содержащий уникальные слова каждого урока
    :param output_list: list
        Список, который будет заполняться
    :return: None
    """
    for i, v in enumerate(list_of_sets):
        output_list.append(v.difference(reduce(lambda x, y: x | y, list_of_sets[:i] + list_of_sets[i + 1:])))


if __name__ == '__main__':
    # Этот список должен содержать пукть к текстовым файлам уроков в формате .txt
    lesson_file_list = [
        '...1.txt',
        '...2.txt',
        '...3.txt',
        '...4.txt',
        '...5.txt',
        '...6.txt',
        '...7.txt',
        '...8.txt'
    ]

    # Список объектов WordAnalyser для каждого из файлов (уроков) из lesson_file_list
    list_of_analyser = [WordAnalyser(value) for value in lesson_file_list]
    # Множеств (уникальных слов) всех уроков из list_of_analyser
    list_of_sets = [object.get_words_set() for object in list_of_analyser]
    # Список pd.Series всех уроков
    list_of_series = [object.get_pd_series() for object in list_of_analyser]

    # Собираем все pd.Series из list_of_series в одну таблицу и сохраняем в таблицу
    result = pd.concat(list_of_series, axis=1)
    result.to_excel('lessons.xls', index=False)

    # Теперь получим уникальные (в рамках курса) для каждого урока слова
    list_of_unic_words = []
    create_unic_tup(list_of_sets, list_of_unic_words)
    unic_words_df = pd.DataFrame(list_of_unic_words).T
    unic_words_df.columns = [name.split('/')[-1] for name in lesson_file_list]
    unic_words_df.to_excel('unic_lessons.xls', index=False)
