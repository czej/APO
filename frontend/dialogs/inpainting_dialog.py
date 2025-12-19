import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk


class InpaintingDialog:
    """Dialog do przeprowadzania operacji Inpainting."""
    
    def __init__(self, parent, image, app_manager=None):
        self.parent = parent
        self.original_image = image.copy()
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
        
    def _apply_inpainting(self, image, mask, method='telea', radius=3):
        """Aplikuje inpainting bezpośrednio przez CV2"""
        if image is None:
            raise ValueError("Brak obrazu wejściowego")
        
        if mask is None:
            raise ValueError("Brak maski")
        
        if image.shape[:2] != mask.shape[:2]:
            raise ValueError(f"Rozmiary obrazu {image.shape[:2]} i maski {mask.shape[:2]} się różnią")
        
        # Konwersja maski
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        
        if mask.dtype != np.uint8:
            mask = mask.astype(np.uint8)
        
        # Binaryzacja
        _, mask_binary = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
        
        # Wybór metody
        flag = cv2.INPAINT_TELEA if method.lower() == 'telea' else cv2.INPAINT_NS
        
        # Ograniczenie radius
        radius = max(1, min(20, int(radius)))
        
        # Aplikacja inpainting
        result = cv2.inpaint(image, mask_binary, radius, flag)
        
        return result
        
    def _create_widgets(self):
        """Tworzy interfejs użytkownika"""
        
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ===== KONTROLKI =====
        control_frame = ttk.LabelFrame(main_frame, text="Ustawienia", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        row = 0
        
        # Tworzenie maski
        ttk.Label(control_frame, text="TWORZENIE MASKI", 
                  font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=(0,10))
        row += 1
        
        ttk.Button(control_frame, text="Załaduj maskę z pliku", 
                   command=self._load_mask).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        ttk.Button(control_frame, text="Wyczyść maskę", 
                   command=self._clear_mask).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Progowanie
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
        
        # Rysowanie
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
        
        # Parametry inpainting
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
        
        # Przyciski akcji
        ttk.Button(control_frame, text="Podgląd", 
                   command=self._update_preview).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        ttk.Button(control_frame, text="Zastosuj i zamknij", 
                   command=self._apply_and_close).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        ttk.Button(control_frame, text="Anuluj", 
                   command=self.window.destroy).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        row += 1
        
        # ===== PODGLĄDY =====
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        ttk.Label(preview_frame, text="Oryginalny obraz + Maska (rysuj tutaj)", 
                  font=('Arial', 10, 'bold')).pack()
        
        self.canvas_original = tk.Canvas(preview_frame, width=400, height=300, bg='gray')
        self.canvas_original.pack(pady=5)
        
        # Eventy rysowania
        self.canvas_original.bind("<Button-1>", self._start_draw)
        self.canvas_original.bind("<B1-Motion>", self._draw)
        self.canvas_original.bind("<ButtonRelease-1>", self._stop_draw)
        
        ttk.Label(preview_frame, text="Wynik Inpainting", 
                  font=('Arial', 10, 'bold')).pack()
        
        self.canvas_result = tk.Canvas(preview_frame, width=400, height=300, bg='gray')
        self.canvas_result.pack(pady=5)
        
    def _update_threshold_label(self):
        self.lower_threshold_label.config(text=str(self.lower_threshold_var.get()))
        self.upper_threshold_label.config(text=str(self.upper_threshold_var.get()))
        
    def _update_radius_label(self):
        self.radius_label.config(text=str(self.radius_var.get()))
        
    def _update_brush_label(self):
        self.brush_label.config(text=f"{self.brush_size_var.get()} px")
        
    def _load_mask(self):
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
        self.mask = np.zeros(self.original_image.shape[:2], dtype=np.uint8)
        self._update_preview()
        
    def _create_mask_from_threshold(self):
        lower = self.lower_threshold_var.get()
        upper = self.upper_threshold_var.get()
        
        if lower > upper:
            messagebox.showerror("Błąd", "Dolny próg nie może być większy niż górny")
            return
        
        if len(self.original_image.shape) == 3:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.original_image
            
        self.mask = cv2.inRange(gray, lower, upper)
        self._update_preview()
        messagebox.showinfo("Sukces", "Maska utworzona z progowania")
        
    def _start_draw(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        
    def _draw(self, event):
        if not self.drawing:
            return
            
        x, y = event.x, event.y
        
        # Pobierz rzeczywiste wymiary canvas
        canvas_width = self.canvas_original.winfo_width()
        canvas_height = self.canvas_original.winfo_height()
        
        # Pobierz wymiary wyświetlanego obrazu (po thumbnail)
        img_height, img_width = self.mask.shape
        
        # Oblicz skalę wyświetlanego obrazu
        scale = min(canvas_width / img_width, canvas_height / img_height)
        display_width = int(img_width * scale)
        display_height = int(img_height * scale)
        
        # Oblicz offset (obraz jest wyśrodkowany)
        offset_x = (canvas_width - display_width) // 2
        offset_y = (canvas_height - display_height) // 2
        
        # Przekształć współrzędne z canvas do współrzędnych obrazu
        img_x = int((x - offset_x) / scale)
        img_y = int((y - offset_y) / scale)
        
        # Sprawdź czy kliknięcie jest w obrazie
        if img_x < 0 or img_y < 0 or img_x >= img_width or img_y >= img_height:
            return
        
        if self.last_x is not None and self.last_y is not None:
            last_img_x = int((self.last_x - offset_x) / scale)
            last_img_y = int((self.last_y - offset_y) / scale)
            
            brush_size = self.brush_size_var.get()
            cv2.line(self.mask, (last_img_x, last_img_y), (img_x, img_y), 
                    255, thickness=brush_size)
        
        self.last_x = x
        self.last_y = y
        
        self._update_preview()
        
    def _stop_draw(self, event):
        self.drawing = False
        self.last_x = None
        self.last_y = None
        
    def _update_preview(self):
        # Oryginalny + maska
        if len(self.original_image.shape) == 3:
            overlay = self.original_image.copy()
        else:
            overlay = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2BGR)
        
        mask_colored = np.zeros_like(overlay)
        mask_colored[:, :, 2] = self.mask
        overlay = cv2.addWeighted(overlay, 0.7, mask_colored, 0.3, 0)
        
        self._display_image(overlay, self.canvas_original)
        
        # Wynik inpainting
        if np.any(self.mask > 0):
            try:
                result = self._apply_inpainting(
                    self.original_image,
                    self.mask,
                    method=self.method_var.get(),
                    radius=self.radius_var.get()
                )
                self.result_image = result
                self._display_image(result, self.canvas_result)
            except Exception as e:
                self.result_image = None
                self._display_image(self.original_image, self.canvas_result)
        else:
            self.result_image = self.original_image.copy()
            self._display_image(self.original_image, self.canvas_result)
            
    def _display_image(self, img, canvas):
        if len(img.shape) == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img
        
        # Użyj stałych wymiarów zamiast winfo (które zwracają 1 przed renderowaniem)
        canvas_width = 400
        canvas_height = 300
        
        img_pil = Image.fromarray(img_rgb)
        img_pil.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_pil)
        canvas.delete("all")
        canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor=tk.CENTER)
        canvas.image = photo
                
    def _apply_and_close(self):
        if not np.any(self.mask > 0):
            messagebox.showwarning("Ostrzeżenie", "Maska jest pusta. Utwórz maskę przed zastosowaniem.")
            return
        
        try:
            result = self._apply_inpainting(
                self.original_image,
                self.mask,
                method=self.method_var.get(),
                radius=self.radius_var.get()
            )
            if self.on_result_callback:
                self.on_result_callback(result)
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zastosować inpainting: {str(e)}")