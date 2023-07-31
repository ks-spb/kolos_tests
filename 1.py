import cv2
import numpy as np
import pyautogui
from time import time, sleep

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
image = screenshot()



# Применяем Canny алгоритм для поиска границ
edges = cv2.Canny(image, 100, 200)

# Ищем контуры и проходим по ним
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    # Обводим контур прямоугольником
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Вырезаем найденную область из исходного изображения
    roi = image[y:y + h, x:x + w]

    # Сохраняем полученный фрагмент скриншота в отдельный файл
    cv2.imwrite('segment_' + str(y) + '.png', roi)

# Выводим конечное изображение
cv2.imshow('Result', image)
cv2.waitKey(0)