# Программа принимает 2 изображения:
# 1. Изображение, на котором нужно найти все элементы, сохранить их в папке elem
# Одновременно создастся файл hashes.txt, в котором будут храниться номера и хэши всех элементов
# 2. Образец элемента, который нужно найти
# Программа находит на изображении с образцом нужный элемент,
# создает его хэш,
# ищет его среди сохраненных хэшей в файле hashes.txt
# Если находит, то открывает изображение этого элемента из папки elem
# Если нет, то выводит сообщение об ошибке

import cv2
import numpy as np
import json


def get_all_elements(image):
    """ Принимает изображение типа Image
     возвращает массив координат и размеров всех элементов на изображении
     в виде: [[x, y, w, h], ...] (x, y - координаты верхнего левого угла, w, h - ширина и высота)"""

    # Применяем Canny алгоритм для поиска границ
    edges = cv2.Canny(image, 100, 200)

    # Применяем морфологическую операцию закрытия
    kernel = np.ones((7, 7), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Ищем контуры и проходим по ним
    contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    out = []  # Массив для хранения координат и размеров всех элементов на изображении

    for cnt in contours:
        # Находим прямоугольник
        x, y, w, h = cv2.boundingRect(cnt)
        out.append([x, y, x + w, y + h])

    return out


# Загрузка изображения 1
# Если имя задано, то с изображения будут считаны все элементы и помещены
# в массив папку elem с именами segment_0.png, segment_1.png, ...
# А их хэши будут помещены в файл hashes.txt
image_name = 'screenshot.png'

# Загрузка изображения 2
# Это образец, который должен содержать 1 элемент для поиска в папке elem
sample_name = 'sample2.png'


# Если файл существует, то считываем из него хэши в словарь, где ключ - номер элемента, значение - хэш
try:
    with open('hashes.txt') as f:
        hashes = json.load(f)
        hashes = {int(k): v for k, v in hashes.items()}
except:
    hashes = {}

if image_name:
    image = cv2.imread(image_name)
    elements_for_save = get_all_elements(image)
    # По списку хэшей находим максимальный номер элемента, следующий будет новым
    num = max(hashes.keys()) if hashes else 0
    num += 1
    for i, elem in enumerate(elements_for_save):

        x, y, w, h = elem
        segment = image[y:h, x:w]

        hash = cv2.img_hash.pHash(segment)  # Получаем хэш сегмента
        hash_string = np.array(hash).tobytes().hex()  # Преобразование хэша в шестнадцатеричную строку

        if hash_string not in hashes.values():
            # Если хэша нет в словаре, то добавляем его
            hashes[num] = hash_string  # Сохраняем хэш в словарь
            cv2.imwrite(f'elem/segment_{num}.png', segment)  # Сохраняем сегмент в папку elem
            num += 1

    # Пересохраняем словарь в файл
    with open('hashes.txt', 'w') as f:
        json.dump(hashes, f, indent=4, default=int)


# Загрузка образца
sample = cv2.imread(sample_name)
# Находим элементы на образце
sample_elements = get_all_elements(sample)  # Получаем список координат и размеров всех элементов на образце
print("Найдено элементов на образце: ", len(sample_elements))
# Находим координаты центра образца
x, y = sample.shape[1] // 2, sample.shape[0] // 2
# Находим, какому элементу принадлежат координаты центра (на каком был клик)
sample_element = [elem for elem in sample_elements if elem[0] < x < elem[2] and elem[1] < y < elem[3]]

if sample_element:
    # Если нашли элемент в центре образца, то считаем что на нем был клик мыши
    x, y, w, h = sample_element[0]
    sample_segment = sample[y:h, x:w]
    sample_hash = cv2.img_hash.pHash(sample_segment)  # Получаем хэш сегмента

    for num, hash_string in hashes.items():
        # Преобразование шестнадцатеричной строки хэша обратно в массив numpy
        elem_hash = np.frombuffer(bytes.fromhex(hash_string), dtype=np.uint8)
        if cv2.norm(sample_hash[0], elem_hash, cv2.NORM_HAMMING) < 10:
            # Если образец похож на элемент из словаря, то выводим его
            segment = cv2.imread(f'elem/segment_{num}.png')
            cv2.imshow('Segment', segment)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
else:
    # Если не нашли, то выводим сообщение об ошибке
    print('Элемент в центре не найден')

