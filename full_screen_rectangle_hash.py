# Тест для сравнения экранов по набору элементов представленных прямоугольниками,
# параметры которых представлены округленными crc хэшами

# Создается объект tkinter без окна
# Программа ожидает нажатия клавиши ctrl и делает скриншот с помощью mss
# На экране находятся элементы (как в screen_monitoring.py), тут нас интересуют только их координаты и размеры
# По этим данным вычисляется хэши.
# Каждый хэш проверяется по БД, и если есть, извлекаются номера экранов, на которых он
# встречается. По частоте встречаемости находим экран или экраны с наибольшим совпадением.
# Новые хэши добавляются в БД с найденным номером.
# Если значение встречаемости ниже определенного порога, то экрану назначается новый номер, он добавляется к
# спискам хэшей которые на нем встречаются, а новые хэши добавляются в БД с номером этого экрана в списке,
# с тем же номером изображение сохраняется в папку full_screen.

# Если экран был добавлен программа сообщает об этом, если такой или похожие есть, они выводятся в окне.

import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mss
import mss.tools
import cv2
import numpy as np
import zlib
import time
import keyboard
import os


ACCEPT = 3  # Допустимое отклонение в координатах и размерах прямоугольников
COUNT_EL = 40  # Процент элементов на экране, которые должны совпадать, чтобы считать экран одинаковым


def screenshot():
    """ Делает скриншот и возвращает его в виде np массива """
    with mss.mss() as sct:
        monitor = {'top': 0, 'left': 0, 'width': sct.monitors[0]['width'], 'height': sct.monitors[0]['height']}
        scr_img = sct.grab(monitor)  # Делаем скриншот
        img = np.asarray(scr_img)  # Записываем его в np
        return img


class ScreenShoManager:
    """ Сохраняет экраны, хранит их номера и хэши в файл full_screen.txt """

    def __init__(self):
        # Проверяем наличие папки full_screen
        if not os.path.exists('full_screen'):
            os.mkdir('full_screen')
        # Файл для записи номера скриншота и его хэша хранит данные в json формате
        # Читаем его содержимое в словарь. Если файла нет создаем чистый словарь
        # Формат словаря: {crc_hash: set(номера экранов)}

        # Счетчик номеров экранов устанавливается по номеру последнего сохраненного экрана
        # Если файл не найден, то счетчик устанавливается в 0
        self.scr_counter = 0
        for file in os.listdir('full_screen'):
            if file.startswith('scr_'):
                num = int(file[4:-4])
                if num > self.scr_counter:
                    self.scr_counter = num

        try:
            with open('full_screen/full_screen.txt', 'r') as file:
                self.screens = json.load(file)
                # В файле set хранится как список, преобразуем его в set
                for key in self.screens:
                    self.screens[key] = set(self.screens[key])

        except FileNotFoundError:
            self.screens = {}

    def get_hashes_screen(self, screenshot):
        """ Принимает скриншот в формате np, находит на нем прямоугольные области описывающие элементы,
        получает crc хэши прямоугольников по x, y, w, h, возвращает их список """

        # Применяем Canny алгоритм для поиска границ
        edges = cv2.Canny(screenshot, 100, 200)

        # Применяем морфологическую операцию закрытия
        kernel = np.ones((7, 7), np.uint8)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Ищем контуры и проходим по ним
        contours, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        hash_list = []

        for cnt in contours:
            # Находим прямоугольник
            x, y, w, h = cv2.boundingRect(cnt)

            # Округляем координаты и размеры прямоугольника для получения допустимых отличий
            x_scaled = x // ACCEPT
            y_scaled = y // ACCEPT
            w_scaled = w // ACCEPT
            h_scaled = h // ACCEPT

            rect_str = str(x_scaled) + str(y_scaled) + str(w_scaled) + str(h_scaled)

            hash_bytes = zlib.crc32(rect_str.encode())
            hash_list.append(f"{hash_bytes:08x}")  # Добавляем хэш в список
        return hash_list

    def get_free_num(self):
        """ Возвращает номер нового экрана """
        self.scr_counter += 1
        return self.scr_counter


