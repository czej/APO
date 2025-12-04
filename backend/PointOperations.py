import numpy as np

class PointOperations:
    @staticmethod
    def negate(img):
        """
        Negacja obrazu (odwrócenie poziomów szarości).
        
        Parametr:
            img: obraz numpy.ndarray (grayscale)
        
        Zwraca:
            znegowany obraz
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        return 255 - img
    
    @staticmethod
    def posterize(img, levels):
        """
        Redukcja poziomów szarości (posteryzacja).
        
        Parametry:
            img: obraz numpy.ndarray (grayscale)
            levels: liczba poziomów szarości (np. 2, 4, 8, 16)
        
        Zwraca:
            obraz z ograniczoną liczbą poziomów szarości
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        if levels < 2 or levels > 256:
            raise ValueError("Liczba poziomów musi być w zakresie 2-256")
        
        # Oblicz rozmiar przedziału
        step = 256 / levels
        
        # Kwantyzacja
        result = np.floor(img / step) * step
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def threshold_binary(img, threshold):
        """
        Progowanie binarne.
        
        Parametry:
            img: obraz numpy.ndarray (grayscale)
            threshold: próg (0-255)
        
        Zwraca:
            obraz binarny (0 lub 255)
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        if threshold < 0 or threshold > 255:
            raise ValueError("Próg musi być w zakresie 0-255")
        
        result = np.where(img >= threshold, 255, 0).astype(np.uint8)
        return result
    
    @staticmethod
    def threshold_with_levels(img, threshold):
        """
        Progowanie z zachowaniem poziomów szarości.
        Piksele poniżej progu = 0, powyżej = oryginalna wartość
        
        Parametry:
            img: obraz numpy.ndarray (grayscale)
            threshold: próg (0-255)
        
        Zwraca:
            obraz z zachowanymi poziomami szarości powyżej progu
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        if threshold < 0 or threshold > 255:
            raise ValueError("Próg musi być w zakresie 0-255")
        
        result = np.where(img >= threshold, img, 0).astype(np.uint8)
        return result