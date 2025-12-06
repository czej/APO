import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np


class MorphologyDialog:
    """
    Okno dialogowe dla operacji morfologicznych
    """
    def __init__(self, parent, image, app_manager, operation_name):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Morfologia - {operation_name}")
        self.window.geometry("400x450")
        self.window.resizable(False, False)
        
        self.image = image
        self.app_manager = app_manager
        self.operation_name = operation_name
        self.result_image = None
        self.on_result_callback = None
        
        self._create_widgets()
        self._update_preview()
        
    def _create_widgets(self):
        """Tworzy elementy interfejsu"""
        # Frame główny
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        title_label = ttk.Label(
            main_frame,
            text=f"Operacja: {self.operation_name}",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Element strukturalny
        element_frame = ttk.LabelFrame(main_frame, text="Element strukturalny", padding="10")
        element_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Wybór kształtu
        ttk.Label(element_frame, text="Kształt:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.shape_var = tk.StringVar(value='rect')
        shape_combo = ttk.Combobox(
            element_frame,
            textvariable=self.shape_var,
            values=['rect', 'cross', 'ellipse'],
            state='readonly',
            width=15
        )
        shape_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        shape_combo.bind('<<ComboboxSelected>>', lambda e: self._update_preview())
        
        # Opis kształtów
        shapes_info = ttk.Label(
            element_frame,
            text="rect = Prostokąt | cross = Krzyż | ellipse = Elipsa",
            font=("Arial", 8),
            foreground="gray"
        )
        shapes_info.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Rozmiar elementu
        ttk.Label(element_frame, text="Rozmiar:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.size_var = tk.IntVar(value=3)
        size_frame = ttk.Frame(element_frame)
        size_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        self.size_scale = ttk.Scale(
            size_frame,
            from_=3,
            to=9,
            orient=tk.HORIZONTAL,
            variable=self.size_var,
            command=lambda v: self._on_size_change()
        )
        self.size_scale.pack(side=tk.LEFT)
        
        self.size_label = ttk.Label(size_frame, text="3x3")
        self.size_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Liczba iteracji
        iterations_frame = ttk.LabelFrame(main_frame, text="Iteracje", padding="10")
        iterations_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(iterations_frame, text="Liczba iteracji:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.iterations_var = tk.IntVar(value=1)
        iter_frame = ttk.Frame(iterations_frame)
        iter_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        self.iter_scale = ttk.Scale(
            iter_frame,
            from_=1,
            to=5,
            orient=tk.HORIZONTAL,
            variable=self.iterations_var,
            command=lambda v: self._on_iterations_change()
        )
        self.iter_scale.pack(side=tk.LEFT)
        
        self.iter_label = ttk.Label(iter_frame, text="1")
        self.iter_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Podgląd
        preview_frame = ttk.LabelFrame(main_frame, text="Podgląd", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_label = ttk.Label(preview_frame, text="Kliknij 'Podgląd' aby zobaczyć wynik")
        self.preview_label.pack()
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Podgląd",
            command=self._update_preview
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self._on_ok
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _on_size_change(self):
        """Obsługuje zmianę rozmiaru elementu"""
        size = int(self.size_var.get())
        # Zapewniamy nieparzysty rozmiar
        if size % 2 == 0:
            size += 1
            self.size_var.set(size)
        self.size_label.config(text=f"{size}x{size}")
        self._update_preview()
    
    def _on_iterations_change(self):
        """Obsługuje zmianę liczby iteracji"""
        iterations = int(self.iterations_var.get())
        self.iter_label.config(text=str(iterations))
        self._update_preview()
    
    def _update_preview(self):
        """Aktualizuje podgląd wyniku"""
        try:
            shape = self.shape_var.get()
            size = int(self.size_var.get())
            iterations = int(self.iterations_var.get())
            
            # Wykonaj operację
            if self.operation_name == "Erozja":
                self.result_image = self.app_manager.morphology_erosion(
                    self.image, shape, size, iterations
                )
            elif self.operation_name == "Dylacja":
                self.result_image = self.app_manager.morphology_dilation(
                    self.image, shape, size, iterations
                )
            elif self.operation_name == "Otwarcie":
                self.result_image = self.app_manager.morphology_opening(
                    self.image, shape, size, iterations
                )
            elif self.operation_name == "Zamknięcie":
                self.result_image = self.app_manager.morphology_closing(
                    self.image, shape, size, iterations
                )
            
            # Aktualizuj podgląd
            shape_names = {'rect': 'Prostokąt', 'cross': 'Krzyż', 'ellipse': 'Elipsa'}
            info_text = (
                f"Element: {shape_names[shape]} {size}x{size}\n"
                f"Iteracje: {iterations}\n"
                f"Kliknij OK aby zastosować"
            )
            self.preview_label.config(text=info_text)
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas podglądu: {str(e)}")
    
    def _on_ok(self):
        """Zatwierdza operację i przekazuje wynik"""
        if self.result_image is not None and self.on_result_callback:
            self.on_result_callback(self.result_image)
        self.window.destroy()


class SkeletonizationDialog:
    """
    Okno dialogowe dla szkieletyzacji
    """
    def __init__(self, parent, image, app_manager):
        self.window = tk.Toplevel(parent)
        self.window.title("Szkieletyzacja")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        
        self.image = image
        self.app_manager = app_manager
        self.result_image = None
        self.on_result_callback = None
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Tworzy elementy interfejsu"""
        # Frame główny
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        title_label = ttk.Label(
            main_frame,
            text="Szkieletyzacja obiektu binarnego",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Informacja
        info_frame = ttk.LabelFrame(main_frame, text="Informacja", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        info_text = (
            "Szkieletyzacja redukuje obiekt binarny do linii środkowej "
            "(szkieletu) zachowując topologię obiektu.\n\n"
            "Algorytm: Zgodny z wykładem\n"
            "- Iteracyjne ścienianie z 8 kierunkami\n"
            "- Elementy strukturalne: 0°, 90°, 180°, 270° + przekątne\n\n"
            "⚠️ WAŻNE:\n"
            "• Obraz musi być binarny (czarno-biały)\n"
            "• Obiekty BIAŁE (255) na CZARNYM tle (0)\n"
            "• Im czystszy obraz, tym lepszy szkielet"
        )
        info_label = ttk.Label(info_frame, text=info_text, wraplength=350, justify=tk.LEFT)
        info_label.pack()
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Podgląd",
            command=self._update_preview
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self._on_ok
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(
            main_frame,
            text="Kliknij 'Podgląd' lub 'OK' aby wykonać szkieletyzację",
            foreground="gray"
        )
        self.status_label.pack(pady=(10, 0))
    
    def _update_preview(self):
        """Wykonuje szkieletyzację i wyświetla podgląd"""
        try:
            self.status_label.config(text="Wykonywanie szkieletyzacji...", foreground="blue")
            self.window.update()
            
            self.result_image = self.app_manager.morphology_skeletonization(self.image)
            
            self.status_label.config(
                text="Szkieletyzacja zakończona. Kliknij OK aby zastosować.",
                foreground="green"
            )
            
        except Exception as e:
            self.status_label.config(text=f"Błąd: {str(e)}", foreground="red")
            messagebox.showerror("Błąd", f"Błąd podczas szkieletyzacji: {str(e)}")
    
    def _on_ok(self):
        """Zatwierdza operację i przekazuje wynik"""
        if self.result_image is None:
            # Jeśli nie było podglądu, wykonaj operację
            self._update_preview()
        
        if self.result_image is not None and self.on_result_callback:
            self.on_result_callback(self.result_image)
        self.window.destroy()