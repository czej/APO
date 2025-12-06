import cv2
import numpy as np


class ConvolutionOperations:
    """
    Klasa implementująca operacje konwolucji dla zadania 3:
    - Wygładzanie liniowe (uśrednienie, ważone, Gauss)
    - Wyostrzanie (Laplacjan)
    - Detekcja krawędzi (Prewitt kierunkowy, Sobel)
    """
    
    # ==================== MASKI WYGŁADZANIA ====================
    
    SMOOTHING_MASKS = {
        "Uśrednienie": np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]
        ], dtype=np.float32) / 5,
        
        "Filtr Gaussa": np.array([
            [1, 2, 1],
            [2, 5, 2],
            [1, 2, 1]
        ], dtype=np.float32) / 17,
    }
    
    # ==================== MASKI LAPLASJANOWE ====================
    
    LAPLACIAN_MASKS = {
        "Laplacjan wariant 1": np.array([
            [0, 1, 0],
            [1, -4, 1],
            [0, 1, 0]
        ], dtype=np.float32),
        
        "Laplacjan wariant 2": np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ], dtype=np.float32),
        
        "Laplacjan wariant 3": np.array([
            [-1, 2, -1],
            [2, -4, 2],
            [-1, 2, -1]
        ], dtype=np.float32),
    }
    
    # ==================== MASKI PREWITTA (8 kierunków) ====================
    
    PREWITT_MASKS = {
        "Prewitt N (0°)": np.array([
            [1, 1, 1],
            [0, 0, 0],
            [-1, -1, -1]
        ], dtype=np.float32),
        
        "Prewitt NE (45°)": np.array([
            [0, 1, 1],
            [-1, 0, 1],
            [-1, -1, 0]
        ], dtype=np.float32),
        
        "Prewitt E (90°)": np.array([
            [-1, 0, 1],
            [-1, 0, 1],
            [-1, 0, 1]
        ], dtype=np.float32),
        
        "Prewitt SE (135°)": np.array([
            [-1, -1, 0],
            [-1, 0, 1],
            [0, 1, 1]
        ], dtype=np.float32),
        
        "Prewitt S (180°)": np.array([
            [-1, -1, -1],
            [0, 0, 0],
            [1, 1, 1]
        ], dtype=np.float32),
        
        "Prewitt SW (225°)": np.array([
            [0, -1, -1],
            [1, 0, -1],
            [1, 1, 0]
        ], dtype=np.float32),
        
        "Prewitt W (270°)": np.array([
            [1, 0, -1],
            [1, 0, -1],
            [1, 0, -1]
        ], dtype=np.float32),
        
        "Prewitt NW (315°)": np.array([
            [1, 1, 0],
            [1, 0, -1],
            [0, -1, -1]
        ], dtype=np.float32),
    }
    
    # ==================== MASKI SOBELA ====================
    
    SOBEL_X = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ], dtype=np.float32)
    
    SOBEL_Y = np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ], dtype=np.float32)
    
    # ==================== TYPY BRZEGÓW ====================
    
    BORDER_TYPES = {
        "BORDER_CONSTANT": cv2.BORDER_CONSTANT,
        "BORDER_REFLECT": cv2.BORDER_REFLECT,
        "Wypełnienie wyniku stałą": None  # Specjalna obsługa
    }
    
    def __init__(self):
        pass
    
    # ==================== METODY POMOCNICZE ====================
    
    @staticmethod
    def _validate_image(img):
        """Sprawdza czy obraz jest monochromatyczny"""
        if img is None:
            raise ValueError("Obraz jest pusty (None)")
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być monochromatyczny (skala szarości)")
        return True
    
    @staticmethod
    def _normalize_result(img):
        """Normalizuje wynik do zakresu 0-255"""
        img_min = np.min(img)
        img_max = np.max(img)
        
        if img_max - img_min == 0:
            return np.zeros_like(img, dtype=np.uint8)
        
        normalized = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
        return normalized
    
    def _apply_convolution_with_border(self, img, kernel, border_type, border_value):
        """
        Wspólna metoda do stosowania konwolucji z obsługą brzegów
        
        Args:
            img: Obraz wejściowy
            kernel: Maska konwolucji
            border_type: Typ brzegu
            border_value: Wartość dla BORDER_CONSTANT
            
        Returns:
            Przetworzony obraz
        """
        # Obsługa "Wypełnienie wyniku stałą"
        if border_type == "Wypełnienie wyniku stałą":
            result = np.full_like(img, border_value, dtype=np.float32)
            
            pad = kernel.shape[0] // 2
            h, w = img.shape
            
            for i in range(pad, h - pad):
                for j in range(pad, w - pad):
                    roi = img[i-pad:i+pad+1, j-pad:j+pad+1].astype(np.float32)
                    result[i, j] = np.sum(roi * kernel)
            
            return result
        else:
            # Standardowa konwolucja z cv2
            border = self.BORDER_TYPES[border_type]
            img_float = img.astype(np.float32)
            
            # Dla BORDER_CONSTANT musimy ręcznie dodać ramkę
            if border == cv2.BORDER_CONSTANT:
                pad = kernel.shape[0] // 2
                padded = cv2.copyMakeBorder(
                    src=img_float,
                    top=pad,
                    bottom=pad,
                    left=pad,
                    right=pad,
                    borderType=cv2.BORDER_CONSTANT,
                    value=float(border_value)
                )
                result = cv2.filter2D(
                    src=padded,
                    ddepth=-1,
                    kernel=kernel,
                    anchor=(-1, -1),
                    borderType=cv2.BORDER_ISOLATED
                )
                # Wytnij ramkę z powrotem
                result = result[pad:-pad, pad:-pad]
            else:
                result = cv2.filter2D(
                    src=img_float,
                    ddepth=-1,
                    kernel=kernel,
                    anchor=(-1, -1),
                    borderType=border
                )
            
            return result.astype(np.float32)
    
    # ==================== WYGŁADZANIE LINIOWE ====================
    
    def apply_smoothing(self, img, mask_name, border_type="BORDER_REFLECT", border_value=0):
        """
        Stosuje filtr wygładzający
        
        Args:
            img: Obraz wejściowy (grayscale)
            mask_name: Nazwa maski z SMOOTHING_MASKS
            border_type: Typ brzegu ("BORDER_CONSTANT", "BORDER_REFLECT", "Wypełnienie wyniku stałą")
            border_value: Wartość dla BORDER_CONSTANT (0-255)
        
        Returns:
            Wygładzony obraz
        """
        self._validate_image(img)
        
        if mask_name not in self.SMOOTHING_MASKS:
            raise ValueError(f"Nieznana maska: {mask_name}")
        
        kernel = self.SMOOTHING_MASKS[mask_name]
        result = self._apply_convolution_with_border(img, kernel, border_type, border_value)
        
        return result.astype(np.uint8)
    
    # ==================== WYOSTRZANIE (LAPLACJAN) ====================
    
    def apply_sharpening(self, img, mask_name, border_type="BORDER_REFLECT", border_value=0):
        """
        Stosuje filtr wyostrzający (Laplacjan)
        
        Args:
            img: Obraz wejściowy (grayscale)
            mask_name: Nazwa maski z LAPLACIAN_MASKS
            border_type: Typ brzegu
            border_value: Wartość dla BORDER_CONSTANT
        
        Returns:
            Wyostrzony obraz
        """
        self._validate_image(img)
        
        if mask_name not in self.LAPLACIAN_MASKS:
            raise ValueError(f"Nieznana maska: {mask_name}")
        
        kernel = self.LAPLACIAN_MASKS[mask_name]
        result = self._apply_convolution_with_border(img, kernel, border_type, border_value)
        
        return self._normalize_result(result)
    
    # ==================== DETEKCJA KRAWĘDZI - PREWITT ====================
    
    def apply_prewitt(self, img, direction, border_type="BORDER_REFLECT", border_value=0):
        """
        Stosuje kierunkowy filtr Prewitta
        
        Args:
            img: Obraz wejściowy (grayscale)
            direction: Kierunek z PREWITT_MASKS
            border_type: Typ brzegu
            border_value: Wartość dla BORDER_CONSTANT
        
        Returns:
            Obraz z wykrytymi krawędziami
        """
        self._validate_image(img)
        
        if direction not in self.PREWITT_MASKS:
            raise ValueError(f"Nieznany kierunek: {direction}")
        
        kernel = self.PREWITT_MASKS[direction]
        result = self._apply_convolution_with_border(img, kernel, border_type, border_value)
        
        return self._normalize_result(result)
    
    # ==================== DETEKCJA KRAWĘDZI - SOBEL ====================
    
    def apply_sobel(self, img, border_type="BORDER_REFLECT", border_value=0):
        """
        Stosuje operator Sobela (kombinacja dwóch prostopadłych masek)
        
        Args:
            img: Obraz wejściowy (grayscale)
            border_type: Typ brzegu
            border_value: Wartość dla BORDER_CONSTANT
        
        Returns:
            Obraz z wykrytymi krawędziami (magniduda gradientu)
        """
        self._validate_image(img)
        
        # Gradient X i Y
        grad_x = self._apply_convolution_with_border(img, self.SOBEL_X, border_type, border_value)
        grad_y = self._apply_convolution_with_border(img, self.SOBEL_Y, border_type, border_value)
        
        # Magnituda gradientu
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        return self._normalize_result(magnitude)
    
    # ==================== WŁASNA MASKA ====================
    
    def apply_custom_mask(self, img, mask, border_type="BORDER_REFLECT", border_value=0):
        """
        Stosuje własną maskę zdefiniowaną przez użytkownika
        
        Args:
            img: Obraz wejściowy (grayscale)
            mask: Maska konwolucji (numpy array)
            border_type: Typ brzegu
            border_value: Wartość dla BORDER_CONSTANT
        
        Returns:
            Przefiltrowany obraz
        """
        self._validate_image(img)
        
        if mask.shape != (3, 3):
            raise ValueError("Maska musi być rozmiaru 3x3")
        
        result = self._apply_convolution_with_border(img, mask, border_type, border_value)
        
        # Sprawdź czy wartości są w rozsądnym zakresie
        if np.min(result) < 0 or np.max(result) > 255:
            return self._normalize_result(result)
        else:
            return np.clip(result, 0, 255).astype(np.uint8)
    
    # ==================== GETTERY DLA UI ====================
    
    def get_smoothing_mask_names(self):
        """Zwraca listę nazw masek wygładzających"""
        return list(self.SMOOTHING_MASKS.keys())
    
    def get_laplacian_mask_names(self):
        """Zwraca listę nazw masek Laplacjana"""
        return list(self.LAPLACIAN_MASKS.keys())
    
    def get_prewitt_directions(self):
        """Zwraca listę kierunków Prewitta"""
        return list(self.PREWITT_MASKS.keys())
    
    def get_border_types(self):
        """Zwraca listę typów brzegów"""
        return list(self.BORDER_TYPES.keys())
    
    # ==================== CANNY EDGE DETECTION ====================
    
    def apply_canny(self, img, threshold1=100, threshold2=200):
        """
        Detekcja krawędzi operatorem Canny'ego
        
        Args:
            img: Obraz wejściowy (grayscale)
            threshold1: Dolny próg histerezy
            threshold2: Górny próg histerezy
        
        Returns:
            Obraz binarny z krawędziami
        """
        self._validate_image(img)
        
        result = cv2.Canny(
            image=img,
            threshold1=threshold1,
            threshold2=threshold2,
            apertureSize=3,
            L2gradient=False
        )
        
        return result
    
    # ==================== MEDIAN FILTER ====================
    
    def apply_median(self, img, kernel_size=3, border_type="BORDER_REFLECT", border_value=0):
        """
        Filtr medianowy
        
        Args:
            img: Obraz wejściowy (grayscale)
            kernel_size: Rozmiar kernela (3, 5, 7, 9)
            border_type: Typ brzegu
            border_value: Wartość dla BORDER_CONSTANT
        
        Returns:
            Przefiltrowany obraz
        """
        self._validate_image(img)
        
        if kernel_size not in [3, 5, 7, 9]:
            raise ValueError("Rozmiar kernela musi być 3, 5, 7 lub 9")
        
        # Obsługa "Wypełnienie wyniku stałą"
        if border_type == "Wypełnienie wyniku stałą":
            result = np.full_like(img, border_value, dtype=np.uint8)
            
            pad = kernel_size // 2
            h, w = img.shape
            
            for i in range(pad, h - pad):
                for j in range(pad, w - pad):
                    roi = img[i-pad:i+pad+1, j-pad:j+pad+1]
                    result[i, j] = np.median(roi)
            
            return result
        else:
            border = self.BORDER_TYPES[border_type]
            
            # Dla BORDER_CONSTANT dodaj ramkę
            if border == cv2.BORDER_CONSTANT:
                pad = kernel_size // 2
                padded = cv2.copyMakeBorder(
                    src=img,
                    top=pad,
                    bottom=pad,
                    left=pad,
                    right=pad,
                    borderType=cv2.BORDER_CONSTANT,
                    value=float(border_value)
                )
                result = cv2.medianBlur(src=padded, ksize=kernel_size)
                result = result[pad:-pad, pad:-pad]
            else:
                result = cv2.medianBlur(src=img, ksize=kernel_size)
            
            return result