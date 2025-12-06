import numpy as np


class MaskOperations:
    """Operacje konwersji masek binarnych"""
    
    @staticmethod
    def to_8bit_mask(img):
        """
        Konwertuje maskę binarną (0/1) na maskę 8-bitową (0/255).
        
        Parametr:
            img: obraz numpy.ndarray (grayscale)
        
        Zwraca:
            maska 8-bitowa (0/255)
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        # Sprawdź czy to maska binarna (wartości 0/1)
        unique_values = np.unique(img)
        if not np.all(np.isin(unique_values, [0, 1])):
            raise ValueError(
                "Obraz nie jest maską binarną (0/1).\n"
                f"Znalezione wartości: {unique_values}\n\n"
                "Użyj progowania aby utworzyć maskę binarną."
            )
        
        # Konwersja: 0->0, 1->255
        result = (img * 255).astype(np.uint8)
        
        return result
    
    @staticmethod
    def to_binary_mask(img):
        """
        Konwertuje maskę 8-bitową (0/255) na maskę binarną (0/1).
        
        Parametr:
            img: obraz numpy.ndarray (grayscale)
        
        Zwraca:
            maska binarna (0/1)
        """
        if len(img.shape) != 2:
            raise ValueError("Obraz musi być w odcieniach szarości")
        
        # Sprawdź czy to maska 8-bitowa (wartości 0/255)
        unique_values = np.unique(img)
        if not np.all(np.isin(unique_values, [0, 255])):
            raise ValueError(
                "Obraz nie jest maską 8-bitową (0/255).\n"
                f"Znalezione wartości: {unique_values}\n\n"
                "Użyj progowania binarnego aby utworzyć maskę."
            )
        
        # Konwersja: 0→0, 255→1
        result = (img // 255).astype(np.uint8)
        
        return result