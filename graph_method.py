# Черно-белая сегментация изображения
import cv2
import numpy as np

# Загрузка изображения
img = cv2.imread('screenshot4.png')

# Преобразование в оттенки серого
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Бинаризация
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

cv2.imshow('Segments', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
exit()
# Поиск контуров
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Инициализация черным цветом
segments = np.zeros(img.shape, dtype=np.uint8) + 255

# Сегментация и выделение контуров
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(segments, (x, y), (x + w, y + h), (255, 255, 255), -1)

cv2.imshow('Segments', segments)
cv2.waitKey(0)
cv2.destroyAllWindows()