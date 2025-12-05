import tkinter as tk
from PIL import Image, ImageTk
import cv2


class PosterizeDialog(tk.Toplevel):
    """Dialog do posteryzacji (redukcji poziomów szarości)"""
    
    def __init__(self, parent, img, app_manager):
        """
        Parametry:
            parent: okno rodzica
            img: obraz numpy.ndarray (grayscale)
            app_manager: instancja AppManager
        """
        super().__init__(parent)
        
        self.img = img
        self.app_manager = app_manager
        self.on_result_callback = None
        
        self.title("Posterize")
        self.geometry("600x550")
        
        self._create_ui()
        
    def _create_ui(self):
        """Tworzy interfejs dialogu"""
        # Nagłówek
        header_frame = tk.Frame(self, bg="#f0f0f0", height=60)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Posteryzacja - Redukcja poziomów szarości",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        tk.Label(
            header_frame,
            text="Zmniejsz liczbę poziomów szarości w obrazie",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666"
        ).pack()
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Levels input
        levels_frame = tk.Frame(content_frame)
        levels_frame.pack(pady=20)
        
        tk.Label(
            levels_frame,
            text="Liczba poziomów szarości (2-256):",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        self.levels_var = tk.IntVar(value=8)
        
        spinbox = tk.Spinbox(
            levels_frame,
            from_=2,
            to=256,
            textvariable=self.levels_var,
            width=10,
            font=("Arial", 10),
            command=self._update_info
        )
        spinbox.pack(side=tk.LEFT)
        
        # Slider jako alternatywa
        slider_frame = tk.Frame(content_frame)
        slider_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(
            slider_frame,
            text="Szybki wybór:",
            font=("Arial", 9)
        ).pack(anchor="w")
        
        slider = tk.Scale(
            slider_frame,
            from_=2,
            to=256,
            orient=tk.HORIZONTAL,
            variable=self.levels_var,
            command=lambda v: self._update_info(),
            showvalue=False
        )
        slider.pack(fill=tk.X, pady=5)
        
        # Common presets
        presets_frame = tk.Frame(content_frame)
        presets_frame.pack(pady=10)
        
        tk.Label(
            presets_frame,
            text="Presety:",
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        for preset in [2, 4, 8, 16, 32, 64, 128]:
            tk.Button(
                presets_frame,
                text=str(preset),
                command=lambda p=preset: self._set_preset(p),
                width=4
            ).pack(side=tk.LEFT, padx=2)
        
        # Info label
        self.info_label = tk.Label(
            content_frame,
            text="",
            font=("Arial", 9),
            fg="#666",
            justify=tk.LEFT
        )
        self.info_label.pack(pady=15, anchor="w")
        self._update_info()
        
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
        
    def _set_preset(self, value):
        """Ustawia wartość z presetu"""
        self.levels_var.set(value)
        self._update_info()
            
    def _update_info(self):
        """Aktualizuje informacje o posteryzacji"""
        levels = self.levels_var.get()
        bits = levels.bit_length() - 1
        
        info = (
            f"Wybrano: {levels} poziomów\n"
            f"Odpowiednik ~{bits}-bitowej kwantyzacji\n"
            f"Rozmiar kroku: {256 // levels} wartości na poziom"
        )
        self.info_label.config(text=info)
            
    def _apply(self):
        """Zastosuj posteryzację"""
        try:
            levels = self.levels_var.get()
            result = self.app_manager.apply_posterize(self.img, levels)
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.destroy()
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Błąd", str(e))