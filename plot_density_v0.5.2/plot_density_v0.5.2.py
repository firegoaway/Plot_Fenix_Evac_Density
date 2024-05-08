import matplotlib
matplotlib.use('TkAgg')
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
            delta = time - evac_times[-1][0] if evac_times[0][1] >= density_threshold else 0.2 # Тут к конечной сумме total_delta_sum прибавляется лишнее значение 0.2. Оригинал: "delta = time - evac_times[-1][0] if evac_times[-1][1] >= density_threshold else 0.2". В оригинале delta почему-то принимает отрицательное значение.
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
    
    print(f"tск* - Время существования всех скоплений на временном отрезке [{first_time_exceeded} ; {last_time_exceeded}] сек, \nгде плотность потока, состоящего хотя бы из 2 человек, превышает {density_threshold} (м2/м2): {total_delta_sum:.1f} сек.")
    
    return evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded

def plot_densities(evac_times, density_threshold, total_delta_sum, first_time_exceeded, last_time_exceeded):
    times, densities = zip(*evac_times)
    plt.figure()
    plt.plot(times, densities, drawstyle="steps-post", linewidth=1, color="#00FF00ff",
             marker='o', markersize=1, markeredgewidth=1, markerfacecolor="#1f77b4ff", markeredgecolor="#1f77b4ff")
    plt.axhline(density_threshold, color="red", linestyle="--", lw=2, label=f'Критическая плотность >= {density_threshold} (м2/м2)')
    plt.fill_between(times, densities, density_threshold,
                     where=[d > density_threshold for d in densities],
                     color='red', alpha=0.3, label='Зона критической плотности')
    plt.xlabel('Время (сек)')
    plt.ylabel('Плотность (м2/м2)')
    plt.title(f'График плотности людского потока\nВремя существования скоплений (tск*): {total_delta_sum:.1f} сек')
    plt.grid(True)
    plt.legend()
    plt.show()

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Выберите файлы с результатами формата peoples_detailed_nnnnnn_n.tsv",
                                             filetypes=[("TSV files", "*.tsv")])
    density_threshold = 0.5
    if file_paths:
        evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded = process_data(file_paths, density_threshold)
        plot_densities(evac_times, density_threshold, total_delta_sum, first_time_exceeded, last_time_exceeded)
    else:
        print("Файлы не выбраны.")

if __name__ == "__main__":
    open_file_dialog()
