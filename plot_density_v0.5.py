import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

def clean_and_convert_float(number_str):
    """Convert a comma-separated float string to a float."""
    return float(number_str.replace(',', '.'))

def process_data(file_paths, density_threshold=0.5):
    densities = {}
    num_lines_above_threshold = 0
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
                        densities[evacuation_time] = max(densities[evacuation_time], density)
                        if density > density_threshold:
                            num_lines_above_threshold += 1
                            if first_crossing_time is None:
                                first_crossing_time = evacuation_time
                            last_crossing_time = evacuation_time

    # Calculate the time duration if both first and last times are available
    time_duration = last_crossing_time - first_crossing_time if first_crossing_time is not None and last_crossing_time is not None else 1  # Prevent division by zero

    # Calculate normalized integral result
    integral_result = (num_lines_above_threshold * 0.25) / time_duration

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
    plt.title(f'График плотности людского потока\nВремя существования скоплений: {integral_result:.1f} сек')
    plt.grid(True)
    plt.legend()

    # Annotate the Integral Result on the graph
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
        print(f"Время существования скоплений при плотности >= {density_threshold}: {round(integral_result, 1)} сек")   # Normalized Integral Result of Density
        plot_densities(densities, density_threshold, round(integral_result, 1))
    else:
        print("Файлы не выбраны.")

if __name__ == "__main__":
    open_file_dialog()
