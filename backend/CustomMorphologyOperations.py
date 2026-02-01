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
        Sprawdza, czy obraz jest binarny (jedynie wartości 0 i 255).
        Rzuca ValueError z czytelną wiadomością jeśli nie jest.
        """
        if image.ndim != 2:
            raise ValueError(
                "Obraz nie jest jednokanalowy.\n"
                "Wymagany obraz w skali szarości (2D)."
            )

        unique = np.unique(image)
        # dopuszczamy {0}, {255}, {0, 255}
        allowed = {0, 255}
        if not set(unique.tolist()).issubset(allowed):
            raise ValueError(
                "Obraz nie jest binarny.\n\n"
                "Dozwolone wartości pikselów: 0 i 255.\n"
                f"Znalezione wartości: {sorted(unique.tolist())}\n\n"
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

    # ─── operacje ─────────────────────────────────────────────────────────

    @staticmethod
    def erode(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Erozja obrazu binarnego z podanym elementem strukturyzującym.

        Parameters
        ----------
        image  : np.ndarray, shape (H, W), dtype uint8 — obraz binarny (0/255)
        kernel : np.ndarray, shape (kH, kW), dtype uint8 — element strukturyzujący (0/1)

        Returns
        -------
        np.ndarray — wynik erozji
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)

        kernel = kernel.astype(np.uint8)
        result = cv2.morphologyEx(image, cv2.MORPH_ERODE, kernel)
        return result

    @staticmethod
    def dilate(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Dylacja obrazu binarnego z podanym elementem strukturyzującym.

        Parameters
        ----------
        image  : np.ndarray, shape (H, W), dtype uint8 — obraz binarny (0/255)
        kernel : np.ndarray, shape (kH, kW), dtype uint8 — element strukturyzujący (0/1)

        Returns
        -------
        np.ndarray — wynik dylacji
        """
        CustomMorphologyOperations._validate_binary(image)
        CustomMorphologyOperations._validate_kernel(kernel)

        kernel = kernel.astype(np.uint8)
        result = cv2.morphologyEx(image, cv2.MORPH_DILATE, kernel)
        return result