"""
Этот скрипт реализует решение задачи о поиске уникальных для каждого урока курса слова.
Текущая версия работает с фалйми формата .txt, но может быть легко доработана для работы с другими
фаорматами текстовых файлов.
"""
from courseanalyser import CourseAnalyser


if __name__ == '__main__':
    # Директория с текстовыми файлами уроков в формате .txt
    files_path = ''
    # Создаем экземпляр класса CourseAnalyser
    course = CourseAnalyser()

    # Этот список должен содержать пукти к текстовым файлам уроков в формате .txt
    lesson_file_list = [
        files_path + '1.txt',
        files_path + '2.txt',
        files_path + '3.txt',
        files_path + '4.txt',
        files_path + '5.txt',
        files_path + '6.txt',
        files_path + '7.txt',
        files_path + '8.txt',
        files_path + '9.txt',
        files_path + '10.txt',
        files_path + '11.txt',
        files_path + '12.txt',
        files_path + '13.txt',
        files_path + '14.txt',
        files_path + '15.txt',
        files_path + '16.txt',
        files_path + '17.txt',

    ]

    # Передаем свойству экземляра класса course список файлов (уроков)
    course.list_of_files = lesson_file_list
    # Строим таблицу статистики
    course.full_statistic_table()
