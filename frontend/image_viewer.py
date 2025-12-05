import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np


class ImageViewer:
    """Okno do wyświetlania pojedynczego obrazu"""
    
    def __init__(self, parent, img, title="Image", scale='fit'):
        """
        Parametry:
            parent: rodzic (root lub Toplevel)
            img: obraz numpy.ndarray (BGR lub Grayscale)
            title: tytuł okna
            scale: 'fit', 'original', 'fullscreen'
        """
        self.parent = parent
        self.original_img = img
        self.title = title
        self.scale = scale
        self.on_focus_callback = None  # Callback wywoływany gdy okno otrzyma focus
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        
        # Bind focus event
        self.window.bind("<FocusIn>", self._on_focus)
        self.window.bind("<Configure>", self._on_resize)
        
        self._display_image()
        
        # Menu kontekstowe
        self._create_context_menu()
        
    def _display_image(self):
        """Wyświetla obraz w oknie"""
        img = self.original_img.copy()
        
        # Konwersja do RGB dla PIL
        if len(img.shape) == 2:
            # Grayscale
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 3:
            # BGR -> RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img
        
        # Skalowanie
        if self.scale == 'fit':
            # Dopasuj do rozmiaru 800x600
            img_rgb = self._resize_keep_aspect(img_rgb, 800, 600)
            # Ustaw rozmiar bez marginesów
            img_h, img_w = img_rgb.shape[:2]
            self.window.geometry(f"{img_w}x{img_h + 25}")
            # Wyłącz padding okna
            self.window.configure(padx=0, pady=0)
        elif self.scale == 'fullscreen':
            screen_w = self.parent.winfo_screenwidth()
            screen_h = self.parent.winfo_screenheight()
            img_rgb = cv2.resize(img_rgb, (screen_w, screen_h))
            self.window.attributes('-fullscreen', True)
            self.window.bind("<Escape>", lambda e: self._exit_fullscreen())
        elif self.scale == 'original':
            # Bez zmian rozmiaru
            pass
        
        # Konwersja do PhotoImage
        img_pil = Image.fromarray(img_rgb)
        self.photo_image = ImageTk.PhotoImage(img_pil)
        
       # Frame bez paddingu
        container = tk.Frame(self.window, bg='#e0e0e0')
        container.pack(fill=tk.BOTH, expand=True)
        container.pack_propagate(False)

        # Label z obrazem - bez żadnych marginesów
        self.label = tk.Label(container, image=self.photo_image, bg='#e0e0e0', bd=0, highlightthickness=0)
        self.label.pack(fill=tk.BOTH, expand=True)

        # Zapisz aktualny rozmiar okna dla resize
        self.window.update_idletasks()
        self.last_width = self.window.winfo_width()
        self.last_height = self.window.winfo_height()
        
        # Info bar na dole
        self._create_info_bar()
        
    def _resize_keep_aspect(self, img, max_width, max_height):
        """Zmienia rozmiar obrazu zachowując proporcje"""
        h, w = img.shape[:2]
        
        # Oblicz współczynniki skalowania dla obu wymiarów
        scale_w = max_width / w
        scale_h = max_height / h
        
        # Wybierz mniejszy współczynnik (żeby obraz zmieścił się w obu wymiarach)
        scale = min(scale_w, scale_h)
        
        # Jeśli obraz jest mniejszy niż max, nie powiększaj
        # if scale >= 1.0:
        #     return img
        
        # Oblicz nowy rozmiar
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    def _create_info_bar(self):
        """Tworzy pasek informacji na dole okna"""
        info_frame = tk.Frame(self.window, bg="#e0e0e0", height=25)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        img = self.original_img
        h, w = img.shape[:2]
        img_type = "8-bit Gray" if len(img.shape) == 2 else "24-bit RGB"
        size_kb = img.nbytes / 1024
        
        info_text = f"  {w}x{h} pixels | {img_type} | {size_kb:.1f} KB"
        
        tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 8),
            bg="#e0e0e0",
            fg="#333",
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
    def _create_context_menu(self):
        """Tworzy menu kontekstowe (PPM)"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_separator()
        
        # Submenu Scale
        scale_menu = tk.Menu(self.context_menu, tearoff=0)
        self.context_menu.add_cascade(label="Scale", menu=scale_menu)
        scale_menu.add_command(label="Fit to Window (800x600)", command=lambda: self._rescale('fit'))
        scale_menu.add_command(label="Original Size", command=lambda: self._rescale('original'))
        scale_menu.add_command(label="Fullscreen", command=lambda: self._rescale('fullscreen'))
        
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Close", command=self.window.destroy)
        
        # Bind right click
        self.label.bind("<Button-3>", self._show_context_menu)
        
    def _show_context_menu(self, event):
        """Pokazuje menu kontekstowe"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def _rescale(self, scale_type):
        """Zmienia skalowanie obrazu"""
        self.scale = scale_type
        # Zniszcz obecne widgety
        for widget in self.window.winfo_children():
            widget.destroy()
        # Wyświetl ponownie
        self._display_image()
        
    def _exit_fullscreen(self):
        """Wychodzi z trybu pełnoekranowego"""
        self.window.attributes('-fullscreen', False)
        self._rescale('fit')
        
    def _on_focus(self, event):
        """Wywoływane gdy okno otrzyma focus"""
        if self.on_focus_callback:
            self.on_focus_callback()

    def _on_resize(self, event):
        """Automatyczne skalowanie obrazu przy zmianie rozmiaru okna"""
        # Ignoruj wydarzenia dla innych widgetów
        if event.widget != self.window:
            return
        
        # Sprawdź czy rozmiar faktycznie się zmienił (unikaj pętli)
        if hasattr(self, 'last_width') and hasattr(self, 'last_height'):
            if abs(event.width - self.last_width) < 10 and abs(event.height - self.last_height) < 10:
                return
        
        self.last_width = event.width
        self.last_height = event.height
        
        # Tylko dla trybu 'fit' i 'original' (nie fullscreen)
        if self.scale == 'fullscreen':
            return
        
        # Pobierz rozmiar okna (odejmij margines na info bar ~25px)
        target_width = event.width - 10
        target_height = event.height - 35  # Info bar na dole
        
        if target_width <= 0 or target_height <= 0:
            return
        
        # Przeskaluj obraz proporcjonalnie
        img = self.original_img.copy()
        
        # Konwersja do RGB
        if len(img.shape) == 2:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img
        
        # Skaluj zachowując proporcje
        img_resized = self._resize_keep_aspect(img_rgb, target_width, target_height)
        
        # Aktualizuj PhotoImage
        from PIL import Image, ImageTk
        img_pil = Image.fromarray(img_resized)
        self.photo_image = ImageTk.PhotoImage(img_pil)
        
        # Aktualizuj label
        self.label.config(image=self.photo_image)