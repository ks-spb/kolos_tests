import cv2
import numpy as np
import pyautogui
from time import time, sleep
import imagehash
from PIL import Image

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

# Загружаем изображение
# image = screenshot()
# Загрузка изображения
image = cv2.imread('screenshot_cut.png')

# Применяем Canny алгоритм для поиска границ
edges = cv2.Canny(image, 100, 200)

# Применяем морфологическую операцию закрытия
kernel = np.ones((7,7),np.uint8)
closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

# Ищем контуры и проходим по ним
contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Создание объекта AverageHash
average_hash = cv2.img_hash.AverageHash_create()
hashes = []


for i, cnt in enumerate(contours):
    # Обводим контур прямоугольником
    x, y, w, h = cv2.boundingRect(cnt)


    # Вырезаем найденную область из исходного изображения
    roi = image[y:y + h, x:x + w]
    roi_image = Image.fromarray(roi)
    # Сохраняем полученный фрагмент скриншота в отдельный файл
    cv2.imwrite('elem/segment_' + str(i) + '.png', roi)

    # Вычисление хэша изображения с помощью cv2
    hash = average_hash.compute(roi)
    # Получение хэша в виде строки
    hash = np.array(hash).tobytes().hex()

    if hash in hashes:
        print('          hash in hashes' + str(i))
    hashes.append(hash)

    print(i, hash)

    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# -----------------------------------------------------------
#     # Вычисление хэша изображения с помощью алгоритма average_hash
#     hash = imagehash.average_hash(roi_image)
#     # hash = imagehash.average_hash(Image.open('image1.png'))
#     if hash in hashes:
#         print('          hash in hashes' + str(i))
#     hashes.append(hash)
#
#     print(i, hash)
    # # Сравнение хэшей двух изображений
    # otherhash = imagehash.average_hash(Image.open('image2.png'))
    # print(hash == otherhash)  # Выводит True, если изображения похожи, иначе False
    #
    # # Вычисление расстояния Хэмминга между двумя хэшами
    # print(hash - otherhash)  # Выводит расстояние Хэмминга между двумя хэшами
# -----------------------------------------------------------

# Выводим конечное изображение
cv2.imshow('Result', image)
cv2.imwrite('sample1' + '.png', image)
cv2.waitKey(0)
