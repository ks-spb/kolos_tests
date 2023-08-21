import cv2
import numpy as np

# Загрузка изображения
image = cv2.imread('screenshot.png')

# Преобразование в оттенки серого
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Применение Canny
edges = cv2.Canny(gray, 50, 150)

# Поиск контуров
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
  # Обрабатываем только внешние контуры
  x,y,w,h = cv2.boundingRect(cnt)
  cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)

# Вывод результата
cv2.imshow('Result', image)
cv2.waitKey(0)
cv2.destroyAllWindows()