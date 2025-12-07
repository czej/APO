"""
Dialogi dla operacji histogramu - LAB3 Zadanie 1
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
import numpy as np


class StretchHistogramDialog:
    """Dialog dla rozciągania histogramu w zadanym zakresie"""
    
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
        self.dialog.title("Rozciąganie histogramu")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        
        # Zmienne - domyślnie znajdź min/max w obrazie
        hist_stats = self.app_manager.calculate_histograms(self.image)
        histogram = hist_stats[0].histogram
        
        # Znajdź rzeczywisty zakres wartości w obrazie (z marginesem 1%)
        cumsum = np.cumsum(histogram)
        total = cumsum[-1]
        p1_auto = np.argmax(cumsum > total * 0.01)  # 1% percentyl
        p2_auto = np.argmax(cumsum > total * 0.99)  # 99% percentyl
        
        self.p1 = tk.IntVar(value=p1_auto)
        self.p2 = tk.IntVar(value=p2_auto)
        self.q1 = tk.IntVar(value=0)
        self.q2 = tk.IntVar(value=255)
        self.preview_enabled = tk.BooleanVar(value=False)
        
        # Timer do debouncing
        self._update_timer = None
        
        self._create_widgets()
        self._update_histograms()  # Pokaż początkowe histogramy
        
    def _create_widgets(self):
        """Tworzy widgety dialogu"""
        # Główna ramka z histogramami
        hist_main_frame = tk.Frame(self.dialog)
        hist_main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Histogram PRZED
        hist_before_frame = tk.Frame(hist_main_frame)
        hist_before_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            hist_before_frame, 
            text="Histogram PRZED", 
            font=("Arial", 11, "bold")
        ).pack()
        
        self.fig_before = Figure(figsize=(4, 3))
        self.ax_before = self.fig_before.add_subplot(111)
        self.canvas_before = FigureCanvasTkAgg(self.fig_before, master=hist_before_frame)
        self.canvas_before.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Histogram PO
        hist_after_frame = tk.Frame(hist_main_frame)
        hist_after_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            hist_after_frame,
            text="Histogram PO",
            font=("Arial", 11, "bold")
        ).pack()
        
        self.fig_after = Figure(figsize=(4, 3))
        self.ax_after = self.fig_after.add_subplot(111)
        self.canvas_after = FigureCanvasTkAgg(self.fig_after, master=hist_after_frame)
        self.canvas_after.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Ramka informacyjna
        info_frame = ttk.LabelFrame(self.dialog, text="Informacje", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = (
            "Rozciąganie histogramu - transformacja liniowa:\n"
            "• Zakres źródłowy [p1, p2] → Zakres docelowy [q1, q2]\n"
            "• Wzór: output = (input - p1) × (q2 - q1) / (p2 - p1) + q1"
        )
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Ramka parametrów
        params_frame = ttk.LabelFrame(self.dialog, text="Parametry", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Zakres źródłowy
        ttk.Label(
            params_frame, 
            text="Zakres źródłowy (obraz wejściowy):",
            font=("Arial", 10, "bold")
        ).pack(pady=(0, 5))
        
        # p1
        p1_frame = ttk.Frame(params_frame)
        p1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(p1_frame, text="p1 (dolny):", width=15).pack(side=tk.LEFT)
        p1_scale = ttk.Scale(
            p1_frame, from_=0, to=255, variable=self.p1,
            orient=tk.HORIZONTAL, command=lambda v: self._on_param_change()
        )
        p1_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.p1_label = ttk.Label(p1_frame, text=str(self.p1.get()), width=5)
        self.p1_label.pack(side=tk.LEFT)
        
        # p2
        p2_frame = ttk.Frame(params_frame)
        p2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(p2_frame, text="p2 (górny):", width=15).pack(side=tk.LEFT)
        p2_scale = ttk.Scale(
            p2_frame, from_=0, to=255, variable=self.p2,
            orient=tk.HORIZONTAL, command=lambda v: self._on_param_change()
        )
        p2_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.p2_label = ttk.Label(p2_frame, text=str(self.p2.get()), width=5)
        self.p2_label.pack(side=tk.LEFT)
        
        ttk.Separator(params_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Zakres docelowy
        ttk.Label(
            params_frame,
            text="Zakres docelowy (obraz wyjściowy):",
            font=("Arial", 10, "bold")
        ).pack(pady=(0, 5))
        
        # q1
        q1_frame = ttk.Frame(params_frame)
        q1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(q1_frame, text="q1 (dolny):", width=15).pack(side=tk.LEFT)
        q1_scale = ttk.Scale(
            q1_frame, from_=0, to=255, variable=self.q1,
            orient=tk.HORIZONTAL, command=lambda v: self._on_param_change()
        )
        q1_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.q1_label = ttk.Label(q1_frame, text=str(self.q1.get()), width=5)
        self.q1_label.pack(side=tk.LEFT)
        
        # q2
        q2_frame = ttk.Frame(params_frame)
        q2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(q2_frame, text="q2 (górny):", width=15).pack(side=tk.LEFT)
        q2_scale = ttk.Scale(
            q2_frame, from_=0, to=255, variable=self.q2,
            orient=tk.HORIZONTAL, command=lambda v: self._on_param_change()
        )
        q2_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.q2_label = ttk.Label(q2_frame, text=str(self.q2.get()), width=5)
        self.q2_label.pack(side=tk.LEFT)
        
        ttk.Separator(params_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Podgląd na żywo
        ttk.Checkbutton(
            params_frame,
            text="Podgląd obrazu",
            variable=self.preview_enabled,
            command=self._update_preview
        ).pack(pady=5)
        
        # Informacja o błędzie
        self.error_label = ttk.Label(
            params_frame, 
            text="", 
            foreground="red",
            font=("Arial", 9)
        )
        self.error_label.pack(pady=5)
        
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
        
    def _update_histograms(self):
        """Aktualizuje oba histogramy"""
        p1 = int(self.p1.get())
        p2 = int(self.p2.get())
        q1 = int(self.q1.get())
        q2 = int(self.q2.get())
        
        # Histogram PRZED
        hist_before = self.app_manager.calculate_histograms(self.image)
        histogram_before = hist_before[0].histogram
        
        self.ax_before.clear()
        x = np.arange(256)
        self.ax_before.bar(x, histogram_before, color='gray', width=1.0, alpha=0.7, edgecolor='none')
        
        # Zaznacz zakres [p1, p2] na histogramie przed
        self.ax_before.axvline(p1, color='red', linestyle='--', linewidth=2, label=f'p1={p1}')
        self.ax_before.axvline(p2, color='blue', linestyle='--', linewidth=2, label=f'p2={p2}')
        
        self.ax_before.set_title("PRZED rozciąganiem")
        self.ax_before.set_xlabel("Wartość piksela")
        self.ax_before.set_ylabel("Częstość")
        self.ax_before.set_xlim(0, 255)
        self.ax_before.legend(fontsize=8)
        self.ax_before.grid(True, alpha=0.3)
        
        # Zapamiętaj skalę Y z histogramu PRZED
        y_max_before = histogram_before.max() * 1.1 if histogram_before.max() > 0 else 10000
        self.ax_before.set_ylim(0, y_max_before)
        
        self.canvas_before.draw()
        
        # Histogram PO (jeśli parametry są poprawne)
        if p1 < p2 and q1 < q2:
            from backend.HistogramOperations import HistogramOperations
            try:
                result = HistogramOperations.stretch_histogram_range(
                    self.image, p1, p2, q1, q2
                )
                
                hist_after = self.app_manager.calculate_histograms(result)
                histogram_after = hist_after[0].histogram
                
                self.ax_after.clear()
                self.ax_after.bar(x, histogram_after, color='green', width=1.0, alpha=0.7, edgecolor='none')
                
                # Zaznacz zakres [q1, q2] na histogramie po
                self.ax_after.axvline(q1, color='red', linestyle='--', linewidth=2, label=f'q1={q1}')
                self.ax_after.axvline(q2, color='blue', linestyle='--', linewidth=2, label=f'q2={q2}')
                
                self.ax_after.set_title("PO rozciągnięciu")
                self.ax_after.set_xlabel("Wartość piksela")
                self.ax_after.set_ylabel("Częstość")
                self.ax_after.set_xlim(0, 255)
                
                # Użyj TEJ SAMEJ skali Y co histogram PRZED
                self.ax_after.set_ylim(0, y_max_before)
                
                # Napraw formatowanie osi Y
                self.ax_after.ticklabel_format(style='plain', axis='y')
                
                self.ax_after.legend(fontsize=8)
                self.ax_after.grid(True, alpha=0.3)
                
                self.canvas_after.draw()
                
                self.result = result
            except Exception as e:
                self.error_label.config(text=f"Błąd: {str(e)}")
    
    def _on_param_change(self):
        """Wywoływane gdy zmienią się parametry"""
        p1 = int(self.p1.get())
        p2 = int(self.p2.get())
        q1 = int(self.q1.get())
        q2 = int(self.q2.get())
        
        self.p1_label.config(text=str(p1))
        self.p2_label.config(text=str(p2))
        self.q1_label.config(text=str(q1))
        self.q2_label.config(text=str(q2))
        
        # Walidacja
        error_msg = ""
        if p1 >= p2:
            error_msg = "Błąd: p1 musi być < p2"
        elif q1 >= q2:
            error_msg = "Błąd: q1 musi być < q2"
        
        self.error_label.config(text=error_msg)
        
        # Anuluj poprzedni timer
        if self._update_timer is not None:
            self.dialog.after_cancel(self._update_timer)
        
        # Zaplanuj aktualizację za 300ms (debouncing)
        self._update_timer = self.dialog.after(300, self._delayed_update)
    
    def _delayed_update(self):
        """Wykonuje aktualizację po debouncing"""
        self._update_timer = None
        
        p1 = int(self.p1.get())
        p2 = int(self.p2.get())
        q1 = int(self.q1.get())
        q2 = int(self.q2.get())
        
        # Walidacja
        if p1 >= p2 or q1 >= q2:
            return
        
        # Aktualizuj histogramy
        self._update_histograms()
        
        # Podgląd obrazu jeśli włączony
        if self.preview_enabled.get():
            self._update_preview()
    
    def _update_preview(self):
        """Aktualizuje podgląd obrazu"""
        if not self.preview_enabled.get():
            if hasattr(self, 'preview_window') and self.preview_window.winfo_exists():
                self.preview_window.destroy()
            return
        
        # Wynik już jest obliczony w self.result przez _update_histograms
        if self.result is not None:
            self._show_preview_window(self.result)
    
    def _show_preview_window(self, result):
        """Pokazuje podgląd w osobnym oknie"""
        if not hasattr(self, 'preview_window') or not self.preview_window.winfo_exists():
            from PIL import Image, ImageTk
            import cv2
            
            self.preview_window = tk.Toplevel(self.dialog)
            self.preview_window.title("Podgląd")
            self.preview_window.attributes('-topmost', True)
            
            self.preview_label = tk.Label(self.preview_window, bg='#2b2b2b')
            self.preview_label.pack()
        
        from PIL import Image, ImageTk
        import cv2
        
        h, w = result.shape[:2]
        max_size = 600
        
        scale = min(max_size / w, max_size / h)
        
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            display = cv2.resize(result, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        else:
            display = result
        
        self.preview_window.geometry(f"{display.shape[1]}x{display.shape[0]}")
        
        img_pil = Image.fromarray(display)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        self.preview_label.config(image=img_tk)
        self.preview_label.image = img_tk
    
    def _apply(self):
        """Aplikuje operację i zamyka dialog"""
        p1 = int(self.p1.get())
        p2 = int(self.p2.get())
        q1 = int(self.q1.get())
        q2 = int(self.q2.get())
        
        # Walidacja
        if p1 >= p2:
            messagebox.showerror("Błąd", "p1 musi być mniejsze od p2")
            return
        if q1 >= q2:
            messagebox.showerror("Błąd", "q1 musi być mniejsze od q2")
            return
        
        from backend.HistogramOperations import HistogramOperations
        try:
            result = HistogramOperations.stretch_histogram_range(
                self.image, p1, p2, q1, q2
            )
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))