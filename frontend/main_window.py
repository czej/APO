import tkinter as tk
from tkinter import Menu, messagebox
import cv2
import numpy as np

from frontend.image_viewer import ImageViewer
from frontend.histogram import HistogramViewer
from frontend.dialogs import ThresholdDialog, PosterizeDialog, StretchDialog, BinaryOperationDialog, ScalarOperationDialog
from frontend.dialogs import SmoothingDialog, SharpeningDialog, PrewittDialog, SobelDialog, CustomMaskDialog, MedianDialog, CannyDialog
from frontend.dialogs import MorphologyDialog, SkeletonizationDialog, DoubleThresholdDialog, OtsuThresholdDialog, AdaptiveThresholdDialog
from backend.AppManager import AppManager


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Application")
        self.root.geometry("1200x800")
        
        self.app_manager = AppManager()
        self.images = []  # Lista wszystkich załadowanych obrazów
        self.current_image = None
        self.image_viewers = []  # Lista otwartych okien z obrazami
        
        self._create_menu()
        self._create_main_panel()
        
    def _create_menu(self):
        """Tworzy menu w stylu ImageJ"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # FILE MENU
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Otwórz...", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Zapisz", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Zapisz jako...", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Zamknij", command=self.close_current_image)
        file_menu.add_command(label="Wyjście", command=self.root.quit)
        
        # IMAGE MENU
        image_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Obraz", menu=image_menu)
        image_menu.add_command(label="Duplikuj...", command=self.duplicate_image, accelerator="Ctrl+D")
        
        # Submenu: Type
        type_menu = Menu(image_menu, tearoff=0)
        image_menu.add_cascade(label="Typ", menu=type_menu)
        type_menu.add_command(label="8-bit Skala szarości", command=self.convert_to_grayscale)
        type_menu.add_command(label="RGB Kolor", command=self.convert_to_color)
        type_menu.add_separator()
        type_menu.add_command(label="Maska binarna (0/1)", command=self.convert_to_binary_mask)
        type_menu.add_command(label="Maska 8-bit (0/255)", command=self.convert_to_8bit_mask)
        
        # Submenu: Adjust
        adjust_menu = Menu(image_menu, tearoff=0)
        image_menu.add_cascade(label="Dostosuj", menu=adjust_menu)
        adjust_menu.add_command(label="Jasność/Kontrast...")
        
        # PROCESS MENU - LAB 1
        process_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Przetwarzanie", menu=process_menu)
        
        # Point Operations
        process_menu.add_command(label="Odwróć (Negacja)", command=self.apply_negate, accelerator="Ctrl+Shift+I")
        process_menu.add_command(label="Posteryzacja...", command=self.apply_posterize)
        process_menu.add_separator()
        
        # Thresholding submenu
        threshold_menu = Menu(process_menu, tearoff=0)
        process_menu.add_cascade(label="Binaryzacja", menu=threshold_menu)
        threshold_menu.add_command(label="Progowanie", command=self.apply_threshold_binary)
        threshold_menu.add_command(label="Progowanie z poziomami", command=self.apply_threshold_levels)

        # Segmentation
        segmentation_menu = Menu(process_menu, tearoff=0)
        process_menu.add_cascade(label="Segmentacja", menu=segmentation_menu)
        segmentation_menu.add_command(label="Progowanie z dwoma progami", command=self.apply_double_threshold)
        segmentation_menu.add_command(label="Progowanie Otsu", command=self.apply_otsu_threshold)
        segmentation_menu.add_command(label="Progowanie adaptacyjne", command=self.apply_adaptive_threshold)
        
        # Histogram operations
        process_menu.add_command(label="Rozciągnij histogram", command=self.apply_stretch_histogram)
        process_menu.add_command(label="Wyrównaj histogram", command=self.apply_equalize_histogram)
        
        # PROCESS MENU - LAB 2
        process_menu.add_separator()
        
        # Math submenu
        math_menu = Menu(process_menu, tearoff=0)
        process_menu.add_cascade(label="Matematyka", menu=math_menu)
        math_menu.add_command(label="Dodaj obrazy", command=self.apply_add_images)
        math_menu.add_separator()
        math_menu.add_command(label="Dodaj liczbę", command=self.apply_add_scalar)
        math_menu.add_command(label="Pomnóż przez liczbę", command=self.apply_multiply_scalar)
        math_menu.add_command(label="Podziel przez liczbę", command=self.apply_divide_scalar)
        math_menu.add_separator()
        math_menu.add_command(label="Różnica bezwzględna", command=self.apply_absolute_difference)
        
        # Logical operations submenu
        logical_menu = Menu(process_menu, tearoff=0)
        process_menu.add_cascade(label="Logiczne", menu=logical_menu) 
        logical_menu.add_command(label="AND", command=self.apply_logical_and)
        logical_menu.add_command(label="OR", command=self.apply_logical_or)
        logical_menu.add_command(label="XOR", command=self.apply_logical_xor)
        logical_menu.add_command(label="NOT", command=self.apply_logical_not)
        
        # Filters submenu
        filters_menu = Menu(process_menu, tearoff=0)
        process_menu.add_cascade(label="Filtry", menu=filters_menu)
        filters_menu.add_command(label="Wygładzanie", command=self.apply_smoothing)
        filters_menu.add_command(label="Własna maska 3x3", command=self.apply_custom_mask)
        filters_menu.add_command(label="Wyostrzanie (Laplasjan)", command=self.apply_sharpening)
        filters_menu.add_command(label="Mediana", command=self.apply_median)
        
        # Edge detection submenu
        edge_menu = Menu(process_menu, tearoff=0)
        process_menu.add_cascade(label="Wykrywanie krawędzi", menu=edge_menu)
        edge_menu.add_command(label="Sobel", command=self.apply_sobel)
        edge_menu.add_command(label="Prewitt (kierunkowy)", command=self.apply_prewitt)
        edge_menu.add_command(label="Canny", command=self.apply_canny)
        
        # ANALYZE MENU - LAB 3 & 4
        analyze_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analiza", menu=analyze_menu)
        analyze_menu.add_command(label="Histogram", command=self.show_histogram, accelerator="Ctrl+H")
        analyze_menu.add_separator()
        analyze_menu.add_command(label="Pomiar")
        analyze_menu.add_command(label="Ustaw pomiary...")
        
        # Morphology submenu
        # Morphology submenu - LAB 3
        morphology_menu = Menu(analyze_menu, tearoff=0)
        analyze_menu.add_cascade(label="Morfologia", menu=morphology_menu)
        morphology_menu.add_command(label="Erozja", command=self.apply_erosion)
        morphology_menu.add_command(label="Dylacja", command=self.apply_dilation)
        morphology_menu.add_command(label="Otwarcie", command=self.apply_opening)
        morphology_menu.add_command(label="Zamknięcie", command=self.apply_closing)
        morphology_menu.add_separator()
        morphology_menu.add_command(label="Szkieletyzacja", command=self.apply_skeletonization)
        
        # PLUGINS MENU
        plugins_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Wtyczki", menu=plugins_menu)
        plugins_menu.add_command(label="Transformata Hougha...")
        plugins_menu.add_command(label="Inpainting...")
        plugins_menu.add_command(label="Segmentacja Graph Cut...")
        
        # WINDOW MENU
        window_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Okna", menu=window_menu)
        window_menu.add_command(label="Kaskadowo", command=self.cascade_windows)
        window_menu.add_command(label="Kafelki", command=self.tile_windows)
        window_menu.add_separator()
        window_menu.add_command(label="Pokaż wszystkie", command=self.show_all_windows)
        window_menu.add_command(label="Zamknij wszystkie", command=self.close_all_windows)
        
        # HELP MENU
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pomoc", menu=help_menu)
        help_menu.add_command(label="O programie...", command=self.show_about)
        
        # Keyboard shortcuts - bez zmian
        self.root.bind("<Control-o>", lambda e: self.load_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-d>", lambda e: self.duplicate_image())
        self.root.bind("<Control-h>", lambda e: self.show_histogram())
        self.root.bind("<Control-Shift-I>", lambda e: self.apply_negate())
        
    def _create_main_panel(self):
        """Tworzy główny panel aplikacji"""
        # Info panel
        info_frame = tk.Frame(self.root, bg="#f0f0f0", height=60)
        info_frame.pack(side=tk.TOP, fill=tk.X)
        info_frame.pack_propagate(False)
        
        tk.Label(
            info_frame, 
            text="Image Processing Application", 
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        ).pack(pady=10)
        
        self.status_label = tk.Label(
            info_frame,
            text="Ready | No image loaded",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666"
        )
        self.status_label.pack(pady=5)
        
        # Main canvas area (może być wykorzystany później)
        self.canvas_frame = tk.Frame(self.root, bg="white")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        welcome_label = tk.Label(
            self.canvas_frame,
            text="Open an image to start\n\nFile → Open... or Ctrl+O",
            font=("Arial", 12),
            fg="#999",
            bg="white"
        )
        welcome_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
    def _update_status(self, text):
        """Aktualizuje status bar"""
        self.status_label.config(text=text)
        
    def _require_image(func):
        """Dekorator sprawdzający czy obraz jest załadowany"""
        def wrapper(self, *args, **kwargs):
            if self.current_image is None:
                messagebox.showwarning(
                    "No Active Image",
                    "Please open or select an image first."
                )
                return None
            return func(self, *args, **kwargs)
        return wrapper
    
    def _require_grayscale(func):
        """Dekorator sprawdzający czy obraz jest w skali szarości"""
        def wrapper(self, *args, **kwargs):
            if self.current_image is None:
                messagebox.showwarning("No Active Image", "Please open an image first.")
                return None
            if len(self.current_image.shape) != 2:
                messagebox.showerror(
                    "Grayscale Required",
                    "This operation requires a grayscale image.\n\nConvert: Image → Type → 8-bit Grayscale"
                )
                return None
            return func(self, *args, **kwargs)
        return wrapper
    
    def _require_multiple_images(min_count=2):  # DODAJ TEN DEKORATOR
        """
        Dekorator sprawdzający czy jest wystarczająco dużo obrazów.
        
        Parametr:
            min_count: minimalna liczba obrazów wymagana
        """
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if len(self.images) < min_count:
                    messagebox.showwarning(
                        "Za mało obrazów",
                        f"Potrzebujesz co najmniej {min_count} obrazów do tej operacji.\n\n"
                        f"Obecnie: {len(self.images)} obraz(ów)"
                    )
                    return None
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
    
    # ============ FILE OPERATIONS ============
    
    def load_image(self):
        """Wczytuje obraz z pliku"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("All Images", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tif *.tiff"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            messagebox.showerror("Error", f"Failed to load image:\n{file_path}")
            return
        
        # Remove alpha channel if exists
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Automatic grayscale conversion
        if len(img.shape) == 3 and img.shape[2] == 3:
            # RGB -> Grayscale (if all channels are equal)
            if np.all(img[:,:,0] == img[:,:,1]) and np.all(img[:,:,1] == img[:,:,2]):
                img = img[:,:,0]
        
        self.images.append(img)
        self.current_image = img
        
        # Otwórz w nowym oknie
        viewer = ImageViewer(self.root, img, f"Image {len(self.images)}")
        viewer.on_focus_callback = lambda: self._set_active_image(img)
        viewer.on_close_callback = self._on_image_closed 
        self.image_viewers.append(viewer)
        
        self._update_status(f"Loaded: {file_path.split('/')[-1]} | {img.shape[1]}x{img.shape[0]} | {img.dtype}")
        
    @_require_image
    def save_image(self):
        """Zapisuje aktywny obraz"""
        self.save_image_as()
        
    @_require_image
    def save_image_as(self):
        """Zapisuje aktywny obraz jako..."""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tif")
            ]
        )
        
        if file_path:
            cv2.imwrite(file_path, self.current_image)
            messagebox.showinfo("Success", f"Image saved:\n{file_path}")
            self._update_status(f"Saved: {file_path.split('/')[-1]}")
            
    def close_current_image(self):
        """Zamyka aktywne okno obrazu"""
        # TODO: implementacja
        pass
    
    # ============ IMAGE OPERATIONS ============
    
    @_require_image
    def duplicate_image(self):
        """Duplikuje aktywny obraz"""
        dup = self.current_image.copy()
        self.images.append(dup)
        
        viewer = ImageViewer(self.root, dup, f"Duplicate of Image {len(self.images)-1}")
        viewer.on_focus_callback = lambda: self._set_active_image(dup)
        viewer.on_close_callback = self._on_image_closed
        self.image_viewers.append(viewer)
        
        self._update_status("Image duplicated")
        
    @_require_image
    def convert_to_grayscale(self):
        """Konwertuje aktywny obraz na skalę szarości"""
        if len(self.current_image.shape) == 2:
            messagebox.showinfo("Info", "Image is already grayscale.")
            return
        
        gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.images.append(gray)
        self.current_image = gray
        
        viewer = ImageViewer(self.root, gray, f"Grayscale {len(self.images)}")
        viewer.on_focus_callback = lambda: self._set_active_image(gray)
        viewer.on_close_callback = self._on_image_closed
        self.image_viewers.append(viewer)
        
        self._update_status("Converted to grayscale")
        
    @_require_grayscale
    def convert_to_color(self):
        """Konwertuje obraz grayscale na kolor (pseudocolor)"""
        color = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
        self.images.append(color)
        self.current_image = color
        
        viewer = ImageViewer(self.root, color, f"Color {len(self.images)}")
        viewer.on_focus_callback = lambda: self._set_active_image(color)
        viewer.on_close_callback = self._on_image_closed
        self.image_viewers.append(viewer)
        
        self._update_status("Converted to color")
    
    # ============ PROCESS OPERATIONS (LAB 1) ============
    
    @_require_grayscale
    def apply_negate(self):
        """Negacja obrazu"""
        result = self.app_manager.apply_negate(self.current_image)
        self._show_result(result, "Inverted")
        
    @_require_grayscale
    def apply_posterize(self):
        """Posteryzacja obrazu"""
        dialog = PosterizeDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Posterized")
        
    @_require_grayscale
    def apply_threshold_binary(self):
        """Progowanie binarne"""
        dialog = ThresholdDialog(
            self.root, 
            self.current_image, 
            self.app_manager,
            mode="binary"
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "Binary Threshold")
        
    @_require_grayscale
    def apply_threshold_levels(self):
        """Progowanie z zachowaniem poziomów"""
        dialog = ThresholdDialog(
            self.root,
            self.current_image,
            self.app_manager,
            mode="levels"
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "Threshold with Levels")
        
    @_require_grayscale
    def apply_stretch_histogram(self):
        """Rozciąganie histogramu"""
        dialog = StretchDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Stretched Histogram")
        
    @_require_grayscale
    def apply_equalize_histogram(self):
        """Equalizacja histogramu"""
        result = self.app_manager.apply_equalize_histogram(self.current_image)
        self._show_result(result, "Equalized Histogram")
    
    # ============ ANALYZE OPERATIONS ============
    
    @_require_image
    def show_histogram(self):
        """Wyświetla histogram"""
        histograms = self.app_manager.calculate_histograms(self.current_image)
        HistogramViewer(self.root, histograms)

    # ============ ARITHMETIC OPERATIONS (LAB 2) ============

    @_require_multiple_images(min_count=2)
    def apply_add_images(self):
        """Dodawanie obrazów (2-5)"""
        dialog = BinaryOperationDialog(
            self.root,
            "Dodawanie",
            "arithmetic_multi",
            self.images,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "Dodawanie obrazów")

    @_require_grayscale
    def apply_add_scalar(self):
        """Dodawanie liczby do obrazu"""
        dialog = ScalarOperationDialog(
            self.root,
            "Dodaj",
            self.current_image,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "Dodawanie liczby")
    
    @_require_grayscale
    def apply_multiply_scalar(self):
        """Mnożenie obrazu przez liczbę"""
        dialog = ScalarOperationDialog(
            self.root,
            "Pomnóż",
            self.current_image,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "Mnożenie przez liczbę")
    
    @_require_grayscale
    def apply_divide_scalar(self):
        """Dzielenie obrazu przez liczbę"""
        dialog = ScalarOperationDialog(
            self.root,
            "Podziel",
            self.current_image,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "Dzielenie przez liczbę")
    
    @_require_multiple_images(min_count=2)
    def apply_absolute_difference(self):
        """Różnica bezwzględna obrazów"""
        dialog = BinaryOperationDialog(
            self.root,
            "Różnica bezwzględna",
            "arithmetic",
            self.images,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "Różnica bezwzględna")

    # ============ LOGICAL OPERATIONS (LAB 2) ============
    
    @_require_grayscale
    def apply_logical_not(self):
        """Operacja logiczna NOT"""
        result = self.app_manager.apply_logical_not(self.current_image)
        self._show_result(result, "NOT")
    
    @_require_multiple_images(min_count=2)
    def apply_logical_and(self):
        """Operacja logiczna AND"""
        dialog = BinaryOperationDialog(
            self.root,
            "AND",
            "logical",
            self.images,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "AND")

    @_require_multiple_images(min_count=2)
    def apply_logical_or(self):
        """Operacja logiczna OR"""
        dialog = BinaryOperationDialog(
            self.root,
            "OR",
            "logical",
            self.images,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "OR")

    @_require_multiple_images(min_count=2)
    def apply_logical_xor(self):
        """Operacja logiczna XOR"""
        dialog = BinaryOperationDialog(
            self.root,
            "XOR",
            "logical",
            self.images,
            self.app_manager
        )
        dialog.on_result_callback = lambda img: self._show_result(img, "XOR")

    @_require_grayscale
    def convert_to_binary_mask(self):
        """Konwertuje maskę 8-bitową (0/255) na binarną (0/1)"""
        try:
            binary = self.app_manager.convert_to_binary_mask(self.current_image)
            self.images.append(binary)
            self.current_image = binary
            
            viewer = ImageViewer(self.root, binary, f"Maska binarna {len(self.images)}")
            viewer.on_focus_callback = lambda: self._set_active_image(binary)
            viewer.on_close_callback = self._on_image_closed
            self.image_viewers.append(viewer)
            
            self._update_status("Przekonwertowano na maskę binarną (0/1)")
        except ValueError as e:
            messagebox.showerror("Błąd konwersji", str(e))
    
    @_require_grayscale
    def convert_to_8bit_mask(self):
        """Konwertuje maskę binarną (0/1) na 8-bitową (0/255)"""
        try:
            mask_8bit = self.app_manager.convert_to_8bit_mask(self.current_image)
            self.images.append(mask_8bit)
            self.current_image = mask_8bit
            
            viewer = ImageViewer(self.root, mask_8bit, f"Maska 8-bit {len(self.images)}")
            viewer.on_focus_callback = lambda: self._set_active_image(mask_8bit)
            viewer.on_close_callback = self._on_image_closed
            self.image_viewers.append(viewer)
            
            self._update_status("Przekonwertowano na maskę 8-bit (0/255)")
        except ValueError as e:
            messagebox.showerror("Błąd konwersji", str(e))

    @_require_grayscale
    def apply_smoothing(self):
        """Wygładzanie liniowe"""
        dialog = SmoothingDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Wygładzanie")

    @_require_grayscale
    def apply_custom_mask(self):
        """Własna maska 3x3"""
        dialog = CustomMaskDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Własna maska")

    @_require_grayscale
    def apply_sharpening(self):
        """Wyostrzanie (Laplacjan)"""
        dialog = SharpeningDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Wyostrzanie")

    @_require_grayscale
    def apply_prewitt(self):
        """Kierunkowa detekcja krawędzi Prewitta"""
        dialog = PrewittDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Prewitt")

    @_require_grayscale
    def apply_sobel(self):
        """Detekcja krawędzi Sobela"""
        dialog = SobelDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Sobel")

    @_require_grayscale
    def apply_median(self):
        dialog = MedianDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Mediana")

    @_require_grayscale
    def apply_canny(self):
        """Detekcja krawędzi Canny"""
        dialog = CannyDialog(self.root, self.current_image, self.app_manager)
        dialog.on_result_callback = lambda img: self._show_result(img, "Canny")

    # ============ SEGMENTATION OPERATIONS - LAB 3 Zadanie 2 ============

    @_require_grayscale
    def apply_double_threshold(self):
        """Progowanie z dwoma progami"""
        try:
            dialog = DoubleThresholdDialog(self.root, self.current_image, self.app_manager)
            dialog.on_result_callback = lambda img: self._show_result(img, "Progowanie dwoma progami")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    @_require_grayscale
    def apply_otsu_threshold(self):
        """Progowanie metodą Otsu"""
        try:
            dialog = OtsuThresholdDialog(self.root, self.current_image, self.app_manager)
            dialog.on_result_callback = lambda img: self._show_result(img, "Progowanie Otsu")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    @_require_grayscale
    def apply_adaptive_threshold(self):
        """Progowanie adaptacyjne"""
        try:
            dialog = AdaptiveThresholdDialog(self.root, self.current_image, self.app_manager)
            dialog.on_result_callback = lambda img: self._show_result(img, "Progowanie adaptacyjne")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    # ============ MORPHOLOGY OPERATIONS - LAB 3 ============

    @_require_grayscale
    def apply_erosion(self):
        try:
            dialog = MorphologyDialog(self.root, self.current_image, self.app_manager, "Erozja")
            dialog.on_result_callback = lambda img: self._show_result(img, "Erozja")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    @_require_grayscale
    def apply_dilation(self):
        try:
            dialog = MorphologyDialog(self.root, self.current_image, self.app_manager, "Dylacja")
            dialog.on_result_callback = lambda img: self._show_result(img, "Dylacja")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    @_require_grayscale
    def apply_opening(self):
        try:
            dialog = MorphologyDialog(self.root, self.current_image, self.app_manager, "Otwarcie")
            dialog.on_result_callback = lambda img: self._show_result(img, "Otwarcie")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    @_require_grayscale
    def apply_closing(self):
        try:
            dialog = MorphologyDialog(self.root, self.current_image, self.app_manager, "Zamknięcie")
            dialog.on_result_callback = lambda img: self._show_result(img, "Zamknięcie")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))

    @_require_grayscale
    def apply_skeletonization(self):
        try:
            dialog = SkeletonizationDialog(self.root, self.current_image, self.app_manager)
            dialog.on_result_callback = lambda img: self._show_result(img, "Szkieletyzacja")
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))
        
    # ============ WINDOW MANAGEMENT ============
    
    def cascade_windows(self):
        """Układa okna kaskadowo"""
        offset = 30
        for i, viewer in enumerate(self.image_viewers):
            if viewer.window.winfo_exists():
                viewer.window.geometry(f"+{50 + i*offset}+{50 + i*offset}")
                
    def tile_windows(self):
        """Układa okna obok siebie"""
        # TODO: implementacja
        pass
        
    def show_all_windows(self):
        """Pokazuje wszystkie okna"""
        for viewer in self.image_viewers:
            if viewer.window.winfo_exists():
                viewer.window.deiconify()
                
    def close_all_windows(self):
        """Zamyka wszystkie okna obrazów"""
        for viewer in self.image_viewers:
            if viewer.window.winfo_exists():
                viewer.window.destroy()
        self.image_viewers.clear()
        self.current_image = None
        self._update_status("All images closed")
    
    # ============ HELPERS ============
    
    def _set_active_image(self, img):
        """Ustawia aktywny obraz"""
        self.current_image = img
        shape_str = f"{img.shape[1]}x{img.shape[0]}"
        type_str = "Grayscale" if len(img.shape) == 2 else "Color"
        self._update_status(f"Active: {shape_str} | {type_str} | {img.dtype}")
        
    def _show_result(self, img, title):
        """Wyświetla wynik operacji w nowym oknie"""
        self.images.append(img)
        viewer = ImageViewer(self.root, img, title)
        viewer.on_focus_callback = lambda: self._set_active_image(img)
        viewer.on_close_callback = self._on_image_closed
        self.image_viewers.append(viewer)
        self._update_status(f"Created: {title}")

    def _on_image_closed(self, img):
        """
        Wywoływane gdy okno obrazu jest zamykane.
        Usuwa obraz z pamięci programu.
        """
        # Znajdź indeks obrazu przez porównanie identity (is)
        img_index = None
        for idx, image in enumerate(self.images):
            if image is img:
                img_index = idx
                break
        
        # Usuń obraz z listy
        if img_index is not None:
            self.images.pop(img_index)
        
        # Jeśli to był aktywny obraz, wyczyść
        if self.current_image is img:
            self.current_image = None
            if self.images:
                # Ustaw pierwszy dostępny obraz jako aktywny
                self.current_image = self.images[0]
                self._update_status(f"Aktywny obraz zmieniony | Pozostało: {len(self.images)} obraz(ów)")
            else:
                self._update_status("Wszystkie obrazy zamknięte | Brak aktywnego obrazu")
        else:
            self._update_status(f"Obraz zamknięty | Pozostało: {len(self.images)} obraz(ów)")
        
        # Usuń viewer z listy (opcjonalnie - czyszczenie)
        self.image_viewers = [v for v in self.image_viewers if v.window.winfo_exists()]
        
    def show_about(self):
        """Wyświetla okno About"""
        messagebox.showinfo(
            "About",
            "Image Processing Application\n\n"
            "Laboratorium APO 2025/2026\n"
            "Based on ImageJ interface"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()