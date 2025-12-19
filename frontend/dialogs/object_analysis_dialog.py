"""
Dialog do analizy wielu obiektów - Lab 4
Prosty interfejs z tabelą wyników
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import cv2
from typing import Callable
from PIL import Image, ImageTk


class ObjectAnalysisDialog:
    """Dialog do analizy wielu obiektów"""
    
    def __init__(self, parent, image: np.ndarray, app_manager):
        self.parent = parent
        self.image = image.copy()
        self.app_manager = app_manager
        self.objects_data = []
        self.preview_image = None
        self.on_result_callback: Callable = None
        
        # Sprawdź czy obraz jest binarny
        unique_vals = np.unique(image)
        if not (len(unique_vals) <= 2 and (unique_vals.max() == 255 or unique_vals.max() == 1)):
            raise ValueError("Obraz musi być binarny!")
        
        self._create_dialog()
        self._perform_analysis()
        
    def _create_dialog(self):
        """Tworzy okno dialogowe"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Analiza wielu obiektów")
        self.dialog.geometry("1000x700")
        
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tytuł
        ttk.Label(main_frame, text="Analiza obiektów na obrazie binarnym",
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Podgląd z konturami
        preview_frame = ttk.LabelFrame(main_frame, text="Preview z konturami", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(preview_frame, bg='black', height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info
        self.info_label = ttk.Label(main_frame, text="Analizowanie...",
                                    font=('Arial', 10))
        self.info_label.pack(pady=(0, 5))
        
        # Tabela
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ('ID', 'Pole', 'Obwód', 'AspectRatio', 'Extent', 'Solidity', 'EquivDiam', 'M1', 'M2', 'M3')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Pole', text='Pole')
        self.tree.heading('Obwód', text='Obwód')
        self.tree.heading('AspectRatio', text='AspectRatio')
        self.tree.heading('Extent', text='Extent')
        self.tree.heading('Solidity', text='Solidity')
        self.tree.heading('EquivDiam', text='EquivDiam')
        self.tree.heading('M1', text='M1')
        self.tree.heading('M2', text='M2')
        self.tree.heading('M3', text='M3')
        
        self.tree.column('ID', width=40)
        self.tree.column('Pole', width=80)
        self.tree.column('Obwód', width=80)
        self.tree.column('AspectRatio', width=90)
        self.tree.column('Extent', width=70)
        self.tree.column('Solidity', width=70)
        self.tree.column('EquivDiam', width=80)
        self.tree.column('M1', width=90)
        self.tree.column('M2', width=90)
        self.tree.column('M3', width=90)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Zapisz do CSV", 
                  command=self._save_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zapisz preview", 
                  command=self._save_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Pokaż preview w oknie", 
                  command=self._show_in_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zamknij", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
    def _perform_analysis(self):
        """Wykonuje analizę"""
        from backend.ObjectAnalysis import ObjectAnalysis
        
        try:
            self.objects_data, self.preview_image = ObjectAnalysis.analyze_objects(self.image)
            
            # Wyświetl preview
            self._display_preview()
            
            # Info
            self.info_label.config(
                text=f"Znaleziono {len(self.objects_data)} obiektów"
            )
            
            # Tabela
            self._fill_table()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd analizy: {str(e)}")
            self.dialog.destroy()
    
    def _display_preview(self):
        """Wyświetla preview na canvas"""
        if self.preview_image is None:
            return
        
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10:
            canvas_width = 800
        if canvas_height < 10:
            canvas_height = 300
        
        # Skaluj
        h, w = self.preview_image.shape[:2]
        scale = min(canvas_width / w, canvas_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        resized = cv2.resize(self.preview_image, (new_w, new_h))
        
        # BGR -> RGB
        resized_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(resized_rgb)
        
        photo = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                image=photo, anchor=tk.CENTER)
        self.canvas.image = photo
    
    def _fill_table(self):
        """Wypełnia tabelę"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Sortuj według pola
        sorted_objs = sorted(self.objects_data, key=lambda x: x['area'], reverse=True)
        
        for obj in sorted_objs:
            self.tree.insert('', 'end', values=(
                obj['id'],
                f"{obj['area']:.1f}",
                f"{obj['perimeter']:.1f}",
                f"{obj['aspect_ratio']:.3f}",
                f"{obj['extent']:.3f}",
                f"{obj['solidity']:.3f}",
                f"{obj['equivalent_diameter']:.1f}",
                f"{obj['M1']:.4f}",
                f"{obj['M2']:.4f}",
                f"{obj['M3']:.4f}"
            ))
    
    def _save_csv(self):
        """Zapisz do CSV"""
        if not self.objects_data:
            messagebox.showwarning("Uwaga", "Brak danych")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            from backend.ObjectAnalysis import ObjectAnalysis
            ObjectAnalysis.save_to_csv(self.objects_data, filename)
            messagebox.showinfo("Sukces", f"Zapisano do: {filename}")
    
    def _save_preview(self):
        """Zapisz preview"""
        if self.preview_image is None:
            messagebox.showwarning("Uwaga", "Brak preview")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            cv2.imwrite(filename, self.preview_image)
            messagebox.showinfo("Sukces", f"Zapisano: {filename}")
    
    def _show_in_window(self):
        """Pokaż preview w nowym oknie"""
        if self.preview_image is None:
            messagebox.showwarning("Uwaga", "Brak preview")
            return
        
        if self.on_result_callback:
            self.on_result_callback(self.preview_image)