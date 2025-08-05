import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Button, Label, ttk, BooleanVar
import numpy as np
from math import log, log10

def custom_message_box(parent, callback_open_png, callback_open_folder, callback_close):
    def on_open_png():
        callback_open_png()

    def on_open_folder():
        callback_open_folder()

    def on_close():
        callback_close()
        top.destroy()

    top = Toplevel(parent)
    top.title("PFED v0.7.0")
    top.geometry("500x260")

    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
    icon_path = os.path.join(parent_directory, '.gitpics', 'pfed.ico')

    try:
        top.iconbitmap(icon_path)
        top.wm_iconbitmap(icon_path)
    except Exception as e:
        print(f"Внимание: Не удалось загрузить иконку для диалога: {e}")

    colors = {
        "primary": "#3498db",
        "secondary": "#2ecc71",
        "bg_light": "#f5f5f5",
        "text_dark": "#34495e",
        "success": "#27ae60",
    }

    style = ttk.Style()
    style.configure("Success.TLabel", font=("Segoe UI", 14, "bold"), foreground=colors["success"], background=colors["bg_light"])
    style.configure("Message.TLabel", font=("Segoe UI", 11), foreground=colors["text_dark"], background=colors["bg_light"])
    style.configure("PFED.TButton", font=("Segoe UI", 10, "bold"), padding=10)
    style.map("PFED.TButton",
              background=[("active", colors["secondary"]), ("!disabled", colors["primary"]), ("disabled", "#bdc3c7")],
              foreground=[("active", colors["text_dark"]), ("!disabled", colors["bg_light"]), ("disabled", "#7f8c8d")])

    top_frame = ttk.Frame(top, padding="20")
    top_frame.pack(fill=tk.BOTH, expand=True)

    success_icon = ttk.Label(top_frame, text="✓", font=("Segoe UI", 36, "bold"), foreground=colors["success"], background=colors["bg_light"])
    success_icon.pack(pady=(0, 5))

    label = ttk.Label(top_frame, text="Графики плотности построены!", style="Success.TLabel")
    label.pack(pady=(0, 15))

    message = ttk.Label(top_frame, text="Результаты сохранены. Выберите следующее действие:", style="Message.TLabel", wraplength=450)
    message.pack(pady=(0, 20))

    button_frame = ttk.Frame(top_frame)
    button_frame.pack(pady=5)

    view_btn = ttk.Button(button_frame, text="Показать графики", command=on_open_png, style="PFED.TButton", width=16)
    view_btn.pack(side='left', padx=8)

    folder_btn = ttk.Button(button_frame, text="Открыть папку", command=on_open_folder, style="PFED.TButton", width=16)
    folder_btn.pack(side='left', padx=8)

    exit_btn = ttk.Button(button_frame, text="Выйти", command=on_close, style="PFED.TButton", width=16)
    exit_btn.pack(side='left', padx=8)

    top.update_idletasks()
    width = top.winfo_width()
    height = top.winfo_height()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f'{width}x{height}+{x}+{y}')

    top.transient(parent)
    top.grab_set()
    top.protocol("WM_DELETE_WINDOW", on_close)
    view_btn.focus_set()

class DensityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.file_paths = []
        self.save_path = ""
        self.save_folder = ""
        self.density_threshold = 0.5
        self.single_plot_mode = BooleanVar()
        self.combined_data = []

        self.title("PFED v0.7.0")
        self.geometry("500x220")
        self.minsize(450, 190)

        self.colors = {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "bg_light": "#f5f5f5",
            "text_dark": "#34495e",
            "success": "#27ae60",
            "warning": "#f39c12",
        }
        self.configure(bg=self.colors["bg_light"])

        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        icon_path = os.path.join(parent_directory, '.gitpics', 'pfed.ico')
        try:
            self.iconbitmap(icon_path)
            self.wm_iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background=self.colors["bg_light"])
        self.style.configure("TLabel", background=self.colors["bg_light"], font=("Segoe UI", 10))
        self.style.configure("PFED.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        self.style.map("PFED.TButton",
                       background=[("active", self.colors["secondary"]), ("!disabled", self.colors["primary"]), ("disabled", "#bdc3c7")],
                       foreground=[("active", self.colors["text_dark"]), ("!disabled", self.colors["bg_light"]), ("disabled", "#7f8c8d")])
        self.style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"))
        self.style.configure("TProgressbar", troughcolor=self.colors["bg_light"], background=self.colors["success"])

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(main_frame, text="Выберите файлы для обработки", style="Status.TLabel", wraplength=450)
        self.status_label.pack(pady=(0, 15))

        self.checkbox = ttk.Checkbutton(main_frame, text="форм-фактор: единый график для всех временных участков",
                                       variable=self.single_plot_mode)
        self.checkbox.pack(pady=(0, 15))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.select_file_btn = ttk.Button(button_frame, text="Выбрать файлы", command=self.select_files, width=20, style="PFED.TButton")
        self.select_file_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True)

        self.process_btn = ttk.Button(button_frame, text="Обработать", command=self.start_processing, state="disabled", width=20, style="PFED.TButton")
        self.process_btn.pack(side=tk.LEFT, padx=(10, 0), expand=True)

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(pady=(10, 0), fill=tk.X, expand=True)
        self.progress_bar.pack_forget()

        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def select_files(self):
        self.file_paths = filedialog.askopenfilenames(
            title="Выберите файлы с результатами формата peoples_detailed_nnnnnn_n.tsv",
            filetypes=[("Файлы формата TSV", "*.tsv")]
        )
        if self.file_paths:
            status_text = f"Выбрано файлов: {len(self.file_paths)}"
            self.status_label.config(text=status_text, foreground=self.colors["success"])
            self.process_btn.config(state="normal")
        else:
            self.status_label.config(text="Файлы не выбраны. Пожалуйста, выберите файлы.", foreground=self.colors["warning"])
            self.process_btn.config(state="disabled")

    def start_processing(self):
        if not self.file_paths:
            messagebox.showerror("Ошибка", "Не выбраны файлы для обработки.")
            return

        mode_text = "единый график" if self.single_plot_mode.get() else "отдельные графики"
        self.status_label.config(text=f"Обработка файлов ({mode_text})...", foreground=self.colors["text_dark"])
        self.select_file_btn.config(state="disabled")
        self.process_btn.config(state="disabled")
        self.checkbox.config(state="disabled")
        self.update_idletasks()

        self.progress_bar.pack(pady=(10, 0), fill=tk.X, expand=True)
        
        if self.single_plot_mode.get():
            self._process_single_plot_mode()
        else:
            self._process_multiple_plot_mode()

        self.progress_bar.pack_forget()
        self.show_results_dialog()

    def _process_single_plot_mode(self):
        self.progress_bar["maximum"] = len(self.file_paths)
        self.combined_data = []
        
        for i, file_path in enumerate(self.file_paths):
            evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded = self.process_data([file_path])
            
            folder_path = os.path.dirname(file_path)
            second_folder_name = os.path.split(os.path.split(folder_path)[0])[-1]
            
            self.combined_data.append({
                'evac_times': evac_times,
                'total_delta_sum': total_delta_sum,
                'first_time_exceeded': first_time_exceeded,
                'last_time_exceeded': last_time_exceeded,
                'folder_name': second_folder_name
            })
            
            self.progress_bar["value"] = i + 1
            self.update_idletasks()
        
        # Create combined plot
        first_file_path = self.file_paths[0]
        folder_path = os.path.dirname(first_file_path)
        self.save_folder = os.path.abspath(os.path.join(folder_path, '..', '..', '..'))
        file_name = os.path.basename(file_path).replace('.tsv', f'_{second_folder_name}.png')   #file_name = "combined_density_plot.png"
        self.save_path = os.path.join(self.save_folder, file_name)
        
        self.plot_densities_combined(self.combined_data, self.density_threshold, self.save_path)
        print(f"Объединенный график сохранен по адресу: {self.save_path}")

    def _process_multiple_plot_mode(self):
        self.progress_bar["maximum"] = len(self.file_paths)
        
        for i, file_path in enumerate(self.file_paths):
            evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded = self.process_data([file_path])

            folder_path = os.path.dirname(file_path)
            second_folder_name = os.path.split(os.path.split(folder_path)[0])[-1]
            self.save_folder = os.path.abspath(os.path.join(folder_path, '..', '..', '..'))
            file_name = os.path.basename(file_path).replace('.tsv', f'_{second_folder_name}.png')
            self.save_path = os.path.join(self.save_folder, file_name)
            
            self.addToClipBoard(second_folder_name)

            self.plot_densities(evac_times, self.density_threshold, total_delta_sum, first_time_exceeded, last_time_exceeded, self.save_path)
            print(f"Графики сохранены по адресу: {self.save_path}")
            
            self.progress_bar["value"] = i + 1
            self.update_idletasks()

    def show_results_dialog(self):
        mode_text = "единый график" if self.single_plot_mode.get() else f"{len(self.file_paths)} отдельных графиков"
        status_text = f"Обработка завершена. Создан: {mode_text}"
        self.status_label.config(text=status_text, foreground=self.colors["success"])
        self.select_file_btn.config(state="normal")
        self.process_btn.config(state="normal")
        self.checkbox.config(state="normal")
        custom_message_box(self, self.open_png, self.open_png_folder, self.quit)

    def open_png(self):
        os.startfile(self.save_path)

    def open_png_folder(self):
        os.startfile(self.save_folder)

    def addToClipBoard(self, text):
        command = 'echo ' + text.strip() + '| clip'
        os.system(command)

    def clean_and_convert_float(self, number_str):
        number_str = number_str.strip().split(' ')[0]
        return float(number_str.replace(',', '.'))

    def parse_evac_time(self, line):
        return self.clean_and_convert_float(line.split(':')[1])

    def compute_deltas(self, evac_times):
        deltas = []
        first_time_exceeded = None
        last_time_exceeded = None
        previous_time = None

        for time, max_density in evac_times:
            if max_density >= self.density_threshold:
                if first_time_exceeded is None:
                    first_time_exceeded = time
                last_time_exceeded = time
                if previous_time is not None:
                    delta = time - previous_time
                else:
                    delta = 0.2
                deltas.append(delta)
            else:
                deltas.append(0)
            previous_time = time
        return sum(deltas), first_time_exceeded, last_time_exceeded

    def process_data(self, file_paths):
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
                        time = self.parse_evac_time(first_cell)
                        current_max_density = 0
                    elif len(row) > 4 and row[4] != 'Density':
                        try:
                            density = abs(log10(self.clean_and_convert_float(row[4]))) - 0.8
                            if density > current_max_density:
                                current_max_density = density
                        except ValueError:
                            pass
                if current_max_density > 0 and time is not None:
                    evac_times.append((time, current_max_density))

        total_delta_sum, first_time_exceeded, last_time_exceeded = self.compute_deltas(evac_times)
        print(f"tск* - Время существования всех скоплений на временном отрезке [{first_time_exceeded} ; {last_time_exceeded}] сек, \nгде плотность потока, состоящего хотя бы из 2 человек, превышает {self.density_threshold} ($м2/м2$): {total_delta_sum:.1f} сек.")
        return evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded

    def plot_densities(self, evac_times, density_threshold, total_delta_sum, first_time_exceeded, last_time_exceeded, save_path):
        times, densities = zip(*evac_times)
        plt.figure(figsize=(12, 4))
        plt.plot(times, densities, drawstyle="steps-post", linewidth=1, color="#00FF00ff",
                 marker='o', markersize=1, markeredgewidth=1, markerfacecolor="#1f77b4ff", markeredgecolor="#1f77b4ff")
        plt.axhline(density_threshold, color="red", linestyle="--", lw=2, label=f'Критическая плотность >= {density_threshold} ($м^2/м^2$)')
        plt.fill_between(times, densities, density_threshold,
                         where=[d >= density_threshold for d in densities],
                         color='red', alpha=0.3, label='Зона критической плотности')
        plt.xlabel('Время (сек)')
        plt.ylabel('Плотность ($м^2/м^2$)')
        plt.title(f'График плотности людского потока\nВремя существования скоплений (tск*): {total_delta_sum:.1f} сек', fontsize=12)
        plt.grid(True)
        plt.legend(loc='upper center')  #, bbox_to_anchor=(0.5, 1.0))
        plt.savefig(save_path, bbox_inches='tight', format='png')
        plt.close()

    def plot_densities_combined(self, combined_data, density_threshold, save_path):
        plt.figure(figsize=(14, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        total_combined_delta = 0
        all_first_times = []
        all_last_times = []
        
        for i, data in enumerate(combined_data):
            evac_times = data['evac_times']
            folder_name = data['folder_name']
            total_delta_sum = data['total_delta_sum']
            first_time_exceeded = data['first_time_exceeded']
            last_time_exceeded = data['last_time_exceeded']
            
            if evac_times:
                times, densities = zip(*evac_times)
                color = colors[i % len(colors)]
                
                plt.plot(times, densities, drawstyle="steps-post", linewidth=2, color=color,
                        marker='o', markersize=2, markeredgewidth=1,
                        markerfacecolor=color, markeredgecolor=color,
                        label=f'{folder_name} (tск*: {total_delta_sum:.1f}с)')
                
                total_combined_delta += total_delta_sum
                if first_time_exceeded is not None:
                    all_first_times.append(first_time_exceeded)
                if last_time_exceeded is not None:
                    all_last_times.append(last_time_exceeded)
        
        plt.axhline(density_threshold, color="red", linestyle="--", lw=2,
                   label=f'Критическая плотность >= {density_threshold} ($м^2/м^2$)')
        
        overall_first = min(all_first_times) if all_first_times else None
        overall_last = max(all_last_times) if all_last_times else None
        
        plt.xlabel('Время (сек)')
        plt.ylabel('Плотность ($м^2/м^2$)')
        plt.title(f'Объединенный график плотности людского потока\n'
                 f'Общее время существования скоплений: {total_combined_delta:.1f} сек\n'
                 f'Временной диапазон: [{overall_first} ; {overall_last}] сек', fontsize=12)
        plt.grid(True)
        plt.legend(loc='upper right') #, bbox_to_anchor=(1.02, 1.0))
        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight', format='png', dpi=150)
        plt.close()

if __name__ == "__main__":
    app = DensityApp()
    app.mainloop()