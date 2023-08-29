# Программа демонстрирует работу сбора элементов экрана в фоновом режиме
# Для этого создается новый процесс (программа работает на отдельном ядре процессора)
# При работе программа регистрирует изменения экрана и на каждом новом экране
# производит поиск элементов, после чего записывает их в очередь.
# После окончания, нажатия клавиши Пробел, останавливается фоновый процесс,
# а в основном процессе сохраняются изображения экранов с отмеченными элементами.
# Сохранение экранов сделано для наглядности, программа собирает информацию о каждом значке
# его хэш, положение на экране и размер.

import mss
import mss.tools
import cv2
from multiprocessing import Process, Queue, Manager
from threading import Thread
import time
import numpy as np
import keyboard


def screen_monitor(queue_img):
    """ Запускает поток, который делает скриншоты с заданной периодичностью
    и сообщает если экран изменился. """
    sct = mss.mss()
    monitor = {'top': 0, 'left': 0, 'width': sct.monitors[0]['width'], 'height': sct.monitors[0]['height']}
    hash_base_img = None  # Получаем хэш сегмента

    while True:
        scr_img = sct.grab(monitor)  # Делаем скриншот
        img = np.asarray(scr_img)  # Записываем его в np
        hash_img = cv2.img_hash.pHash(img)  # Получаем хэш сегмента

        if hash_base_img is None or (cv2.norm(hash_base_img[0], hash_img[0], cv2.NORM_HAMMING) > 12):
            # Изображения разные
            hash_base_img = hash_img  # Сохраняем новый хэш
            # cv2.imwrite(f'{hash_img}.png', img)
            queue_img.put(img)  # Передаем скриншот в очередь

        time.sleep(0.3)  # Пауза


def process_changes(queue_hashes, queue_img):
    """ Запускает поток, который делает скриншоты с заданной
        периодичностью и сообщает если экран изменился.
        При каждом обновлении экрана очищает выходной список и начинает заполнять его снова
        разбирая полученный скриншот. """
    # Запускаем поток для мониторинга
    thread = Thread(target=screen_monitor, args=(queue_img,))
    thread.start()
    hashes_elements = {}

    while True:

        if not queue_img.empty():
            # Измеряем время выполнения
            start_time = time.time()

            # Получен новый скриншот, выберем из него элементы
            screenshot = queue_img.get()  # Получаем скриншот из очереди
            print('Экран изменился ---------------------------------- ')
            # Принимает изображение типа Image
            # возвращает итератор координат и размеров всех элементов на изображении
            # в виде: [[x, y, w, h], ...] (x, y - координаты верхнего левого угла, w, h - ширина и высота)

            # Применяем Canny алгоритм для поиска границ
            edges = cv2.Canny(screenshot, 100, 200)

            # Применяем морфологическую операцию закрытия
            kernel = np.ones((7, 7), np.uint8)
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            # Ищем контуры и проходим по ним
            contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            hashes_elements.clear()

            for cnt in contours:
                # Находим прямоугольник
                x, y, w, h = cv2.boundingRect(cnt)
                w, h = x + w, y + h
                segment = screenshot[y:h, x:w]

                hash = cv2.img_hash.pHash(segment)  # Получаем хэш сегмента
                hash_string = np.array(hash).tobytes().hex()  # Преобразование хэша в шестнадцатеричную строку

                if hash_string not in hashes_elements.keys():
                    # Если хэша нет в списке, то добавляем его
                    hashes_elements[hash_string] = [x, y, w, h]

                if not queue_img.empty():
                    # Если за время обработки скриншота экран снова изменится
                    # начинаем заново
                    break
            else:
                # Если скриншот обработан, то передаем список хэшей в очередь
                queue_hashes.put((screenshot, hashes_elements))
                print('Обработано экранов ', queue_hashes.qsize())
                print(f'Количество элементов последнего экрана: {len(hashes_elements)}')
                print(f'Список хэшей последнего экрана: {hashes_elements}')
                # Выводим время выполнения
                print(f'Время выполнения: {time.time() - start_time + 0.05} сек.')


flag_new_screen = False  # Флаг, который сообщает о том, что экран (False) не изменился
if __name__ == "__main__":
    with Manager() as manager:
        queue_hashes = manager.Queue()  # Очередь для передачи списка хэшей элементов
        queue_img = Queue()  # Очередь для передачи скриншота в np

        # Запуск процессов
        p1 = Process(target=process_changes, args=(queue_hashes, queue_img,))
        p1.start()

        print('Начало работы')
        while True:
            if keyboard.is_pressed('space'):
                break
        out = []
        print('Выход из программы')
        print('Получено экранов: ', queue_hashes.qsize())
        while not queue_hashes.empty():
            out.append(queue_hashes.get())

        for i, (img, ret) in enumerate(out):
            for key, value in ret.items():
                cv2.rectangle(img, (value[0], value[1]), (value[2], value[3]), (0, 0, 255), 2)
            cv2.imwrite(f'{str(i)}.jpg', img)
        p1.terminate()
