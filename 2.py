import cv2
import numpy as np
from sklearn.cluster import KMeans

# Загрузка изображения
image = cv2.imread('screenshot4.png')

# Преобразование изображения в массив данных
data = image.reshape((-1, 3))

# Создание и обучение модели k-средних
kmeans = KMeans(n_clusters=3)
kmeans.fit(data)

# Предсказание меток для каждого пикселя
labels = kmeans.predict(data)

# Создание нового изображения с использованием меток
new_image = kmeans.cluster_centers_[labels].reshape(image.shape).astype(np.uint8)

# Отображение результата
cv2.imshow('Result', new_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
