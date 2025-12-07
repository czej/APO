"""
Operacje segmentacji obrazów - LAB3 Zadanie 2
Implementuje:
- Progowanie z dwoma progami
- Progowanie metodą Otsu
- Progowanie adaptacyjne

LAB3 Zadanie 1:
- Rozciąganie histogramu w zadanym zakresie
"""

import cv2
import numpy as np


class SegmentationOperations:
    """Klasa zawierająca operacje segmentacji obrazów"""
    
    @staticmethod
    def stretch_histogram_range(image, p1, p2, q1, q2):
        """
        Rozciąganie histogramu w zadanym zakresie.
        
        Przekształca piksele z zakresu [p1, p2] na zakres [q1, q2]
        używając transformacji liniowej.
        
        Wzór:
        output = (input - p1) * (q2 - q1) / (p2 - p1) + q1
        
        Args:
            image: Obraz w skali szarości
            p1: Dolna granica zakresu wejściowego (0-255)
            p2: Górna granica zakresu wejściowego (0-255)
            q1: Dolna granica zakresu wyjściowego (0-255)
            q2: Górna granica zakresu wyjściowego (0-255)
            
        Returns:
            Obraz z rozciągniętym histogramem
        """
        if len(image.shape) != 2:
            raise ValueError("Obraz musi być w skali szarości")
        
        # Walidacja parametrów
        if p1 >= p2:
            raise ValueError("p1 musi być mniejsze od p2")
        if q1 >= q2:
            raise ValueError("q1 musi być mniejsze od q2")
        
        # Konwersja do float dla dokładności obliczeń
        result = image.astype(np.float32)
        
        # Transformacja liniowa: y = (x - p1) * (q2 - q1) / (p2 - p1) + q1
        # Tylko dla pikseli w zakresie [p1, p2]
        
        # Piksele poniżej p1 → q1
        result[image < p1] = q1
        
        # Piksele powyżej p2 → q2  
        result[image > p2] = q2
        
        # Piksele w zakresie [p1, p2] → transformacja liniowa
        mask = (image >= p1) & (image <= p2)
        result[mask] = (image[mask] - p1) * (q2 - q1) / (p2 - p1) + q1
        
        # Obetnij do zakresu [0, 255] i konwertuj do uint8
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def threshold_double(image, lower_threshold, upper_threshold):
        """
        Progowanie z dwoma progami.
        Piksele w zakresie [lower_threshold, upper_threshold] = 255 (białe)
        Pozostałe piksele = 0 (czarne)
        
        Args:
            image: Obraz w skali szarości
            lower_threshold: Dolny próg (0-255)
            upper_threshold: Górny próg (0-255)
            
        Returns:
            Obraz binarny
        """
        if len(image.shape) != 2:
            raise ValueError("Obraz musi być w skali szarości")
        
        if lower_threshold > upper_threshold:
            lower_threshold, upper_threshold = upper_threshold, lower_threshold
        
        # Tworzymy maskę: TRUE dla pikseli w zakresie [lower, upper]
        mask = (image >= lower_threshold) & (image <= upper_threshold)
        
        # Konwersja maski na obraz binarny (0 lub 255)
        result = np.zeros_like(image)
        result[mask] = 255
        
        return result
    
    @staticmethod
    def threshold_otsu(image):
        """
        Progowanie metodą Otsu - automatyczne wyznaczenie optymalnego progu.
        
        Metoda Otsu znajduje próg minimalizujący wariancję wewnątrzklasową
        (lub maksymalizujący wariancję międzyklasową).
        
        Args:
            image: Obraz w skali szarości
            
        Returns:
            tuple: (threshold_value, binary_image)
                - threshold_value: Wyznaczony próg Otsu
                - binary_image: Obraz binarny po progowaniu
        """
        if len(image.shape) != 2:
            raise ValueError("Obraz musi być w skali szarości")
        
        # cv2.threshold z flagą cv2.THRESH_OTSU automatycznie wyznacza próg
        # Zwraca: (threshold_value, thresholded_image)
        threshold_value, binary_image = cv2.threshold(
            image, 
            0,  # Ignorowane przy użyciu THRESH_OTSU
            255,  # Maksymalna wartość dla pikseli powyżej progu
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        return threshold_value, binary_image
    
    @staticmethod
    def threshold_adaptive(image, method='mean', block_size=11, C=2):
        """
        Progowanie adaptacyjne - próg wyznaczany lokalnie dla każdego piksela.
        
        Args:
            image: Obraz w skali szarości
            method: Metoda adaptacyjna:
                - 'mean': ADAPTIVE_THRESH_MEAN_C (średnia w otoczeniu)
                - 'gaussian': ADAPTIVE_THRESH_GAUSSIAN_C (średnia ważona gaussowsko)
            block_size: Rozmiar sąsiedztwa (nieparzysty, >= 3)
            C: Stała odejmowana od średniej (może być ujemna)
            
        Returns:
            Obraz binarny
        """
        if len(image.shape) != 2:
            raise ValueError("Obraz musi być w skali szarości")
        
        # Zapewnienie nieparzystego rozmiaru bloku >= 3
        if block_size < 3:
            block_size = 3
        if block_size % 2 == 0:
            block_size += 1
        
        # Wybór metody adaptacyjnej
        if method == 'mean':
            adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
        elif method == 'gaussian':
            adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        else:
            raise ValueError("Metoda musi być 'mean' lub 'gaussian'")
        
        # Progowanie adaptacyjne
        binary_image = cv2.adaptiveThreshold(
            image,
            255,  # Maksymalna wartość
            adaptive_method,
            cv2.THRESH_BINARY,
            block_size,
            C
        )
        
        return binary_image
    
    @staticmethod
    def threshold_adaptive_inverse(image, method='mean', block_size=11, C=2):
        """
        Progowanie adaptacyjne odwrócone.
        
        Args:
            image: Obraz w skali szarości
            method: Metoda adaptacyjna ('mean' lub 'gaussian')
            block_size: Rozmiar sąsiedztwa (nieparzysty, >= 3)
            C: Stała odejmowana od średniej
            
        Returns:
            Obraz binarny (odwrócony)
        """
        if len(image.shape) != 2:
            raise ValueError("Obraz musi być w skali szarości")
        
        if block_size < 3:
            block_size = 3
        if block_size % 2 == 0:
            block_size += 1
        
        if method == 'mean':
            adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
        elif method == 'gaussian':
            adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        else:
            raise ValueError("Metoda musi być 'mean' lub 'gaussian'")
        
        # Progowanie adaptacyjne odwrócone
        binary_image = cv2.adaptiveThreshold(
            image,
            255,
            adaptive_method,
            cv2.THRESH_BINARY_INV,  # Odwrócone
            block_size,
            C
        )
        
        return binary_image