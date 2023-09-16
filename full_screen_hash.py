# Создается объект tkinter без окна
# Программа ожидает нажатия клавиши ctrl и делает скриншот с помощью mss
# Скриншот сохраняется в папку full_screen в формате png с именем scr_1.png, scr_2.png, ...
# В файл full_screen.txt записывается номер скриншота и его хэш
import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mss
import mss.tools
import cv2
import numpy as np
import keyboard
import os


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
        self.scr_counter = 0
        try:
            with open('full_screen/full_screen.txt', 'r') as file:
                self.screens = json.load(file)
                self.scr_counter = len(self.screens)
        except FileNotFoundError:
            self.screens = {}

    def get_free_name(self):
        """ Возвращает имя для нового скриншота """
        self.scr_counter += 1
        return f'full_screen/scr_{self.scr_counter}.png'

    def get_hash(self):
        """ Возвращает хэш текущего скриншота """
        img = screenshot()
        hash = cv2.img_hash.pHash(img)
        hash_string = np.array(hash).tobytes().hex()
        return hash_string

    def make_and_save_screenshot(self):
        """ Делает, сохраняет скриншот в файл и добавляет его в словарь """
        img = screenshot()  # Делаем скриншот
        name = self.get_free_name()
        hash = cv2.img_hash.pHash(img)
        hash_string = np.array(hash).tobytes().hex()
        cv2.imwrite(name, img)
        self.screens[self.scr_counter] = hash_string
        with open('full_screen/full_screen.txt', 'w') as file:
            json.dump(self.screens, file, indent=4, default=int)
        return name

    def search_screenshots(self, hash_string):
        """ Ищет скриншоты используя алгоритм сравнения хэшей """
        hash1 = np.frombuffer(bytes.fromhex(hash_string), dtype=np.uint8)
        cast = []
        for num, hash_string in self.screens.items():
            hash2 = np.frombuffer(bytes.fromhex(hash_string), dtype=np.uint8)
            if cv2.norm(hash1, hash2, cv2.NORM_HAMMING) < 12:
                cast.append(f'full_screen/scr_{num}.png')
                print(f'Найден скриншот: scr_{num}.png')
        return cast


def on_ctrl_press(event):
    """ Обработчик нажатия клавиши ctrl """
    print('Нажата клавиша ctrl')
    name = scr_manager.make_and_save_screenshot()  # Сохраняем скриншот
    view_screenshots([name], "Новый скриншот")  # Выводим его в окне tkinter


def on_shift_press(event):
    """ Обработчик нажатия клавиши shift """
    hash = scr_manager.get_hash()  # Получаем хэш текущего скриншота
    # Ищем скриншоты с близкими хэшами
    cast = scr_manager.search_screenshots(hash)
    if cast:
        # Если нашли, то выводим их в окне tkinter
        view_screenshots(cast, "Найденные скриншоты")
    else:
        # Если не нашли, то выводим сообщение
        messagebox.showinfo("Скриншоты", "Скриншоты не найдены")


def view_screenshots(cast, name):
    """ Принимает список имен файлов скриншотов и выводит их в окне tkinter
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

    view.wait_window()


root = tk.Tk()
root.withdraw()

keyboard.on_press_key('ctrl', on_ctrl_press)  # Прослушиваем нажатие клавиши ctrl
keyboard.on_press_key('shift', on_shift_press)  # Прослушиваем нажатие клавиши shift
keyboard.on_press_key('esc', lambda x: root.destroy())  # Прослушиваем нажатие клавиши esc для выхода

keyboard.hook(lambda x: None)

# Создаем объект для сохранения скриншотов
scr_manager = ScreenShoManager()

root.mainloop()


