import tkinter as tk
from tkinter import ttk, Canvas
import numpy as np


class HistogramViewer(tk.Toplevel):
    """Okno wyświetlające histogram obrazu - rysowany ręcznie zgodnie z algorytmem"""
    
    def __init__(self, root, histograms, title="Histogram"):
        """
        Parametry:
            root: okno rodzica
            histograms: lista Histogram namedtuples z backend.Histogram
            title: tytuł okna
        """
        super().__init__(root)
        self.title(title)
        self.histograms = histograms
        
        self.geometry("950x650")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._create_ui()
        
    def _create_ui(self):
        """Tworzy interfejs okna histogramu"""
        # Notebook z zakładkami dla kanałów
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Określ nazwy kanałów
        if len(self.histograms) == 3:
            channel_names = ['Blue', 'Green', 'Red']
            colors = ['blue', 'green', 'red']
        else:
            channel_names = ['Gray']
            colors = ['gray']
        
        # Utwórz zakładki dla każdego kanału
        for i, (hist_data, name, color) in enumerate(zip(self.histograms, channel_names, colors)):
            tab = self._create_histogram_tab(hist_data, name, color)
            self.notebook.add(tab, text=name)
            
    def _create_histogram_tab(self, hist_data, name, color):
        """
        Tworzy pojedynczą zakładkę histogramu - RĘCZNIE RYSOWANY
        
        Parametry:
            hist_data: Histogram namedtuple
            name: nazwa kanału
            color: kolor wykresu
        """
        tab = ttk.Frame(self.notebook)
        
        # Layout configuration
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)
        
        # === LEFT SIDE: Canvas z ręcznie rysowanym histogramem ===
        canvas_frame = tk.Frame(tab)
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Canvas do rysowania
        canvas_width = 600
        canvas_height = 400
        canvas = Canvas(canvas_frame, width=canvas_width, height=canvas_height, bg='white')
        canvas.pack()
        
        # Tytuł
        canvas.create_text(
            canvas_width // 2, 20,
            text=f"Histogram - {name} Channel",
            font=("Arial", 12, "bold"),
            fill="black"
        )
        
        # === ALGORYTM GENEROWANIA WYKRESU SŁUPKOWEGO ===
        
        # 1. Wyszukaj maksymalną wartość w tablicy h (LUT)
        h_max = np.max(hist_data.histogram)
        
        if h_max == 0:
            h_max = 1  # Uniknij dzielenia przez zero
        
        # 2. Przygotuj ramkę histogramu i opis osi
        plot_x = 50  # Lewy margines
        plot_y = 50  # Górny margines
        plot_width = canvas_width - 100  # Szerokość obszaru wykresu
        plot_height = canvas_height - 150  # Wysokość obszaru wykresu
        
        # Ramka wykresu
        canvas.create_rectangle(
            plot_x, plot_y,
            plot_x + plot_width, plot_y + plot_height,
            outline="black", width=1
        )
        
        # Opis osi X
        canvas.create_text(
            plot_x + plot_width // 2, plot_y + plot_height + 40,
            text="Wartość piksela",
            font=("Arial", 10),
            fill="black"
        )
        
        # Opis osi Y
        canvas.create_text(
            plot_x - 30, plot_y + plot_height // 2,
            text="Liczba wystąpień",
            font=("Arial", 10),
            angle=90,
            fill="black"
        )

        # Skala na osi Y
        def get_nice_tick_interval(max_val, num_intervals=5):
            """Zwraca ładny odstęp dla dokładnie num_intervals przedziałów"""
            if max_val == 0:
                return 100
            
            # Surowy odstęp
            raw_interval = max_val / num_intervals
            
            # Znajdź rząd wielkości
            magnitude = 10 ** int(np.floor(np.log10(raw_interval)))
            
            # Zaokrąglij do ładnej liczby (1, 2, 2.5, 5, 10) * magnitude
            nice_steps = [1, 2, 2.5, 5, 10]
            normalized = raw_interval / magnitude
            
            for step in nice_steps:
                if normalized <= step:
                    return int(step * magnitude)
            
            return int(10 * magnitude)

        num_intervals = 5
        tick_interval = get_nice_tick_interval(h_max, num_intervals)

        # Rysuj przedziały
        for i in range(num_intervals + 1):
            value = i * tick_interval
            
            # Pomiń kreską jeśli wartość przekracza h_max
            if value > h_max:
                break
            
            # Pozycja Y na canvasie (odwrócona - 0 na górze)
            if h_max > 0:
                y = plot_y + plot_height - (value / h_max) * plot_height
            else:
                y = plot_y + plot_height
            
            # Kreska
            canvas.create_line(plot_x - 5, y, plot_x, y, fill="black")
            
            # Wartość
            canvas.create_text(
                plot_x - 15, y,
                text=f"{value:,}",
                font=("Arial", 8),
                anchor="e"
            )

        # Dodatkowo: wartość maksymalna na samej górze (jeśli różni się od ostatniej kreski)
        if h_max != num_intervals * tick_interval:
            y_max_pos = plot_y
            
            # Wartość max na górze (bez kreski, żeby nie zaśmiecać)
            canvas.create_text(
                plot_x - 15, y_max_pos,
                text=f"{int(h_max):,}",
                font=("Arial", 8, "bold"),
                anchor="e",
                fill="red"
            )
                        
        # Skala na osi X (co 32 wartości)
        for i in range(0, 256, 32):
            x = plot_x + (i / 255) * plot_width
            canvas.create_line(x, plot_y + plot_height, x, plot_y + plot_height + 5, fill="black")
            canvas.create_text(x, plot_y + plot_height + 15, text=str(i), font=("Arial", 8))
        
        # 3. For wszystkich elementów tablicy LUT - rysuj słupki
        bar_width = plot_width / 256  # Szerokość pojedynczego słupka
        
        # Mapowanie kolorów
        color_map = {
            'blue': '#4169E1',
            'green': '#32CD32',
            'red': '#DC143C',
            'gray': '#808080'
        }
        bar_color = color_map.get(color, '#808080')
        
        for i in range(256):
            # Unormuj wartość h(i) - normalizacja do wysokości słupka
            h_value = hist_data.histogram[i]
            
            if h_value > 0:
                # Narysuj słupek o długości odpowiadającej wartości unormowanej
                normalized_height = (h_value / h_max) * plot_height
                
                # Współrzędne słupka
                x1 = plot_x + i * bar_width
                y1 = plot_y + plot_height - normalized_height
                x2 = x1 + bar_width
                y2 = plot_y + plot_height
                
                # Rysuj słupek
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bar_color,
                    outline=bar_color,
                    width=0
                )
        
        # 4. Kumuluj informacje o parametrach rozkładu statystycznego jasności
        # (już policzone w hist_data)
        
        # === RIGHT SIDE: Statistics and LUT ===
        right_frame = tk.Frame(tab)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Statistics box
        stats_frame = tk.LabelFrame(right_frame, text="Statystyki", font=("Arial", 10, "bold"))
        stats_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        stats_text = (
            f"Liczba pikseli: {hist_data.pixels_num:,}\n"
            f"Średnia: {hist_data.mean:.2f}\n"
            f"Odch. std: {hist_data.std:.2f}\n"
            f"Mediana: {hist_data.median}\n"
            f"Min: {hist_data.min}\n"
            f"Max: {hist_data.max}"
        )
        
        tk.Label(
            stats_frame,
            text=stats_text,
            font=("Courier", 9),
            justify=tk.LEFT,
            anchor="w"
        ).pack(padx=10, pady=10, anchor="w")
        
        # LUT (Look-Up Table) values
        lut_frame = tk.LabelFrame(right_frame, text="Tablica LUT", font=("Arial", 10, "bold"))
        lut_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        lut_frame.columnconfigure(0, weight=1)
        lut_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text_scroll_frame = tk.Frame(lut_frame)
        text_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_scroll_frame.columnconfigure(0, weight=1)
        text_scroll_frame.rowconfigure(0, weight=1)
        
        text = tk.Text(
            text_scroll_frame,
            width=30,
            font=("Courier", 8),
            wrap=tk.NONE
        )
        text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = tk.Scrollbar(text_scroll_frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.config(yscrollcommand=scrollbar.set)
        
        # Fill LUT values
        text.insert(tk.END, "Wartość | Liczba\n")
        text.insert(tk.END, "--------+--------\n")
        
        for val in range(256):
            count = int(hist_data.histogram[val])
            if count > 0:  # Pokaż tylko niezerowe wartości
                text.insert(tk.END, f"  {val:3d}   | {count:7d}\n")
        
        text.config(state=tk.DISABLED)
        
        # === BOTTOM: Dodaj informacje o rozkładzie statystycznym ===
        bottom_frame = tk.Frame(tab, bg="#f0f0f0")
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Dodatkowe statystyki
        non_zero = np.count_nonzero(hist_data.histogram)
        min_nonzero = np.min(np.where(hist_data.histogram > 0)[0]) if non_zero > 0 else 0
        max_nonzero = np.max(np.where(hist_data.histogram > 0)[0]) if non_zero > 0 else 255
        range_val = max_nonzero - min_nonzero
        
        extra_stats = (
            f"Zakres: {min_nonzero}-{max_nonzero} (rozpiętość: {range_val})  |  "
            f"Unikalne wartości: {non_zero}  |  "
            f"Dominanta: {np.argmax(hist_data.histogram)} (częstość: {np.max(hist_data.histogram)})"
        )
        
        tk.Label(
            bottom_frame,
            text=extra_stats,
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#333"
        ).pack(pady=8)
        
        return tab