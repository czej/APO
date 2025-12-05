import numpy as np
from functools import wraps


def validate_binary_operation(func):
    """
    Dekorator walidujący operacje dwuargumentowe logiczne.
    Sprawdza:
    - Czy oba obrazy są jednokanałowe (grayscale)
    - Czy mają identyczny rozmiar w pionie i poziomie
    """
    @wraps(func)
    def wrapper(img1, img2):
        # Sprawdzenie czy obrazy jednokanałowe
        if len(img1.shape) != 2 or len(img2.shape) != 2:
            raise ValueError("Oba obrazy muszą być w odcieniach szarości")
        
        # Sprawdzenie identycznego rozmiaru
        if img1.shape != img2.shape:
            raise ValueError(f"Obrazy muszą mieć identyczny rozmiar.\n"
                           f"Obraz 1: {img1.shape[1]}x{img1.shape[0]}\n"
                           f"Obraz 2: {img2.shape[1]}x{img2.shape[0]}")
        
        return func(img1, img2)
    
    return wrapper


class LogicalOperations:
    """Operacje logiczne na obrazach monochromatycznych i binarnych"""
    
    @staticmethod
    def logical_not(img):
        """
        Operacja logiczna NOT (negacja bitowa).
        Działa w pętli bit po bicie na każdym pikselu.
        
        Parametr:
            img: obraz numpy.ndarray (grayscale lub binary)
        
        Zwraca:
            obraz po operacji NOT
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        # Przygotuj tablicę wynikową
        result = np.zeros_like(img, dtype=np.uint8)
        height, width = img.shape
        
        # Pętla po pikselach
        for i in range(height):
            for j in range(width):
                # Operacja bitowa NOT na całym bajcie
                result[i, j] = ~img[i, j] & 0xFF  # & 0xFF zapewnia uint8
        
        return result
    
    @staticmethod
    @validate_binary_operation
    def logical_and(img1, img2):
        """
        Operacja logiczna AND.
        Działa w pętli bit po bicie na odpowiednich pikselach.
        
        Parametry:
            img1, img2: obrazy numpy.ndarray (grayscale lub binary)
        
        Zwraca:
            obraz po operacji AND
        """
        height, width = img1.shape
        
        # Przygotuj tablicę wynikową
        result = np.zeros_like(img1, dtype=np.uint8)
        
        # Pętla po pikselach - działanie na odpowiednich pikselach
        for i in range(height):
            for j in range(width):
                # Operacja bitowa AND - w pętli bit po bicie
                # Działamy na bitach o tej samej wadze
                result[i, j] = img1[i, j] & img2[i, j]
        
        return result
    
    @staticmethod
    @validate_binary_operation
    def logical_or(img1, img2):
        """
        Operacja logiczna OR.
        Działa w pętli bit po bicie na odpowiednich pikselach.
        
        Parametry:
            img1, img2: obrazy numpy.ndarray (grayscale lub binary)
        
        Zwraca:
            obraz po operacji OR
        """
        height, width = img1.shape
        result = np.zeros_like(img1, dtype=np.uint8)
        
        # Pętla po pikselach
        for i in range(height):
            for j in range(width):
                # Operacja bitowa OR - działanie na bitach o tej samej wadze
                result[i, j] = img1[i, j] | img2[i, j]
        
        return result
    
    @staticmethod
    @validate_binary_operation
    def logical_xor(img1, img2):
        """
        Operacja logiczna XOR (exclusive OR).
        Działa w pętli bit po bicie na odpowiednich pikselach.
        
        Parametry:
            img1, img2: obrazy numpy.ndarray (grayscale lub binary)
        
        Zwraca:
            obraz po operacji XOR
        """
        height, width = img1.shape
        result = np.zeros_like(img1, dtype=np.uint8)
        
        # Pętla po pikselach
        for i in range(height):
            for j in range(width):
                # Operacja bitowa XOR - działanie na bitach o tej samej wadze
                result[i, j] = img1[i, j] ^ img2[i, j]
        
        return result