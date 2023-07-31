import cv2
import numpy as np
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries

# Загрузить изображение
img = cv2.imread('image.jpg')

# Разбить на сегменты
segments = slic(img, n_segments=100, compactness=10)

# Для каждого сегмента найти фон
bg_colors = []
for i in np.unique(segments):
    mask = segments == i
    hist = cv2.calcHist([img], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    bg_color = np.argmax(hist)
    bg_colors.append(bg_color)

# Сгруппировать похожие фоны в кластеры    
clusters = kmeans(bg_colors, 5)

# Присвоить каждому сегменту номер кластера
segment_clusters = []
for bg_color in bg_colors:
    cluster = clusters[bg_color]
    segment_clusters.append(cluster)

# Размыть границы    
blurred = blur_boundaries(img, segments, sigma=3)

# Вывести результат
cv2.imshow('Result', blurred)
cv2.waitKey(0)