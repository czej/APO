import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk


class InpaintingDialog:
    """
    Dialog do przeprowadzania operacji Inpainting.
    Umożliwia:
    - Załadowanie maski z pliku
    - Utworzenie maski przez progowanie
    - Rysowanie maski ręcznie
    - Wybór metody inpainting (Telea/Navier-Stokes)
    - Podgląd w czasie rzeczywistym
    """
    
    def __init__(self, parent, image, app_manager):
        self.parent = parent
        self.original_image = image.copy()
        self.app_manager = app_manager
        self.mask = np.zeros(image.shape[:2], dtype=np.uint8)
        self.result_image = None
        self.on_result_callback = None
        
        # Zmienne dla rysowania
        self.drawing = False
        self.brush_size = 10
        self.last_x = None
        self.last_y = None
        
        # Tworzenie okna
        self.window = tk.Toplevel(parent)
        self.window.title("Inpainting")
        self.window.geometry("1100x700")
        
        self._create_widgets()
        self._update_preview()
        
    def _create_widgets(self):
        """Tworzy interfejs użytkownika"""
        
        # Główny kontener
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ===== LEWA STRONA - KONTROLKI =====
        control_frame = ttk.LabelFrame(main_frame, text="Ustawienia", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        row = 0
        
        # --- Sekcja: Maska ---
        ttk.Label(control_frame, text="TWORZENIE MASKI", 
                  font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(0,10))
        row += 1
        
        # Przycisk: Załaduj maskę
        ttk.Button(control_frame, text="Załaduj maskę z pliku", 
                   command=self._load_mask).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        # Przycisk: Wyczyść maskę
        ttk.Button(control_frame, text="Wyczyść maskę", 
                   command=self._clear_mask).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # --- Sekcja: Progowanie ---
        ttk.Label(control_frame, text="MASKA Z PROGOWANIA", 
                  font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(0,10))
        row += 1
        
        ttk.Label(control_frame, text="Dolny próg:").grid(row=row, column=0, sticky=tk.W)
        self.lower_threshold_var = tk.IntVar(value=0)
        ttk.Scale(control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                  variable=self.lower_threshold_var, command=lambda x: self._update_threshold_label()
                  ).grid(row=row, column=1, sticky=(tk.W, tk.E))
        row += 1
        
        self.lower_threshold_label = ttk.Label(control_frame, text="0")
        self.lower_threshold_label.grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        ttk.Label(control_frame, text="Górny próg:").grid(row=row, column=0, sticky=tk.W)
        self.upper_threshold_var = tk.IntVar(value=255)
        ttk.Scale(control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                  variable=self.upper_threshold_var, command=lambda x: self._update_threshold_label()
                  ).grid(row=row, column=1, sticky=(tk.W, tk.E))
        row += 1
        
        self.upper_threshold_label = ttk.Label(control_frame, text="255")
        self.upper_threshold_label.grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        ttk.Button(control_frame, text="Utwórz maskę z progowania", 
                   command=self._create_mask_from_threshold).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # --- Sekcja: Rysowanie ---
        ttk.Label(control_frame, text="RYSOWANIE MASKI", 
                  font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(0,10))
        row += 1
        
        ttk.Label(control_frame, text="Rozmiar pędzla:").grid(row=row, column=0, sticky=tk.W)
        self.brush_size_var = tk.IntVar(value=10)
        ttk.Scale(control_frame, from_=1, to=50, orient=tk.HORIZONTAL,
                  variable=self.brush_size_var, command=lambda x: self._update_brush_label()
                  ).grid(row=row, column=1, sticky=(tk.W, tk.E))
        row += 1
        
        self.brush_label = ttk.Label(control_frame, text="10 px")
        self.brush_label.grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        ttk.Label(control_frame, text="Rysuj na obrazku po prawej →", 
                  foreground="blue").grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # --- Sekcja: Inpainting ---
        ttk.Label(control_frame, text="PARAMETRY INPAINTING", 
                  font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(0,10))
        row += 1
        
        ttk.Label(control_frame, text="Metoda:").grid(row=row, column=0, sticky=tk.W)
        self.method_var = tk.StringVar(value="telea")
        method_combo = ttk.Combobox(control_frame, textvariable=self.method_var, 
                                     values=["telea", "ns"], state="readonly", width=15)
        method_combo.grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        ttk.Label(control_frame, text="Promień:").grid(row=row, column=0, sticky=tk.W)
        self.radius_var = tk.IntVar(value=3)
        ttk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                  variable=self.radius_var, command=lambda x: self._update_radius_label()
                  ).grid(row=row, column=1, sticky=(tk.W, tk.E))
        row += 1
        
        self.radius_label = ttk.Label(control_frame, text="3")
        self.radius_label.grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # --- Przyciski akcji ---
        ttk.Button(control_frame, text="Podgląd", 
                   command=self._update_preview).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        ttk.Button(control_frame, text="Zastosuj i zamknij", 
                   command=self._apply_and_close).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        ttk.Button(control_frame, text="Anuluj", 
                   command=self.window.destroy).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        # ===== PRAWA STRONA - PODGLĄDY =====
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Canvas dla oryginału z maską
        ttk.Label(preview_frame, text="Oryginalny obraz + Maska (rysuj tutaj)", 
                  font=('Arial', 10, 'bold')).pack()
        
        self.canvas_original = tk.Canvas(preview_frame, width=400, height=300, bg='gray')
        self.canvas_original.pack(pady=5)
        
        # Podpięcie eventów rysowania
        self.canvas_original.bind("<Button-1>", self._start_draw)
        self.canvas_original.bind("<B1-Motion>", self._draw)
        self.canvas_original.bind("<ButtonRelease-1>", self._stop_draw)
        
        # Canvas dla wyniku
        ttk.Label(preview_frame, text="Wynik Inpainting", 
                  font=('Arial', 10, 'bold')).pack()
        
        self.canvas_result = tk.Canvas(preview_frame, width=400, height=300, bg='gray')
        self.canvas_result.pack(pady=5)
        
    def _update_threshold_label(self):
        """Aktualizuje etykiety progów"""
        self.lower_threshold_label.config(text=str(self.lower_threshold_var.get()))
        self.upper_threshold_label.config(text=str(self.upper_threshold_var.get()))
        
    def _update_radius_label(self):
        """Aktualizuje etykietę promienia"""
        self.radius_label.config(text=str(self.radius_var.get()))
        
    def _update_brush_label(self):
        """Aktualizuje etykietę rozmiaru pędzla"""
        self.brush_label.config(text=f"{self.brush_size_var.get()} px")
        
    def _load_mask(self):
        """Ładuje maskę z pliku"""
        filename = filedialog.askopenfilename(
            title="Wybierz plik maski",
            filetypes=[("Image files", "*.png *.jpg *.bmp *.tif"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                loaded_mask = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
                if loaded_mask.shape != self.original_image.shape[:2]:
                    messagebox.showerror("Błąd", 
                        f"Rozmiar maski {loaded_mask.shape} nie pasuje do obrazu {self.original_image.shape[:2]}")
                    return
                
                self.mask = loaded_mask
                self._update_preview()
                messagebox.showinfo("Sukces", "Maska załadowana")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można załadować maski: {str(e)}")
                
    def _clear_mask(self):
        """Czyści maskę"""
        self.mask = np.zeros(self.original_image.shape[:2], dtype=np.uint8)
        self._update_preview()
        
    def _create_mask_from_threshold(self):
        """Tworzy maskę na podstawie progowania"""
        lower = self.lower_threshold_var.get()
        upper = self.upper_threshold_var.get()
        
        if lower > upper:
            messagebox.showerror("Błąd", "Dolny próg nie może być większy niż górny")
            return
        
        # Jeśli obraz jest kolorowy, konwertuj do skali szarości
        if len(self.original_image.shape) == 3:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.original_image
            
        self.mask = cv2.inRange(gray, lower, upper)
        self._update_preview()
        messagebox.showinfo("Sukces", "Maska utworzona z progowania")
        
    def _start_draw(self, event):
        """Rozpoczyna rysowanie"""
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        
    def _draw(self, event):
        """Rysuje na masce"""
        if not self.drawing:
            return
            
        x, y = event.x, event.y
        
        # Skalowanie współrzędnych z canvas do rozmiaru obrazu
        canvas_width = self.canvas_original.winfo_width()
        canvas_height = self.canvas_original.winfo_height()
        img_height, img_width = self.mask.shape
        
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height
        
        img_x = int(x * scale_x)
        img_y = int(y * scale_y)
        
        if self.last_x is not None and self.last_y is not None:
            last_img_x = int(self.last_x * scale_x)
            last_img_y = int(self.last_y * scale_y)
            
            # Rysuj linię na masce
            brush_size = self.brush_size_var.get()
            cv2.line(self.mask, (last_img_x, last_img_y), (img_x, img_y), 
                     255, thickness=brush_size)
        
        self.last_x = x
        self.last_y = y
        
        self._update_preview()
        
    def _stop_draw(self, event):
        """Kończy rysowanie"""
        self.drawing = False
        self.last_x = None
        self.last_y = None
        
    def _update_preview(self):
        """Aktualizuje podgląd"""
        # Podgląd oryginału z maską
        if len(self.original_image.shape) == 3:
            overlay = self.original_image.copy()
        else:
            overlay = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2BGR)
        
        # Nakładka maski (czerwony kolor)
        mask_colored = np.zeros_like(overlay)
        mask_colored[:, :, 2] = self.mask  # Czerwony kanał
        overlay = cv2.addWeighted(overlay, 0.7, mask_colored, 0.3, 0)
        
        self._display_image(overlay, self.canvas_original)
        
        # Podgląd wyniku inpainting
        try:
            result = self.app_manager.inpainting_operations.apply_inpainting(
                self.original_image,
                self.mask,
                method=self.method_var.get(),
                radius=self.radius_var.get()
            )
            self.result_image = result
            self._display_image(result, self.canvas_result)
        except Exception as e:
            # Jeśli błąd, wyświetl oryginalny obraz
            self._display_image(self.original_image, self.canvas_result)
            
    def _display_image(self, img, canvas):
        """Wyświetla obraz na canvas"""
        # Konwersja BGR -> RGB jeśli kolorowy
        if len(img.shape) == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img
        
        # Skalowanie do rozmiaru canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            img_pil = Image.fromarray(img_rgb)
            img_pil.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img_pil)
            canvas.delete("all")
            canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor=tk.CENTER)
            canvas.image = photo  # Zapobieganie garbage collection
            
    def _apply_and_close(self):
        """Aplikuje operację i zamyka okno"""
        if self.result_image is not None:
            if self.on_result_callback:
                self.on_result_callback(self.result_image)
            self.window.destroy()
        else:
            messagebox.showerror("Błąd", "Brak wyniku do zastosowania")