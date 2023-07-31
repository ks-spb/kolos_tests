import cv2
import numpy as np

# Загрузка изображения
image = cv2.imread('screen.png')

# Преобразование изображения в оттенки серого
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Применение порогового фильтра для выделения объектов
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Нахождение контуров
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Объединение наложенных и внутренних контуров
for i in range(len(contours)):
    for j in range(i + 1, len(contours)):
        if len(contours[i]) > 0 and cv2.pointPolygonTest(contours[j], tuple(contours[i][0][0]), False) >= 0:
            contours[i] = np.concatenate((contours[i], contours[j]))
            contours[j] = np.array([])

# Удаление пустых контуров
contours = [c for c in contours if len(c) > 0]

# Объединение рядом стоящих контуров
for i in range(len(contours)):
    for j in range(i + 1, len(contours)):
        x1, y1, w1, h1 = cv2.boundingRect(contours[i])
        x2, y2, w2, h2 = cv2.boundingRect(contours[j])
        if abs(x1 - x2) <= 10 and abs(y1 - y2) <= 10:
            contours[i] = np.concatenate((contours[i], contours[j]))
            contours[j] = np.array([])

# Удаление пустых контуров
contours = [c for c in contours if len(c) > 0]

# Рисование рамок вокруг объектов
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Вывод результата
cv2.imshow('Result', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
