import cv2
import numpy as np
from functools import wraps


def validate_arithmetic_operation(func):
    """
    Dekorator walidujący operacje arytmetyczne dwuargumentowe.
    Sprawdza:
    - Czy oba obrazy są jednokanałowe (grayscale)
    - Czy mają identyczny rozmiar
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


class ArithmeticOperations:
    """Operacje arytmetyczne na obrazach monochromatycznych"""
    
    @staticmethod
    @validate_arithmetic_operation
    def absolute_difference(img1, img2):
        """
        Różnica bezwzględna dwóch obrazów.
        Wynik = |img1 - img2|
        
        Parametry:
            img1, img2: obrazy numpy.ndarray (grayscale)
        
        Zwraca:
            obraz różnicy bezwzględnej
        """
        # Konwersja na int16 aby uniknąć overflow przy odejmowaniu
        img1_int = img1.astype(np.int16)
        img2_int = img2.astype(np.int16)
        
        # Oblicz różnicę bezwzględną
        result = np.abs(img1_int - img2_int)
        
        # Konwersja z powrotem na uint8
        result = result.astype(np.uint8)
        
        return result
    
    @staticmethod
    def add_images(images, saturation=True):
        """
        Dodawanie obrazów (2-5 obrazów).
        
        Parametry:
            images: lista obrazów numpy.ndarray (grayscale)
            saturation: 
                - True: z wysyceniem (obcięcie do 0-255)
                - False: bez wysycenia (skalowanie każdego obrazu przed dodaniem)
        
        Zwraca:
            obraz wynikowy
        """
        if not images or len(images) < 2:
            raise ValueError("Potrzebujesz co najmniej 2 obrazów do dodawania")
        
        if len(images) > 5:
            raise ValueError("Maksymalnie 5 obrazów można dodać jednocześnie")
        
        # Sprawdź czy wszystkie grayscale
        for i, img in enumerate(images):
            if len(img.shape) != 2:
                raise ValueError(f"Obraz {i+1} nie jest w odcieniach szarości")
        
        # Sprawdź rozmiary
        base_shape = images[0].shape
        for i, img in enumerate(images[1:], start=2):
            if img.shape != base_shape:
                raise ValueError(f"Obraz {i} ma inny rozmiar: {img.shape[1]}x{img.shape[0]} "
                            f"(oczekiwano: {base_shape[1]}x{base_shape[0]})")
        
        result = np.zeros_like(images[0], dtype=np.float32)
        if saturation:
            # Z wysyceniem
            for img in images:
                result += img.astype(np.float32)
        else:
            # Bez wysycenia
            max_scale_value = 255 // len(images)
            scaled_images = []
            
            for img in images:
                # Normalizacja do zakresu [0, max_scale_value]
                scaled = cv2.normalize(img, None, 0, max_scale_value, cv2.NORM_MINMAX)
                scaled_images.append(scaled)
            
            for img in scaled_images:
                result += img.astype(np.float32)

        result = np.clip(result, 0, 255)
        result = result.astype(np.uint8)
        
        return result