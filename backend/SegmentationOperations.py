"""
Operacje segmentacji obrazów - LAB3 Zadanie 2
Implementuje:
- Progowanie z dwoma progami
- Progowanie metodą Otsu
- Progowanie adaptacyjne
"""

import cv2
import numpy as np


class SegmentationOperations:
    """Klasa zawierająca operacje segmentacji obrazów"""
    
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