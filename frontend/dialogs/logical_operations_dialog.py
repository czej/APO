import tkinter as tk
from tkinter import messagebox


class LogicalOperationsDialog(tk.Toplevel):
    """Dialog do wyboru obrazów dla operacji logicznych"""
    
    def __init__(self, parent, operation, all_images, app_manager):
        """
        Parametry:
            parent: okno rodzica
            operation: "AND", "OR", "XOR"
            all_images: lista wszystkich obrazów
            app_manager: instancja AppManager
        """
        super().__init__(parent)
        
        self.operation = operation
        self.all_images = all_images
        self.app_manager = app_manager
        self.on_result_callback = None
        
        self.title(f"Operacja logiczna {operation}")
        self.geometry("550x500")
        
        self._create_ui()
    
    def _create_ui(self):
        """Tworzy interfejs dialogu"""
        # Nagłówek
        header_frame = tk.Frame(self, bg="#f0f0f0", height=100)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=f"Operacja logiczna {self.operation}",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        ).pack(pady=(15, 5))
        
        tk.Label(
            header_frame,
            text="Wybierz co najmniej 2 obrazy do operacji",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        ).pack(pady=(0, 3))
        
        tk.Label(
            header_frame,
            text="(Ctrl+klik = wielokrotny wybór | Shift+klik = zakres)",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#999"
        ).pack(pady=(0, 8))
        
        tk.Label(
            header_frame,
            text="⚠ Wszystkie wybrane obrazy muszą mieć identyczny rozmiar i typ",
            font=("Arial", 9, "bold"),
            bg="#f0f0f0",
            fg="#d9534f"
        ).pack()
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Info
        info_frame = tk.LabelFrame(content_frame, text="Informacje o operacji", font=("Arial", 9, "bold"))
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        operation_info = {
            "AND": "Wynik = 1 tylko gdy wszystkie piksele = 1\nDziała bit po bicie: obraz1 AND obraz2 AND obraz3...",
            "OR": "Wynik = 1 gdy co najmniej jeden piksel = 1\nDziała bit po bicie: obraz1 OR obraz2 OR obraz3...",
            "XOR": "Wynik = 1 gdy nieparzysta liczba pikseli = 1\nDziała bit po bicie: obraz1 XOR obraz2 XOR obraz3..."
        }
        
        tk.Label(
            info_frame,
            text=operation_info.get(self.operation, ""),
            font=("Arial", 9),
            justify=tk.LEFT,
            fg="#444"
        ).pack(padx=10, pady=8, anchor="w")
        
        # Lista obrazów
        list_header = tk.Frame(content_frame)
        list_header.pack(fill=tk.X, pady=(5, 5))
        
        tk.Label(
            list_header,
            text=f"Dostępne obrazy (łącznie: {len(self.all_images)}):",
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT)
        
        tk.Label(
            list_header,
            text="Wybierz minimum 2 obrazy",
            font=("Arial", 8),
            fg="#d9534f"
        ).pack(side=tk.RIGHT)
        
        listbox_frame = tk.Frame(content_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 9),
            selectmode=tk.EXTENDED,
            height=12
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Wypełnij listę WSZYSTKIMI obrazami
        for idx, img in enumerate(self.all_images):
            h, w = img.shape[:2]
            img_type = "Gray" if len(img.shape) == 2 else "Color"
            
            text = f"Obraz {idx + 1:2d} | {w:4d}x{h:4d} | {img_type:5s}"
            self.listbox.insert(tk.END, text)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        tk.Button(
            button_frame,
            text="Zastosuj",
            command=self._apply,
            width=12,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Anuluj",
            command=self.destroy,
            width=12
        ).pack(side=tk.LEFT, padx=5)
    
    def _apply(self):
        """Zastosuj operację logiczną"""
        selection = self.listbox.curselection()
        
        # Sprawdź czy wybrano co najmniej 2 obrazy
        if len(selection) < 2:
            messagebox.showwarning(
                "Za mało obrazów",
                f"Wybrano: {len(selection)} obraz(ów)\n\n"
                f"Operacja {self.operation} wymaga co najmniej 2 obrazów.\n\n"
                f"Użyj Ctrl+klik aby wybrać więcej obrazów."
            )
            return
        
        # Pobierz wybrane obrazy
        selected_images = [self.all_images[idx] for idx in selection]
        
        # Sprawdź czy wszystkie obrazy są grayscale
        non_grayscale = []
        for i, img in enumerate(selected_images):
            if len(img.shape) != 2:
                non_grayscale.append(selection[i] + 1)  # +1 dla numeracji od 1
        
        if non_grayscale:
            messagebox.showerror(
                "Błąd: Obrazy kolorowe",
                f"Operacje logiczne wymagają obrazów w skali szarości!\n\n"
                f"Obrazy kolorowe w wyborze: {', '.join(map(str, non_grayscale))}\n\n"
                f"Konwertuj obrazy na skalę szarości:\n"
                f"Obraz → Typ → 8-bit Skala szarości"
            )
            return
        
        # Sprawdź czy wszystkie obrazy mają ten sam rozmiar
        first_shape = selected_images[0].shape
        incompatible = []
        
        for i, img in enumerate(selected_images[1:], start=1):
            if img.shape != first_shape:
                incompatible.append((selection[i] + 1, img.shape))
        
        if incompatible:
            error_msg = f"Wszystkie obrazy muszą mieć identyczny rozmiar!\n\n"
            error_msg += f"Pierwszy wybrany obraz (nr {selection[0] + 1}): {first_shape[1]}x{first_shape[0]}\n\n"
            error_msg += "Niekompatybilne obrazy:\n"
            for img_num, shape in incompatible:
                error_msg += f"  • Obraz {img_num}: {shape[1]}x{shape[0]}\n"
            
            messagebox.showerror("Błąd: Niezgodne rozmiary", error_msg)
            return
        
        # Wszystko OK - wykonaj operację
        try:
            result = selected_images[0]
            
            for img in selected_images[1:]:
                if self.operation == "AND":
                    result = self.app_manager.apply_logical_and(result, img)
                elif self.operation == "OR":
                    result = self.app_manager.apply_logical_or(result, img)
                elif self.operation == "XOR":
                    result = self.app_manager.apply_logical_xor(result, img)
                else:
                    raise ValueError(f"Nieznana operacja: {self.operation}")
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Błąd operacji", str(e))