import cv2
import numpy as np


class CustomMorphologyOperations:
    """
    Erozja i dylacja z dowolnym elementem strukturyzującym podanym przez
    użytkownika.  Zamiast cv2.erode / cv2.dilate używamy cv2.morphologyEx,
    który przyjmuje dowolną macierz uint8 jako kernel.
    """

    # ─── walidacja ────────────────────────────────────────────────────────

    @staticmethod
    def _validate_binary(image: np.ndarray) -> None:
        """
        Sprawdza, czy obraz jest binarny (wartości 0/255 lub 0/1).
        Rzuca ValueError z czytelną wiadomością jeśli nie jest.
        """
        if image.ndim != 2:
            raise ValueError(
                "Obraz nie jest jednokanalowy.\n"
                "Wymagany obraz w skali szarości (2D)."
            )

        unique = set(np.unique(image).tolist())
        # dopuszczamy {0}, {1}, {255}, {0, 1}, {0, 255}
        if not (unique.issubset({0, 255}) or unique.issubset({0, 1})):
            raise ValueError(
                "Obraz nie jest binarny.\n\n"
                "Dozwolone wartości pikselów: 0/255 lub 0/1.\n"
                f"Znalezione wartości: {sorted(unique)}\n\n"
                "Wskazówka: przekonwertuj obraz na binarny np.\n"
                "Przetwarzanie → Binaryzacja → Progowanie Otsu"
            )

    @staticmethod
    def _validate_kernel(kernel: np.ndarray) -> None:
        """
        Sprawdza poprawność kernela:
        - musi być macierzą 2D numpy uint8
        - musi zawierać przynajmniej jeden piksel != 0
        """
        if kernel.ndim != 2:
            raise ValueError("Kernel musi być macierzą 2D.")
        if kernel.size == 0:
            raise ValueError("Kernel nie może być pusty.")
        if not np.any(kernel):
            raise ValueError(
                "Element strukturyzujący jest pusty (same zeros).\n"
                "Zaznacz przynajmniej jedną komórku."
            )

    # ─── helper ───────────────────────────────────────────────────────────

    @staticmethod
    def _is_01_mask(image: np.ndarray) -> bool:
        """True jeśli obraz jest maską 0/1 (max wartość <= 1)."""
        return image.max() <= 1

    # ─── operacje ─────────────────────────────────────────────────────────

    @staticmethod
    def erode(image: np.ndarray, kernel: np.ndarray, 
              border_type: str = "BORDER_REFLECT", border_value: int = 0) -> np.ndarray:
        """
        Erozja obrazu binarnego z podanym elementem strukturyzującym.
        Działa dla maski 0/255 i 0/1 — wynik ma ten sam zakres co wejście.
        
        Parameters
        ----------
        image        : obraz binarny (0/255 lub 0/1)
        kernel       : element strukturyzujący (0/1)
        border_type  : "BORDER_CONSTANT" | "BORDER_REFLECT" | "Wypełnienie wyniku stałą"
        border_value : wartość dla BORDER_CONSTANT / wypełnienia (0-255)
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)

        kernel = kernel.astype(np.uint8)
        is_01 = CustomMorphologyOperations._is_01_mask(image)

        # Normalize to 0/255 for morphologyEx
        work = image * 255 if is_01 else image
        
        # Handle border types
        if border_type == "Wypełnienie wyniku stałą":
            # Fill result with constant, compute only interior
            result = np.full_like(work, border_value, dtype=np.uint8)
            pad = kernel.shape[0] // 2
            h, w = work.shape
            
            for i in range(pad, h - pad):
                for j in range(pad, w - pad):
                    roi = work[i-pad:i+pad+1, j-pad:j+pad+1]
                    # Erosion: min of roi where kernel == 1
                    result[i, j] = np.min(roi[kernel == 1])
        
        elif border_type == "BORDER_CONSTANT":
            # Add border before morphologyEx
            pad = kernel.shape[0] // 2
            padded = cv2.copyMakeBorder(
                work, pad, pad, pad, pad,
                cv2.BORDER_CONSTANT, value=float(border_value)
            )
            temp = cv2.morphologyEx(padded, cv2.MORPH_ERODE, kernel)
            result = temp[pad:-pad, pad:-pad]
        
        else:  # BORDER_REFLECT
            cv_border = cv2.BORDER_REFLECT
            result = cv2.morphologyEx(work, cv2.MORPH_ERODE, kernel, 
                                     borderType=cv_border)

        return (result // 255).astype(np.uint8) if is_01 else result

    @staticmethod
    def dilate(image: np.ndarray, kernel: np.ndarray,
               border_type: str = "BORDER_REFLECT", border_value: int = 0) -> np.ndarray:
        """
        Dylacja obrazu binarnego z podanym elementem strukturyzującym.
        Działa dla maski 0/255 i 0/1 — wynik ma ten sam zakres co wejście.
        
        Parameters
        ----------
        image        : obraz binarny (0/255 lub 0/1)
        kernel       : element strukturyzujący (0/1)
        border_type  : "BORDER_CONSTANT" | "BORDER_REFLECT" | "Wypełnienie wyniku stałą"
        border_value : wartość dla BORDER_CONSTANT / wypełnienia (0-255)
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)

        kernel = kernel.astype(np.uint8)
        is_01 = CustomMorphologyOperations._is_01_mask(image)

        # Normalize to 0/255 for morphologyEx
        work = image * 255 if is_01 else image
        
        # Handle border types
        if border_type == "Wypełnienie wyniku stałą":
            # Fill result with constant, compute only interior
            result = np.full_like(work, border_value, dtype=np.uint8)
            pad = kernel.shape[0] // 2
            h, w = work.shape
            
            for i in range(pad, h - pad):
                for j in range(pad, w - pad):
                    roi = work[i-pad:i+pad+1, j-pad:j+pad+1]
                    # Dilation: max of roi where kernel == 1
                    result[i, j] = np.max(roi[kernel == 1])
        
        elif border_type == "BORDER_CONSTANT":
            # Add border before morphologyEx
            pad = kernel.shape[0] // 2
            padded = cv2.copyMakeBorder(
                work, pad, pad, pad, pad,
                cv2.BORDER_CONSTANT, value=float(border_value)
            )
            temp = cv2.morphologyEx(padded, cv2.MORPH_DILATE, kernel)
            result = temp[pad:-pad, pad:-pad]
        
        else:  # BORDER_REFLECT
            cv_border = cv2.BORDER_REFLECT
            result = cv2.morphologyEx(work, cv2.MORPH_DILATE, kernel,
                                     borderType=cv_border)

        return (result // 255).astype(np.uint8) if is_01 else result