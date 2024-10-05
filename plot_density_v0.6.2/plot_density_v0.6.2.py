import os
import matplotlib
matplotlib.use('TkAgg')  # Используем 'Agg' чтобы не отображался GUI
import matplotlib.pyplot as plt

import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import StringVar
from tkinter import Tk, Toplevel, Button, Label
from tkinter import mainloop

import numpy as np
import sympy as sp
from sympy import symbols, integrate
import math
import scipy.integrate as spi
from scipy.integrate import quad

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

def clean_and_convert_float(number_str):
    number_str = number_str.strip().split(' ')[0]
    return float(number_str.replace(',', '.'))

def parse_evac_time(line):
    return clean_and_convert_float(line.split(':')[1])

def compute_deltas(evac_times, density_threshold):
    deltas = []
    first_time_exceeded = None
    last_time_exceeded = None
    
    previous_time = None

    for index, (time, max_density) in enumerate(evac_times):
        if max_density >= density_threshold:
            if first_time_exceeded is None:
                first_time_exceeded = time
            
            last_time_exceeded = time

            if previous_time is not None:
                delta = time - previous_time
            else:
                delta = 0.2  # Значение по умолчанию до того, как встретится первая дельта
            
            deltas.append(delta)
        else:
            # Если Density меньше threshold, принимаем 0
            deltas.append(0)
        
        previous_time = time  # Обновляем значение previous_time перед следующей итерацией

    return sum(deltas), first_time_exceeded, last_time_exceeded

def process_data(file_paths, density_threshold=0.5):
    evac_times = []
    current_max_density = 0.0
    time = None

    for file_path in file_paths:
        with open(file_path, newline='', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter='\t')
            first_line = True

            for row in reader:
                if not row or first_line:
                    first_line = False
                    continue
                first_cell = row[0]
                if 'EvacuationTime' in first_cell:
                    if time is not None:
                        evac_times.append((time, current_max_density))
                    time = parse_evac_time(first_cell)
                    current_max_density = 0
                elif len(row) > 4 and row[4] != 'Density':
                    try:
                        density = clean_and_convert_float(row[4])
                        if density > current_max_density:
                            current_max_density = density
                    except ValueError:
                        pass

            if current_max_density > 0 and time is not None:
                evac_times.append((time, current_max_density))

    total_delta_sum, first_time_exceeded, last_time_exceeded = compute_deltas(evac_times, density_threshold)
    
    print(f"tск* - Время существования всех скоплений на временном отрезке [{first_time_exceeded} ; {last_time_exceeded}] сек, \nгде плотность потока, состоящего хотя бы из 2 человек, превышает {density_threshold} ($м2/м2$): {total_delta_sum:.1f} сек.")
    
    return evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded

def plot_densities(evac_times, density_threshold, total_delta_sum, first_time_exceeded, last_time_exceeded, save_path):
    times, densities = zip(*evac_times)
    plt.figure(figsize=(12,4))
    plt.plot(times, densities, drawstyle="steps-post", linewidth=1, color="#00FF00ff",
             marker='o', markersize=1, markeredgewidth=1, markerfacecolor="#1f77b4ff", markeredgecolor="#1f77b4ff")
    plt.axhline(density_threshold, color="red", linestyle="--", lw=2, label=f'Критическая плотность >= {density_threshold} ($м^2/м^2$)')
    plt.fill_between(times, densities, density_threshold,
                     where=[d > density_threshold for d in densities],
                     color='red', alpha=0.3, label='Зона критической плотности')
    plt.xlabel('Время (сек)')
    plt.ylabel('Плотность ($м^2/м^2$)')
    plt.title(f'График плотности людского потока\nВремя существования скоплений (tск*): {total_delta_sum:.1f} сек', fontsize=12)
    plt.grid(True)
    plt.legend()
    
    # Сохраняем, GUI не показываем
    plt.savefig(save_path, bbox_inches='tight', format='png')  # Сохраняем в качестве PNG
    plt.close()  # Закрываем инстанс, освобождаем память

def open_file_dialog():
    root = tk.Tk()
    
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'pfed.ico')
    
    root.title("PFED v0.6.2")
    root.iconbitmap(icon_path)
    root.wm_iconbitmap(icon_path)
    # root.withdraw() # Используется для скрытия окна программы
    file_paths = filedialog.askopenfilenames(title="Выберите файлы с результатами формата peoples_detailed_nnnnnn_n.tsv",
                                             filetypes=[("Файлы формата TSV", "*.tsv")])
    density_threshold = 0.5
    if file_paths:
        for file_path in file_paths:
            evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded = process_data([file_path], density_threshold)

            folder_path = os.path.dirname(file_path) # Определяем маршрут сохранения
            second_folder_name = os.path.split(os.path.split(folder_path)[0])[-1] # Берем имя второй папки после папки расположения файлов ".tsv"
            save_folder = os.path.abspath(os.path.join(folder_path, '..', '..', '..'))
            file_name = os.path.basename(file_path).replace('.tsv', f'_{second_folder_name}.png')  # Используем имя второй папки
            save_path = os.path.join(save_folder, file_name)
            
            addToClipBoard(second_folder_name)

            plot_densities(evac_times, density_threshold, total_delta_sum, first_time_exceeded, last_time_exceeded, save_path)
            print(f"Графики сохранены по адресу: {save_path}")
    else:
        print("Файлы не выбраны.")
    
    def OpenPNG():
        os.startfile(save_path)

    def OpenPNGfolder():
        os.startfile(save_folder)

    def Close():
        root.quit()  # Закрываем основное окно tkinter

    custom_message_box(OpenPNG, OpenPNGfolder, Close)

def custom_message_box(callback_open_png, callback_open_folder, callback_close):
    def on_open_png():
        callback_open_png()
        #top.destroy()
    
    def on_open_folder():
        callback_open_folder()
        #top.destroy()
    
    def on_close():
        callback_close()
        top.destroy()

    top = Toplevel()
    top.title("PFED v0.6.2")
    top.geometry("400x100")
    
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'pfed.ico')
    
    top.iconbitmap(icon_path)
    top.wm_iconbitmap(icon_path)
    
    top.overrideredirect(False)  # Скрываем стандартную рамку

    label = Label(top, text="Выберите действие", padx=10, pady=10)
    label.pack(pady=(10, 0))
    
    button_frame = ttk.Frame(top)
    button_frame.pack(pady=10)
    
    Button(button_frame, text="Показать графики", command=on_open_png).pack(side='left', padx=5)
    Button(button_frame, text="Открыть папку с графиками", command=on_open_folder).pack(side='left', padx=5)
    Button(button_frame, text="Выйти", command=on_close).pack(side='left', padx=5)
    
    top.update_idletasks()
    width = top.winfo_width()
    height = top.winfo_height()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'{width}x{height}+{x}+{y}')

    top.transient()  # Поверх других окон
    top.grab_set()  # Модальное окно
    top.protocol("WM_DELETE_WINDOW", on_close)  # Закрытие окна

if __name__ == "__main__":
    open_file_dialog()
    mainloop()