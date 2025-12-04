import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class HistogramViewer(tk.Toplevel):
    def __init__(self, root, histograms, title="Histogram"):
        super().__init__(root)
        self.title(title)
        self.histograms = histograms  # list of Histogram namedtuples

        self.geometry("900x600")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        colors = ['Blue', 'Green', 'Red'] if len(histograms) == 3 else ['Grey']

        for i, hist_data in enumerate(histograms):
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=colors[i])

            # Layout config
            tab.columnconfigure(0, weight=3)
            tab.columnconfigure(1, weight=1)
            tab.rowconfigure(0, weight=1)

            # Histogram plot
            fig = Figure(figsize=(5, 4))
            ax = fig.add_subplot(111)
            x = np.arange(256)
            ax.bar(x, hist_data.histogram, color=colors[i].lower(), width=1.0, alpha=0.7)
            ax.set_title(f"Histogram kanału {colors[i]}")
            ax.set_xlabel("Wartość piksela")
            ax.set_ylabel("Liczba wystąpień")
            ax.set_xlim(0, 255)

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

            # Text and scrollbar
            text_frame = tk.Frame(tab)
            text_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            text_frame.columnconfigure(0, weight=1)
            text_frame.rowconfigure(0, weight=1)

            text = tk.Text(text_frame, width=28)
            text.grid(row=0, column=0, sticky="nsew")

            scrollbar = tk.Scrollbar(text_frame, command=text.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            text.config(yscrollcommand=scrollbar.set)

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

            # Statistical values
            stats_frame = tk.Frame(tab)
            stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
            stats_frame.columnconfigure(0, weight=1)

            row1 = (
                f"Liczba pikseli: {hist_data.pixels_num}    "
                f"Średnia: {hist_data.mean:.2f}    "
                f"Mediana: {hist_data.median}"
            )
            row2 = (
                f"Odchylenie std: {hist_data.std:.2f}    "
                f"Min: {hist_data.min}    "
                f"Max: {hist_data.max}"
            )

            tk.Label(
                stats_frame,
                text=row1,
                font=("Consolas", 10),
                anchor="w",
                justify="left"
            ).grid(row=0, column=0, sticky="w", pady=(3, 0))

            tk.Label(
                stats_frame,
                text=row2,
                font=("Consolas", 10),
                anchor="w",
                justify="left"
            ).grid(row=1, column=0, sticky="w", pady=(0, 3))

            text.insert(tk.END, "Wartości histogramu:\n\n")
            for val in range(256):
                count = int(hist_data.histogram[val])
                text.insert(tk.END, f"[{val:3d}]: {count}\n")

            text.config(state=tk.DISABLED)
