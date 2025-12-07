"""
Operacje na histogramie - LAB3 Zadanie 1
"""

import numpy as np


class HistogramOperations:
    """Klasa zawierająca operacje na histogramie"""
    
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
        
        # Transformacja liniowa dla WSZYSTKICH pikseli
        # y = (x - p1) * (q2 - q1) / (p2 - p1) + q1
        result = (result - p1) * (q2 - q1) / (p2 - p1) + q1
        
        # Obetnij do zakresu [0, 255] i konwertuj do uint8
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result