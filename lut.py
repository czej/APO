from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np

# class LutViewer(tk.Toplevel):
#     def __init__(self, root, luts, title="LUT Viewer"):
#         super().__init__(root)
#         self.title(title)
#         self.luts = luts  # lista tablic LUT (np. 3 dla BGR)

#         fig = Figure(figsize=(6,4))
#         self.ax = fig.add_subplot(111)
#         colors = ['b', 'g', 'r'] if len(luts) == 3 else ['k']

#         for lut, c in zip(luts, colors):
#             self.ax.plot(lut, color=c)
#         self.ax.set_title("Tablica LUT")
#         self.ax.set_xlabel("Wartość wejściowa")
#         self.ax.set_ylabel("Wartość wyjściowa")
#         self.ax.set_xlim(0,255)
#         self.ax.set_ylim(0,255)

#         canvas = FigureCanvasTkAgg(fig, master=self)
#         canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
#         canvas.draw()


# class LutViewer(tk.Toplevel):
#     def __init__(self, root, luts, title="LUT Viewer"):
#         super().__init__(root)
#         self.title(title)
#         self.luts = luts  # lista tablic LUT (np. 3 dla BGR)

#         # Layout: wykres po lewej, lista wartości po prawej
#         self.columnconfigure(0, weight=3)
#         self.columnconfigure(1, weight=1)
#         self.rowconfigure(0, weight=1)

#         # Matplotlib Figure (wykres LUT)
#         from matplotlib.figure import Figure
#         from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#         fig = Figure(figsize=(6,4))
#         self.ax = fig.add_subplot(111)
#         colors = ['b', 'g', 'r'] if len(luts) == 3 else ['k']

#         for lut, c in zip(luts, colors):
#             self.ax.plot(lut, color=c)
#         self.ax.set_title("Tablica LUT")
#         self.ax.set_xlabel("Wartość wejściowa")
#         self.ax.set_ylabel("Wartość wyjściowa")
#         self.ax.set_xlim(0,255)
#         self.ax.set_ylim(0,255)

#         canvas = FigureCanvasTkAgg(fig, master=self)
#         canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

#         # Tekst z wartościami LUT
#         self.text = tk.Text(self, width=20)
#         self.text.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

#         # Wypisz LUT-y do text widgetu
#         self.show_luts_values()

#     def show_luts_values(self):
#         self.text.delete("1.0", tk.END)
#         colors = ['B', 'G', 'R'] if len(self.luts) == 3 else ['Mono']

#         for i, lut in enumerate(self.luts):
#             self.text.insert(tk.END, f"{colors[i]} channel LUT values:\n")
#             for val_in in range(256):
#                 self.text.insert(tk.END, f"{val_in:3d} -> {lut[val_in]:3d}\n")
#             self.text.insert(tk.END, "\n")
#         self.text.config(state=tk.DISABLED)


class LutViewer(tk.Toplevel):
    def __init__(self, root, luts, title="LUT Viewer"):
        super().__init__(root)
        self.title(title)
        self.luts = luts

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        fig = Figure(figsize=(6,4))
        self.ax = fig.add_subplot(111)
        colors = ['b', 'g', 'r'] if len(luts) == 3 else ['k']

        x = np.arange(256)
        for lut, c in zip(luts, colors):
            self.ax.bar(x, lut, color=c, width=1.0, alpha=0.6)

        self.ax.set_title("Tablica LUT (wykres słupkowy)")
        self.ax.set_xlabel("Wartość wejściowa")
        self.ax.set_ylabel("Wartość wyjściowa")
        self.ax.set_xlim(0,255)
        self.ax.set_ylim(0,255)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.text = tk.Text(self, width=20)
        self.text.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.show_luts_values()

    def show_luts_values(self):
        self.text.delete("1.0", tk.END)
        colors = ['B', 'G', 'R'] if len(self.luts) == 3 else ['Mono']

        for i, lut in enumerate(self.luts):
            self.text.insert(tk.END, f"{colors[i]} channel LUT values:\n")
            for val_in in range(256):
                self.text.insert(tk.END, f"{val_in:3d} -> {lut[val_in]:3d}\n")
            self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)