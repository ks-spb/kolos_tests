import cv2
import numpy as np

# Загрузка изображения
image = cv2.imread('screenshot.png')

# Преобразование изображения в оттенки серого
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Применение порогового значения
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Применение морфологических операций
kernel = np.ones((3,3), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
sure_bg = cv2.dilate(opening, kernel, iterations=3)

# Нахождение областей переднего плана
dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)

# Нахождение неизвестных областей
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)

# Маркировка областей
_, markers = cv2.connectedComponents(sure_fg)
markers = markers + 1
markers[unknown == 255] = 0

# Применение алгоритма водораздела
markers = cv2.watershed(image, markers)
image[markers == -1] = [255, 0, 0]

# Отображение результата
cv2.imshow('Result', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
