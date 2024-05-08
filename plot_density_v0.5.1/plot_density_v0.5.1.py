import matplotlib.pyplot as plt
import tkinter as tk

from tkinter import filedialog

import numpy as np
import sympy as sp
import math
import scipy.integrate as spi

from scipy.integrate import quad
from sympy import symbols, integrate

def clean_and_convert_float(number_str):
    """Convert a comma-separated float string to a float."""
    return float(number_str.replace(',', '.'))

def process_data(file_paths, density_threshold=0.5):
    densities = {}
    num_lines_above_threshold = 0
    num_lines_below_threshold = 0
    first_crossing_time = None
    last_crossing_time = None

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            evacuation_time = None
            for line in file:
                if "EvacuationTime" in line:
                    parts = line.split(':')
                    evacuation_time = clean_and_convert_float(parts[1].split()[0])
                    if evacuation_time not in densities:
                        densities[evacuation_time] = 0
                elif "Человек" in line and evacuation_time is not None:
                    parts = line.split('\t')
                    if len(parts) >= 5:
                        density = clean_and_convert_float(parts[4])
                        # print(f"{density}") # Чекаем правильность парсинга
                        densities[evacuation_time] = max(densities[evacuation_time], density)
                        if density < density_threshold:
                            num_lines_below_threshold += 1
                        if density >= density_threshold:
                            num_lines_above_threshold += 1
                            if first_crossing_time is None:
                                first_crossing_time = evacuation_time
                            last_crossing_time = evacuation_time

    # Чересстрочный (criss-cross) расчёт первого и последнего времени, если найдены
    # time_duration = last_crossing_time - first_crossing_time if first_crossing_time is not None and last_crossing_time is not None else 1  # Избегаем деления на ноль
    
    # Определяем подынтегральное выражение и его переменные
    num_lines = abs(num_lines_below_threshold - num_lines_above_threshold)
    time_intermediate = (last_crossing_time - first_crossing_time) / 2
    x = symbols('x')
    integral_expression = abs((x + math.log(num_lines_below_threshold)) / (x + math.log(num_lines_above_threshold)))
    
    # Временный вычислителью Шаг = 
    integral_result = integrate(integral_expression, (x, first_crossing_time, last_crossing_time))
    print(f"Разность числа строк, содержащих информацию о плотности: {num_lines_below_threshold} - {num_lines_above_threshold} = {num_lines} ; \nПодынтегральное выражение:{integral_expression} ;\nРезультат ингтегрирования: {integral_result} сек")
    print(f"tск* - Время существования всех скоплений на отрезке [{first_crossing_time} ; {last_crossing_time}] при плотности >= {density_threshold} (м2/м2): {round(integral_result, 1)} сек")   # Выводим значение в консоль для дебага
    # Вычисляем нормализацию (определённый интеграл)
    # integral_result = (num_lines_above_threshold * 0.25) / time_duration

    return densities, integral_result

def plot_densities(densities, density_threshold, integral_result):
    times = sorted(densities.keys())
    max_density_values = [densities[time] for time in times]

    plt.figure()
    plt.plot(times, max_density_values, drawstyle="steps-post", linewidth=1, color="#00FF00ff",
             marker='o', markersize=1, markeredgewidth=1, markerfacecolor="#1f77b4ff", markeredgecolor="#1f77b4ff") # plt.plot(times, max_density_values, marker='o')
    
    plt.axhline(density_threshold, color="red", linestyle="--", lw=2, label=f'Критическая плотность >= {density_threshold} (м2/м2)')
    plt.fill_between(times, max_density_values, density_threshold, 
                     where=[d > density_threshold for d in max_density_values],
                     color='red', alpha=0.3, label='Зона критической плотности')
    
    plt.xlabel('Время (сек)')
    plt.ylabel('Плотность (м2/м2)')
    plt.title(f'График плотности людского потока\nВремя существования скоплений (tск*): {integral_result:.1f} сек')
    plt.grid(True)
    plt.legend()

    # Аннотация на графике (неудобно накладывается поверх графика)
    #plt.annotate(f'Время существования скоплений: {integral_result:.1f} сек', xy=(0.01, 0.01), xycoords='axes fraction', 
    #            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="b", lw=2), fontsize=8)

    plt.show()

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Выберите файлы с результатами формата peoples_detailed_nnnnnn_n.tsv", filetypes=[("TSV files", "*.tsv")])
    density_threshold = 0.5
    if file_paths:
        densities, integral_result = process_data(file_paths, density_threshold)
        plot_densities(densities, density_threshold, round(integral_result, 1))
    else:
        print("Файлы не выбраны.")

if __name__ == "__main__":
    open_file_dialog()
