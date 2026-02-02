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
    def erode(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Erozja obrazu binarnego z podanym elementem strukturyzującym.
        Działa dla maski 0/255 i 0/1 — wynik ma ten sam zakres co wejście.
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)

        kernel = kernel.astype(np.uint8)
        is_01 = CustomMorphologyOperations._is_01_mask(image)

        work = image * 255 if is_01 else image
        result = cv2.morphologyEx(work, cv2.MORPH_ERODE, kernel)

        return (result // 255).astype(np.uint8) if is_01 else result

    @staticmethod
    def dilate(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Dylacja obrazu binarnego z podanym elementem strukturyzującym.
        Działa dla maski 0/255 i 0/1 — wynik ma ten sam zakres co wejście.
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)

        kernel = kernel.astype(np.uint8)
        is_01 = CustomMorphologyOperations._is_01_mask(image)

        work = image * 255 if is_01 else image
        result = cv2.morphologyEx(work, cv2.MORPH_DILATE, kernel)

        return (result // 255).astype(np.uint8) if is_01 else result