import os
import matplotlib
matplotlib.use('Agg')  # Используем 'Agg' чтобы не отображался GUI
import matplotlib.pyplot as plt

import csv
import tkinter as tk
from tkinter import filedialog

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
    for time, max_density in evac_times:
        if max_density >= density_threshold:
            if first_time_exceeded is None:
                first_time_exceeded = time
            last_time_exceeded = time
            delta = time - evac_times[-1][0] if evac_times[0][1] >= density_threshold else 0.2
        else:
            delta = 0
        deltas.append(delta)
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
                    time = parse_evac_time(first_cell)
                    evac_times.append((time, current_max_density))
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
    root.title("PFED v0.6.0")
    root.iconbitmap('.gitpics\\pfed.ico')
    root.wm_iconbitmap('.gitpics\\pfed.ico')
    # root.withdraw() # Используется для скрытия окна программы
    file_paths = filedialog.askopenfilenames(title="Выберите файлы с результатами формата peoples_detailed_nnnnnn_n.tsv",
                                             filetypes=[("Файлы формата TSV", "*.tsv")])
    density_threshold = 0.5
    if file_paths:
        for file_path in file_paths:
            evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded = process_data([file_path], density_threshold)

            # Определяем маршрут сохранения
            folder_path = os.path.dirname(file_path)
            # Берем имя второй папки после папки расположения файлов ".tsv"
            second_folder_name = os.path.split(os.path.split(folder_path)[0])[-1]  
            save_folder = os.path.abspath(os.path.join(folder_path, '..', '..', '..'))
            file_name = os.path.basename(file_path).replace('.tsv', f'_{second_folder_name}.png')  # Используем имя второй папки
            save_path = os.path.join(save_folder, file_name)
            
            addToClipBoard(second_folder_name)

            plot_densities(evac_times, density_threshold, total_delta_sum, first_time_exceeded, last_time_exceeded, save_path)
            print(f"Графики сохранены по адресу: {save_path}")
    else:
        print("Файлы не выбраны.")

if __name__ == "__main__":
    open_file_dialog()