from pprint import pprint
import re
import sys
import csv

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

# читаем адресную книгу в формате CSV в список contacts_list
mode = 'r'
encoding = 'utf-8'
with open("phonebook_raw.csv", mode=mode, encoding=encoding) as f:
  rows = csv.reader(f, delimiter=",")
  contacts_list = list(rows)

# Создание паттерна для нахождения имен(по условию должны быть как минмум Имя и Фамилия)
fio_pattern = r'([А-ЯЁ][а-яё]+[\s\,]?){2,3}'
# Инициализация переменных
preliminary_list = []
final_list = []
info_dict = {}

# Создание упорядочкнной адресной книги (включая дубликаты)
for line in contacts_list:
    # Приведение строкового массива к строке(разделитель ",")
    str = ','.join([item for item in line])
    # Нахождение совпадений ФИО по заданному паттерну
    fio = re.match(fio_pattern, str)
    # При нахождении совпадений создаем упорядоченную структуру данных
    if fio:
        # Приведение Ф, ИО; ФИ,О и ФИО к единому формату [Ф, И, О]
        fio_list = fio.group().rstrip(',').replace(',', ' ').split(' ')
        # Если отчество отсутствует(по услофию ФИ - обязательны), то получаем [Ф, И, '']
        if len(fio_list) < 3:
            fio_list.append('')
        # Обогощение массива с ФИО остальными данными из адресной книги
        organization = line[3]
        position = line[4]
        phone = line[5]
        email = line[6]
        preliminary_list.append(fio_list + [organization] + [position] + [phone] + [email])
preliminary_list.insert(0, contacts_list[0])

# Получение словаря с максимально возможной информацией по каждому человеку
i = 0
while i < len(preliminary_list):
    row = preliminary_list[i]
    # Создание уникального ключа ФамилияИмя
    lf_names = row[0] + row[1]
    # Получение дополнительной информации из дублированных записей
    for line in preliminary_list:
        lf_names_line = line[0] + line[1]
        if lf_names == lf_names_line:
            k = 2
            while k < len(row):
                if row[k] == '' and line[k] != '':
                    row[k] = line[k]
                k += 1
    # Избавление от дублируемых записей
    info_dict[lf_names] = ','.join(row)
    i += 1

# Формирование паттернов поиска и замены для номера телефона и добавочного кода
### Пытался сделать через 1 паттерн (\+7|8)?\s*\(*(\d{3})\)*[ -]*(\d{3})[- ]*(\d{2})[ -]*(\d{2})|\s*\(*(\w+\.)\s*(\d+)\)*
### но при замене дублировался паттерн замены номера телефона, получалось +7(xxx)xxx-xx-xx +7() доб.xxxx
### поэтому разделил на 2 паттерна и последовательно заменил номер телефона, а затем добавочный номер
phone_pattern = r'(\+7|8)?\s*\(*(\d{3})\)*[ -]*(\d{3})[- ]*(\d{2})[ -]*(\d{2})'
code_pattern = r'\s*\(*(\w+\.)\s*(\d+)\)*'
phone_sub = r'+7(\2)\3-\4-\5'
code_sub = r' \1\2'

# Замена номера телефона и добавочного кода на стандартизированные значения
for v in info_dict.values():
    phone_res = re.sub(phone_pattern, phone_sub, v)
    code_res = re.sub(code_pattern, code_sub, phone_res)
    final_list.append(code_res.split(','))


# Запись результата в csv
with open("phonebook.csv", "w", encoding=encoding) as f:
  datawriter = csv.writer(f, delimiter=',')
  datawriter.writerows(final_list)
        

