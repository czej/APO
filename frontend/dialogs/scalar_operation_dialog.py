import tkinter as tk
from tkinter import messagebox


class ScalarOperationDialog(tk.Toplevel):
    """Dialog do operacji arytmetycznych z liczbą (dodawanie, mnożenie, dzielenie)"""
    
    def __init__(self, parent, operation, current_image, app_manager):
        """
        Parametry:
            parent: okno rodzica
            operation: "Dodaj", "Pomnóż", "Podziel"
            current_image: aktywny obraz
            app_manager: instancja AppManager
        """
        super().__init__(parent)
        
        self.operation = operation
        self.current_image = current_image
        self.app_manager = app_manager
        self.on_result_callback = None
        
        self.title(f"{operation} przez liczbę")
        self.geometry("450x500")
        
        self._create_ui()
    
    def _create_ui(self):
        """Tworzy interfejs dialogu"""
        # Nagłówek
        header_frame = tk.Frame(self, bg="#f0f0f0", height=80)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=f"{self.operation} przez liczbę całkowitą",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        ).pack(pady=(15, 5))
        
        current_shape = self.current_image.shape
        tk.Label(
            header_frame,
            text=f"Aktywny obraz: {current_shape[1]}x{current_shape[0]} pikseli",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666"
        ).pack(pady=(0, 10))
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Info
        info_map = {
            "Dodaj": "Dodaje stałą wartość do każdego piksela obrazu.\nWynik = piksel + wartość",
            "Pomnóż": "Mnoży każdy piksel przez stałą wartość.\nWynik = piksel × wartość",
            "Podziel": "Dzieli każdy piksel przez stałą wartość.\nWynik = piksel ÷ wartość"
        }
        
        info_frame = tk.LabelFrame(content_frame, text="Informacje", font=("Arial", 9, "bold"))
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            info_frame,
            text=info_map.get(self.operation, ""),
            font=("Arial", 9),
            justify=tk.LEFT,
            fg="#444"
        ).pack(padx=10, pady=8, anchor="w")
        
        # Input dla liczby
        input_frame = tk.Frame(content_frame)
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="Podaj liczbę całkowitą:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        self.scalar_var = tk.IntVar(value=10 if self.operation != "Podziel" else 2)
        
        spinbox = tk.Spinbox(
            input_frame,
            from_=(-255 if self.operation == "Dodaj" else 1),
            to=255,
            textvariable=self.scalar_var,
            width=10,
            font=("Arial", 10)
        )
        spinbox.pack(side=tk.LEFT)
        
        # Opcja wysycenia (tylko dla dodawania i mnożenia)
        if self.operation in ["Dodaj", "Pomnóż"]:
            saturation_frame = tk.LabelFrame(content_frame, text="Tryb wysycenia", font=("Arial", 9, "bold"))
            saturation_frame.pack(fill=tk.X, pady=(10, 0))
            
            self.saturation_var = tk.BooleanVar(value=True)
            
            tk.Radiobutton(
                saturation_frame,
                text="Z wysyceniem (obcięcie do 0-255)",
                variable=self.saturation_var,
                value=True,
                font=("Arial", 9)
            ).pack(anchor="w", padx=20, pady=5)
            
            tk.Radiobutton(
                saturation_frame,
                text="Bez wysycenia (automatyczne skalowanie)",
                variable=self.saturation_var,
                value=False,
                font=("Arial", 9)
            ).pack(anchor="w", padx=20, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        tk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply,
            width=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Anuluj",
            command=self.destroy,
            width=10
        ).pack(side=tk.LEFT, padx=5)
    
    def _apply(self):
        """Zastosuj operację"""
        try:
            scalar = self.scalar_var.get()
            
            if self.operation == "Podziel" and scalar == 0:
                messagebox.showerror("Błąd", "Nie można dzielić przez zero!")
                return
            
            # Wykonaj operację
            if self.operation == "Dodaj":
                saturation = self.saturation_var.get()
                result = self.app_manager.apply_add_scalar(self.current_image, scalar, saturation)
            elif self.operation == "Pomnóż":
                saturation = self.saturation_var.get()
                result = self.app_manager.apply_multiply_scalar(self.current_image, scalar, saturation)
            elif self.operation == "Podziel":
                result = self.app_manager.apply_divide_scalar(self.current_image, scalar)
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Błąd", str(e))