def on_ctrl_press(event):
    """ Обработчик нажатия клавиши ctrl """

    # Измеряем время выполнения
    start_time = time.time()

    img = screenshot()  # Делаем скриншот
    hashes_list = scr_manager.get_hashes_screen(img)  # Получаем список хэшей элементов

    # До этого момента мы не знаем, есть ли такой экран в БД и его номер, поэтому не можем дополнить ее.
    # Подсчитываем в какие экраны входят хэши из полученного набора и сколько раз
    # Если счетчик максимального экрана больше порога, то считаем что нашли экран
    # Если порог не превышен ни одним экраном, то добавляем новый экран
    is_screen = {}  # Словарь-счетчик, в какие экраны сколько раз входят хэши из полученного набора
                    # {номер экрана: количество вхождений}

    for hash_string in hashes_list:
        # Проверяем есть ли такой хэш в БД
        if hash_string in scr_manager.screens:
            # Если есть, то меняем счетчики
            for num in scr_manager.screens[hash_string]:
                if num not in is_screen:
                    is_screen[num] = 1
                else:
                    is_screen[num] += 1
        else:
            # Если нет, то добавляем новый хэш
            scr_manager.screens[hash_string] = set()

    # Находим номер экрана с максимальным счетчиком
    scr = 0
    if is_screen:
        scr = max(is_screen, key=is_screen.get)

    print(f'Время выполнения: {time.time() - start_time} сек.')

    if not scr or is_screen[scr]/(len(hashes_list)/100) < COUNT_EL:
        # Если счетчик максимального экрана меньше порога, то это новый экран
        scr = scr_manager.get_free_num()  # Получаем номер для нового экрана
        cv2.imwrite(f'full_screen/scr_{scr}.png', img)  # Сохраняем изображение в файл
        view_screenshots([scr], "Добавлен новый экран:")  # Выводим экран в окне tkinter
    else:
        view_screenshots([scr], "Открыт этот экран:")  # Выводим экран в окне tkinter

    # Тут номер экрана уже известен, добавляем номера экранов к хэшам
    screens_copy = {}
    for hash_string in hashes_list:
        scr_manager.screens[hash_string].add(scr)
        # Делаем копию словаря для записи в файл, где преобразуем set в список для записи в файл
        screens_copy[hash_string] = list(scr_manager.screens[hash_string])

    # Записываем словарь в файл
    with open('full_screen/full_screen.txt', 'w') as file:
        json.dump(screens_copy, file, indent=4)


def view_screenshots(cast, name):
    """ Принимает список номеров изображений и выводит их в окне tkinter
     в размере 50%. С возможностью прокрутки """

    # Создать окно от основного
    view = tk.Toplevel()
    view.title(name)
    view.geometry('800x600')

    # Создать канвас и полосу прокрутки
    canvas = tk.Canvas(view, width=800, height=600)
    scrollbar = tk.Scrollbar(view, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Упаковать виджеты
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Создать фрейм
    frame = tk.Frame(canvas)
    canvas.create_window((0,0), window=frame, anchor='nw')

    # Отобразить скриншоты
    image_dict = {}
    for name in cast:
        name = f'full_screen/scr_{name}.png'
        img = cv2.imread(name)
        img = cv2.resize(img, None, fx=0.5, fy=0.5)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = ImageTk.PhotoImage(Image.fromarray(img))
        image_dict[name] = image

        tk.Label(frame, image=image_dict[name]).pack(side=tk.TOP)
        tk.Label(frame, text=name).pack(side=tk.TOP)

    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.update()
    canvas.focus_set()

    view.grab_set()
    view.focus_set()
    view.wait_window()


root = tk.Tk()
root.withdraw()

keyboard.on_press_key('ctrl', on_ctrl_press)  # Прослушиваем нажатие клавиши ctrl
keyboard.on_press_key('esc', lambda x: root.destroy())  # Прослушиваем нажатие клавиши esc для выхода

keyboard.hook(lambda x: None)

# Создаем объект для сохранения скриншотов
scr_manager = ScreenShoManager()

root.mainloop()


