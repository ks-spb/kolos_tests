# Функция создаёт скриншот, уменьшает качество, ищет схожее состояние, если не находит - записывает новое

import pyautogui
import os, sys
import numpy as np
import cv2
from cv2 import img_hash
from time import time, sleep

# Задаем уровень качества (чем меньше число, тем ниже качество)
quality = 1  # Можете выбрать значение от 1 до 95

BASENAME = "elem"  # Префикс для имени файла при сохранении изображения элемента

PATH = input_file = os.path.join(sys.path[0], 'elements_img')  # Путь для сохранения изображений


def screenshot(x_reg: int = 0, y_reg: int = 0, region: int = 0):
    """ Скриншот заданного квадрата или всего экрана

    В качестве аргументов принимает координаты верхней левой точки квадрата и его стороны.
    Если сторона на задана (равна 0) - то делает скриншот всего экрана

    """
    sleep(2)
    if region:
        image = pyautogui.screenshot(region=(x_reg, y_reg, region, region))  # x, y, x+n, y+n (с верхнего левого угла)
    else:
        image = pyautogui.screenshot()
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


#Открытие изображение
image = screenshot()
# image = cv2.imread(os.path.join(PATH, 'sample.png'))

# Начинаем замер времени
start_time = time()

image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
img = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY)[1] # ensure binary

# Время перед получением компонентов
print("Время перед получением компонентов --- %s seconds ---" % (time() - start_time))

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img)

# Время перед
print("Время перед гистограммой --- %s seconds ---" % (time() - start_time))

# Делаем фон черным
# Строим гистограмму изображения
hist = cv2.calcHist([img], [0], None, [256], [0, 256])
# Определяем значение пикселя, которое соответствует наибольшему пику, это фон
background_color = np.argmax(hist)

if background_color != 0:
    # Инвертируем значения пикселей в изображении, чтобы фон был черным - 0
    img = cv2.bitwise_not(img)

# Вывод изображения в окне
cv2.imshow('image', img)
cv2.waitKey(0)

# Время после гистограммы
print("Время после гистограммы --- %s seconds ---" % (time() - start_time))

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img)

# Время после вырезания элементов
print("Время после вырезания элементов --- %s seconds ---" % (time() - start_time))

# создание массива для хранения изображений компонентов
components = []
quantity = 0  # Количество элементов
for i in range(1, num_labels):

    if stats[i, cv2.CC_STAT_AREA] < 130:
        continue

    # создание маски для текущего компонента
    mask = (labels == i).astype(np.uint8) * 255

    # нахождение bounding box текущего компонента
    x, y, w, h = cv2.boundingRect(mask)

    # вырезание объекта по полученным координатам
    crop = img[y:y + h, x:x + w]


    components.append(crop)
    quantity += 1

    # Строим хэш aHash
    # hash = img_hash.PHash(crop)

    # Преобразуем хэш в HEX строку
    # hex_hash = ''.join([hex(h) for h in hash])


# Время перед печатью
print("Время перед печатью --- %s seconds ---" % (time() - start_time))
print(quantity)
for s in components:
    print(s)

    # Строим хэш aHash
    hash = img_hash.PHash(s)
    # извлекаем массив данных хэша
    # hash = hash.hash.flatten()

    # Вывод изображения в окне
    cv2.imshow('image', s)
    cv2.waitKey(0)

    print(hash)

# Время после печати
print("Время после печати --- %s seconds ---" % (time() - start_time))
print(quantity)