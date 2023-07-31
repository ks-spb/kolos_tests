import cv2
import numpy as np

# Загрузка изображения
img = cv2.imread('screen.png')

# Преобразование в оттенки серого
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Бинаризация изображения
ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Поиск контуров
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Объединение вложенных и внешних контуров
for i in range(len(contours)):
    if hierarchy[0][i][3] == -1:
        cv2.drawContours(mask, [contours[i]], -1, (255, 255, 255), -1)
    else:
        cv2.drawContours(mask, [contours[hierarchy[0][i][3]]], -1, (255, 255, 255), -1)

# Поиск контуров на объединенной маске
gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
contours, hierarchy = cv2.findContours(gray_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Объединение контуров букв в слова
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)

    # Проверка размера для фильтрации шума
    if w > 30 and h > 30:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Вывод результата
cv2.imshow('Result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()