import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class ThresholdDialog(tk.Toplevel):
    """Dialog do interaktywnego progowania z wizualizacją histogramu"""
    
    def __init__(self, parent, img, app_manager, mode="binary"):
        """
        Parametry:
            parent: okno rodzica
            img: obraz numpy.ndarray (grayscale)
            app_manager: instancja AppManager
            mode: 'binary' lub 'levels'
        """
        super().__init__(parent)
        
        self.img = img
        self.app_manager = app_manager
        self.mode = mode
        self.on_result_callback = None  # Callback z wynikiem
        
        title = "Progowanie binarne" if mode == "binary" else "Progowanie z poziomami"
        self.title(title)
        self.geometry("700x550")
        
        self._create_ui()
        
    def _create_ui(self):
        """Tworzy interfejs dialogu"""
        # Górna ramka - histogram
        hist_frame = tk.Frame(self)
        hist_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Oblicz histogram
        histogram_stats = self.app_manager.calculate_histograms(self.img)
        self.hist_data = histogram_stats[0].histogram
        
        # Wykres
        self.fig = Figure(figsize=(7, 3.5))
        self.ax = self.fig.add_subplot(111)
        
        x = np.arange(256)
        self.ax.bar(x, self.hist_data, color='gray', width=1.0, alpha=0.7, edgecolor='none')
        
        mode_text = "Binarne" if self.mode == "binary" else "Z poziomami"
        self.ax.set_title(f"Histogram - Progowanie {mode_text}")
        self.ax.set_xlabel("Wartość piksela")
        self.ax.set_ylabel("Częstość")
        self.ax.set_xlim(0, 255)
        
        # Linia progu
        self.threshold_line = self.ax.axvline(
            x=128, 
            color='red', 
            linestyle='--', 
            linewidth=2, 
            label='Próg'
        )
        self.ax.legend()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=hist_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Slider frame
        slider_frame = tk.Frame(self)
        slider_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            slider_frame,
            text="Wartość progu:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.threshold_var = tk.IntVar(value=128)
        self.threshold_label = tk.Label(
            slider_frame,
            text="128",
            font=("Arial", 10, "bold"),
            width=5,
            anchor="w"
        )
        self.threshold_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.slider = tk.Scale(
            slider_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            command=self._update_threshold,
            showvalue=False,
            length=400
        )
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Preview checkbox
        preview_frame = tk.Frame(self)
        preview_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)
        
        self.preview_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            preview_frame,
            text="Pokaż podgląd",
            variable=self.preview_var,
            command=self._toggle_preview
        ).pack(side=tk.LEFT)
        
        # Info label
        info_text = (
            "Binarne: piksele poniżej progu → 0, powyżej → 255" 
            if self.mode == "binary" 
            else "Z poziomami: piksele poniżej progu → 0, powyżej → oryginalna wartość"
        )
        tk.Label(
            preview_frame,
            text=info_text,
            font=("Arial", 8),
            fg="#666"
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        tk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply,
            width=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Anuluj",
            command=self.destroy,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
    def _update_threshold(self, val):
        """Aktualizuje linię progu na histogramie"""
        threshold = int(float(val))
        self.threshold_label.config(text=str(threshold))
        self.threshold_line.set_xdata([threshold, threshold])
        self.canvas.draw()
        
        # Auto-preview jeśli włączony
        if self.preview_var.get():
            self._show_preview()
            
    def _toggle_preview(self):
        """Włącza/wyłącza podgląd"""
        if self.preview_var.get():
            self._show_preview()
        else:
            if hasattr(self, 'preview_window') and self.preview_window.winfo_exists():
                self.preview_window.destroy()
                
    def _show_preview(self):
        """Pokazuje podgląd progowania"""
        threshold = self.threshold_var.get()
        
        if self.mode == "binary":
            result = self.app_manager.apply_threshold_binary(self.img, threshold)
        else:
            result = self.app_manager.apply_threshold_with_levels(self.img, threshold)
        
        # Utwórz lub zaktualizuj okno podglądu
        if not hasattr(self, 'preview_window') or not self.preview_window.winfo_exists():
            from PIL import Image, ImageTk
            import cv2
            
            self.preview_window = tk.Toplevel(self)
            self.preview_window.title("Podgląd")
            
            self.preview_label = tk.Label(self.preview_window, bg='#2b2b2b')
            self.preview_label.pack()
        
        # Skaluj zachowując proporcje do max 600x600
        from PIL import Image, ImageTk
        import cv2
        
        h, w = result.shape[:2]
        max_size = 600
        
        # Oblicz współczynnik skalowania
        scale = min(max_size / w, max_size / h)
        
        # Jeśli obraz jest większy niż max_size, przeskaluj
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            display = cv2.resize(result, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        else:
            display = result
        
        # Ustaw rozmiar okna na rozmiar obrazu
        self.preview_window.geometry(f"{display.shape[1]}x{display.shape[0]}")
        
        # Konwertuj i wyświetl
        img_pil = Image.fromarray(display)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        self.preview_label.config(image=img_tk)
        self.preview_label.image = img_tk  # Keep reference
        
    def _apply(self):
        """Zastosuj progowanie i zwróć wynik"""
        threshold = self.threshold_var.get()
        
        if self.mode == "binary":
            result = self.app_manager.apply_threshold_binary(self.img, threshold)
        else:
            result = self.app_manager.apply_threshold_with_levels(self.img, threshold)
        
        if self.on_result_callback:
            self.on_result_callback(result)
        
        self.destroy()