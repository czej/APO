"""
Dialogi dla operacji segmentacji - LAB3 Zadanie 2
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np


class DoubleThresholdDialog:
    """Dialog dla progowania z dwoma progami"""
    
    def __init__(self, parent, image, app_manager):
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        # Walidacja obrazu
        if len(image.shape) != 2:
            raise ValueError("Operacja wymaga obrazu w skali szarości")
        
        # Tworzenie okna dialogowego
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Progowanie z dwoma progami")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        # Zmienne
        self.lower_threshold = tk.IntVar(value=50)
        self.upper_threshold = tk.IntVar(value=200)
        self.preview_enabled = tk.BooleanVar(value=False)
        
        self._create_widgets()
        # Nie wywołujemy _update_preview() - tylko gdy user zaznaczy checkbox
        
    def _create_widgets(self):
        """Tworzy widgety dialogu"""
        # Ramka informacyjna
        info_frame = ttk.LabelFrame(self.dialog, text="Informacje", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = (
            "Progowanie z dwoma progami:\n"
            "• Piksele w zakresie [Dolny próg, Górny próg] → 255 (białe)\n"
            "• Pozostałe piksele → 0 (czarne)\n"
        )
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Ramka parametrów
        params_frame = ttk.LabelFrame(self.dialog, text="Parametry", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Dolny próg
        lower_frame = ttk.Frame(params_frame)
        lower_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(lower_frame, text="Dolny próg:", width=15).pack(side=tk.LEFT)
        lower_scale = ttk.Scale(
            lower_frame,
            from_=0,
            to=255,
            variable=self.lower_threshold,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_threshold_change()
        )
        lower_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.lower_label = ttk.Label(lower_frame, text="50", width=5)
        self.lower_label.pack(side=tk.LEFT)
        
        # Górny próg
        upper_frame = ttk.Frame(params_frame)
        upper_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(upper_frame, text="Górny próg:", width=15).pack(side=tk.LEFT)
        upper_scale = ttk.Scale(
            upper_frame,
            from_=0,
            to=255,
            variable=self.upper_threshold,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_threshold_change()
        )
        upper_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.upper_label = ttk.Label(upper_frame, text="200", width=5)
        self.upper_label.pack(side=tk.LEFT)
        
        # Podgląd na żywo
        ttk.Checkbutton(
            params_frame,
            text="Podgląd na żywo",
            variable=self.preview_enabled,
            command=self._update_preview
        ).pack(pady=10)
        
        # Informacja o wynikach
        self.stats_label = ttk.Label(params_frame, text="", justify=tk.LEFT)
        self.stats_label.pack(pady=5)
        
        # Przyciski
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def _on_threshold_change(self):
        """Wywoływane gdy zmienią się progi"""
        lower = int(self.lower_threshold.get())
        upper = int(self.upper_threshold.get())
        
        self.lower_label.config(text=str(lower))
        self.upper_label.config(text=str(upper))
        
        if self.preview_enabled.get():
            self._update_preview()
    
    def _update_preview(self):
        """Aktualizuje podgląd i statystyki"""
        if not self.preview_enabled.get():
            if hasattr(self, 'preview_window') and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            return
        
        lower = int(self.lower_threshold.get())
        upper = int(self.upper_threshold.get())
        
        # Oblicz wynik
        from backend.SegmentationOperations import SegmentationOperations
        result = SegmentationOperations.threshold_double(
            self.image, lower, upper
        )
        
        # Statystyki
        white_pixels = np.sum(result == 255)
        total_pixels = result.size
        percentage = (white_pixels / total_pixels) * 100
        
        stats_text = (
            f"Białe piksele: {white_pixels:,} / {total_pixels:,} "
            f"({percentage:.2f}%)"
        )
        self.stats_label.config(text=stats_text)
        
        self.result = result
        
        # Pokaż podgląd
        self._show_preview_window(result)
    
    def _show_preview_window(self, result):
        """Pokazuje podgląd progowania w osobnym oknie"""
        # Utwórz lub zaktualizuj okno podglądu
        if not hasattr(self, 'preview_window') or not self.preview_window.winfo_exists():
            from PIL import Image, ImageTk
            import cv2
            
            self.preview_window = tk.Toplevel(self.dialog)
            self.preview_window.title("Podgląd")
            self.preview_window.attributes('-topmost', True)  # Zawsze na wierzchu
            
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
        """Aplikuje operację i zamyka dialog"""
        lower = int(self.lower_threshold.get())
        upper = int(self.upper_threshold.get())
        
        from backend.SegmentationOperations import SegmentationOperations
        result = SegmentationOperations.threshold_double(
            self.image, lower, upper
        )
        
        if self.on_result_callback:
            self.on_result_callback(result)
        
        self.dialog.destroy()


class OtsuThresholdDialog:
    """Dialog dla progowania metodą Otsu"""
    
    def __init__(self, parent, image, app_manager):
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        # Walidacja obrazu
        if len(image.shape) != 2:
            raise ValueError("Operacja wymaga obrazu w skali szarości")
        
        # Tworzenie okna dialogowego
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Progowanie Otsu")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        
        self._create_widgets()
        self._calculate_otsu()
        
    def _create_widgets(self):
        """Tworzy widgety dialogu"""
        # Ramka informacyjna
        info_frame = ttk.LabelFrame(self.dialog, text="Informacje", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = (
            "Metoda Otsu automatycznie wyznacza optymalny próg binaryzacji.\n"
            "Algorytm minimalizuje wariancję wewnątrzklasową\n"
            "(lub maksymalizuje wariancję międzyklasową)."
        )
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Ramka wyników
        results_frame = ttk.LabelFrame(self.dialog, text="Wyniki", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Wyznaczony próg
        threshold_frame = ttk.Frame(results_frame)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            threshold_frame,
            text="Wyznaczony próg Otsu:",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)
        
        self.threshold_label = ttk.Label(
            threshold_frame,
            text="",
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        self.threshold_label.pack(side=tk.LEFT, padx=10)
        
        # Statystyki
        self.stats_label = ttk.Label(results_frame, text="", justify=tk.LEFT)
        self.stats_label.pack(pady=10)
        
        # Separator
        ttk.Separator(results_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Informacja dodatkowa
        help_text = (
            "Próg został automatycznie wyznaczony na podstawie\n"
            "rozkładu jasności w obrazie."
        )
        ttk.Label(results_frame, text=help_text, justify=tk.LEFT).pack()
        
        # Przyciski
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def _calculate_otsu(self):
        """Oblicza próg Otsu i wyświetla wyniki"""
        # Wyznacz próg Otsu
        from backend.SegmentationOperations import SegmentationOperations
        threshold_value, binary_image = SegmentationOperations.threshold_otsu(
            self.image
        )
        
        # Wyświetl wartość progu
        self.threshold_label.config(text=f"{threshold_value:.2f}")
        
        # Statystyki
        white_pixels = np.sum(binary_image == 255)
        total_pixels = binary_image.size
        percentage = (white_pixels / total_pixels) * 100
        
        stats_text = (
            f"Białe piksele: {white_pixels:,} / {total_pixels:,}\n"
            f"Procent: {percentage:.2f}%\n"
            f"Czarne piksele: {total_pixels - white_pixels:,} ({100-percentage:.2f}%)"
        )
        self.stats_label.config(text=stats_text)
        
        self.result = binary_image
        self.threshold_value = threshold_value
    
    def _apply(self):
        """Aplikuje operację i zamyka dialog"""
        if self.on_result_callback and self.result is not None:
            self.on_result_callback(self.result)
        
        self.dialog.destroy()


class AdaptiveThresholdDialog:
    """Dialog dla progowania adaptacyjnego"""
    
    def __init__(self, parent, image, app_manager):
        self.parent = parent
        self.image = image
        self.app_manager = app_manager
        self.result = None
        self.on_result_callback = None
        
        # Walidacja obrazu
        if len(image.shape) != 2:
            raise ValueError("Operacja wymaga obrazu w skali szarości")
        
        # Tworzenie okna dialogowego
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Progowanie adaptacyjne")
        self.dialog.geometry("550x500")
        self.dialog.transient(parent)
        
        # Zmienne
        self.method = tk.StringVar(value='mean')
        self.block_size = tk.IntVar(value=11)
        self.C = tk.IntVar(value=2)
        self.inverse = tk.BooleanVar(value=False)
        self.preview_enabled = tk.BooleanVar(value=False)
        
        self._create_widgets()
        # Nie wywołujemy _update_preview() - tylko gdy user zaznaczy checkbox
        
    def _create_widgets(self):
        """Tworzy widgety dialogu"""
        # Ramka informacyjna
        info_frame = ttk.LabelFrame(self.dialog, text="Informacje", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = (
            "Progowanie adaptacyjne:\n"
            "• Próg wyznaczany lokalnie dla każdego piksela\n"
            "• MEAN: średnia arytmetyczna w otoczeniu\n"
            "• GAUSSIAN: średnia ważona gaussowsko"
        )
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Ramka parametrów
        params_frame = ttk.LabelFrame(self.dialog, text="Parametry", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Metoda adaptacyjna
        method_frame = ttk.Frame(params_frame)
        method_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(method_frame, text="Metoda:", width=15).pack(side=tk.LEFT)
        ttk.Radiobutton(
            method_frame,
            text="Mean (średnia)",
            variable=self.method,
            value='mean',
            command=self._update_preview
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            method_frame,
            text="Gaussian (ważona)",
            variable=self.method,
            value='gaussian',
            command=self._update_preview
        ).pack(side=tk.LEFT, padx=5)
        
        # Rozmiar bloku
        block_frame = ttk.Frame(params_frame)
        block_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(block_frame, text="Rozmiar bloku:", width=15).pack(side=tk.LEFT)
        
        # Combo box z nieparzystymi wartościami
        block_values = [str(i) for i in range(3, 50, 2)]  # 3, 5, 7, 9, ..., 49
        self.block_combo = ttk.Combobox(
            block_frame,
            textvariable=self.block_size,
            values=block_values,
            width=10,
            state='readonly'
        )
        self.block_combo.pack(side=tk.LEFT, padx=5)
        self.block_combo.bind('<<ComboboxSelected>>', lambda e: self._update_preview())
        
        ttk.Label(
            block_frame,
            text="(rozmiar sąsiedztwa, nieparzysty)",
            foreground="gray"
        ).pack(side=tk.LEFT, padx=5)
        
        # Stała C
        c_frame = ttk.Frame(params_frame)
        c_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(c_frame, text="Stała C:", width=15).pack(side=tk.LEFT)
        c_scale = ttk.Scale(
            c_frame,
            from_=-10,
            to=10,
            variable=self.C,
            orient=tk.HORIZONTAL,
            command=lambda v: self._on_c_change()
        )
        c_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.c_label = ttk.Label(c_frame, text="2", width=5)
        self.c_label.pack(side=tk.LEFT)
        
        ttk.Label(
            params_frame,
            text="C: stała odejmowana od średniej (może być ujemna)",
            foreground="gray",
            font=("Arial", 8)
        ).pack(pady=2)
        
        # Opcja inwersji
        ttk.Checkbutton(
            params_frame,
            text="Inwersja (zamień czarne i białe)",
            variable=self.inverse,
            command=self._update_preview
        ).pack(pady=5)
        
        # Podgląd na żywo
        ttk.Checkbutton(
            params_frame,
            text="Podgląd na żywo",
            variable=self.preview_enabled,
            command=self._update_preview
        ).pack(pady=5)
        
        # Informacja o wynikach
        self.stats_label = ttk.Label(params_frame, text="", justify=tk.LEFT)
        self.stats_label.pack(pady=5)
        
        # Przyciski
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def _on_c_change(self):
        """Wywoływane gdy zmieni się C"""
        c_value = int(self.C.get())
        self.c_label.config(text=str(c_value))
        
        if self.preview_enabled.get():
            self._update_preview()
    
    def _update_preview(self):
        """Aktualizuje podgląd i statystyki"""
        if not self.preview_enabled.get():
            if hasattr(self, 'preview_window') and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            return
        
        method = self.method.get()
        block_size = int(self.block_size.get())
        c_value = int(self.C.get())
        
        # Oblicz wynik
        from backend.SegmentationOperations import SegmentationOperations
        if self.inverse.get():
            result = SegmentationOperations.threshold_adaptive_inverse(
                self.image, method, block_size, c_value
            )
        else:
            result = SegmentationOperations.threshold_adaptive(
                self.image, method, block_size, c_value
            )
        
        # Statystyki
        white_pixels = np.sum(result == 255)
        total_pixels = result.size
        percentage = (white_pixels / total_pixels) * 100
        
        stats_text = (
            f"Białe piksele: {white_pixels:,} / {total_pixels:,} "
            f"({percentage:.2f}%)"
        )
        self.stats_label.config(text=stats_text)
        
        self.result = result
        
        # Pokaż podgląd
        self._show_preview_window(result)
    
    def _show_preview_window(self, result):
        """Pokazuje podgląd progowania w osobnym oknie"""
        # Utwórz lub zaktualizuj okno podglądu
        if not hasattr(self, 'preview_window') or not self.preview_window.winfo_exists():
            from PIL import Image, ImageTk
            import cv2
            
            self.preview_window = tk.Toplevel(self.dialog)
            self.preview_window.title("Podgląd")
            self.preview_window.attributes('-topmost', True)  # Zawsze na wierzchu
            
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
        """Aplikuje operację i zamyka dialog"""
        method = self.method.get()
        block_size = int(self.block_size.get())
        c_value = int(self.C.get())
        
        from backend.SegmentationOperations import SegmentationOperations
        if self.inverse.get():
            result = SegmentationOperations.threshold_adaptive_inverse(
                self.image, method, block_size, c_value
            )
        else:
            result = SegmentationOperations.threshold_adaptive(
                self.image, method, block_size, c_value
            )
        
        if self.on_result_callback:
            self.on_result_callback(result)
        
        self.dialog.destroy()