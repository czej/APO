"""
Frontend dialog dla analizy cech obiektów binarnych - Lab 4 Zadanie 1
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from typing import Callable
import os


class FeatureAnalysisDialog:
    """Dialog do analizy cech obiektu binarnego"""
    
    def __init__(self, parent, image: np.ndarray, app_manager):
        self.parent = parent
        self.image = image.copy()
        self.app_manager = app_manager
        self.features = None
        self.on_result_callback: Callable = None
        
        # Sprawdź czy obraz jest binarny
        unique_vals = np.unique(image)
        if not (len(unique_vals) <= 2 and (unique_vals.max() == 255 or unique_vals.max() == 1)):
            raise ValueError("Obraz musi być binarny! Użyj progowania najpierw.")
        
        self._create_dialog()
        self._perform_analysis()
        
    def _create_dialog(self):
        """Tworzy okno dialogowe"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Analiza cech obiektu - Lab 4 Zadanie 1")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        
        # Główny kontener z scrollbarem
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas ze scrollbarem
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Tytuł
        title_label = ttk.Label(scrollable_frame, 
                               text="Analiza składowych wektora cech obiektu binarnego",
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Ramka na wyniki
        self.results_frame = ttk.LabelFrame(scrollable_frame, text="Wyniki analizy", padding=10)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview do wyświetlania wyników
        columns = ('Cecha', 'Wartość')
        self.tree = ttk.Treeview(self.results_frame, columns=columns, show='tree headings', height=20)
        
        self.tree.heading('Cecha', text='Cecha')
        self.tree.heading('Wartość', text='Wartość')
        
        self.tree.column('#0', width=20, stretch=False)
        self.tree.column('Cecha', width=250)
        self.tree.column('Wartość', width=200)
        
        # Scrollbar dla Treeview
        tree_scroll = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Przyciski
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Zapisz do pliku TXT", 
                  command=self._save_to_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zapisz do CSV (Excel)", 
                  command=self._save_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zamknij", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Pakowanie canvas i scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _perform_analysis(self):
        """Wykonuje analizę cech"""
        from backend.FeatureAnalysis import FeatureAnalysis
        
        try:
            # Wykonaj analizę
            self.features = FeatureAnalysis.analyze_binary_object(self.image)
            
            # Wyświetl wyniki
            self._display_results()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas analizy: {str(e)}")
            self.dialog.destroy()
    
    def _display_results(self):
        """Wyświetla wyniki w Treeview"""
        # Wyczyść poprzednie wyniki
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 1. Podstawowe parametry
        basic = self.tree.insert('', 'end', text='', values=('PODSTAWOWE PARAMETRY', ''))
        self.tree.insert(basic, 'end', text='', 
                        values=('Pole powierzchni', f"{self.features['area']:.4f}"))
        self.tree.insert(basic, 'end', text='', 
                        values=('Obwód', f"{self.features['perimeter']:.4f}"))
        self.tree.insert(basic, 'end', text='', 
                        values=('Centroid X', f"{self.features['centroid']['x']:.4f}"))
        self.tree.insert(basic, 'end', text='', 
                        values=('Centroid Y', f"{self.features['centroid']['y']:.4f}"))
        
        # 2. Współczynniki kształtu
        shape = self.tree.insert('', 'end', text='', values=('WSPÓŁCZYNNIKI KSZTAŁTU', ''))
        sc = self.features['shape_coefficients']
        self.tree.insert(shape, 'end', text='', 
                        values=('Aspect Ratio (W/H)', f"{sc['aspectRatio']:.4f}"))
        self.tree.insert(shape, 'end', text='', 
                        values=('Extent (Area/BBox)', f"{sc['extent']:.4f}"))
        self.tree.insert(shape, 'end', text='', 
                        values=('Solidity (Area/Hull)', f"{sc['solidity']:.4f}"))
        self.tree.insert(shape, 'end', text='', 
                        values=('Equivalent Diameter', f"{sc['equivalentDiameter']:.4f}"))
        
        # 3. Momenty surowe
        raw_moments = self.tree.insert('', 'end', text='', values=('MOMENTY SUROWE (m)', ''))
        for key, val in self.features['moments']['raw'].items():
            self.tree.insert(raw_moments, 'end', text='', values=(key, f"{val:.4f}"))
        
        # 4. Momenty centralne
        central_moments = self.tree.insert('', 'end', text='', values=('MOMENTY CENTRALNE (mu)', ''))
        for key, val in self.features['moments']['central'].items():
            self.tree.insert(central_moments, 'end', text='', values=(key, f"{val:.4f}"))
        
        # 5. Momenty znormalizowane
        norm_moments = self.tree.insert('', 'end', text='', values=('MOMENTY ZNORMALIZOWANE (nu)', ''))
        for key, val in self.features['moments']['normalized'].items():
            self.tree.insert(norm_moments, 'end', text='', values=(key, f"{val:.4f}"))
        
        # Rozwiń wszystkie kategorie
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
    
    def _save_to_txt(self):
        """Zapisuje wyniki do pliku TXT"""
        if self.features is None:
            messagebox.showwarning("Uwaga", "Brak wyników do zapisania")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="feature_analysis.txt"
        )
        
        if filename:
            try:
                from backend.FeatureAnalysis import FeatureAnalysis
                FeatureAnalysis.save_features_to_file(self.features, filename)
                messagebox.showinfo("Sukces", f"Wyniki zapisane do:\n{filename}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd zapisu: {str(e)}")
    
    def _save_to_csv(self):
        """Zapisuje wyniki do pliku CSV (format Excel)"""
        if self.features is None:
            messagebox.showwarning("Uwaga", "Brak wyników do zapisania")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="feature_analysis.csv"
        )
        
        if filename:
            try:
                from backend.FeatureAnalysis import FeatureAnalysis
                # Zapisz jako listę z jednym obiektem
                FeatureAnalysis.save_features_to_csv([self.features], filename)
                messagebox.showinfo("Sukces", 
                                  f"Wyniki zapisane do:\n{filename}\n\n"
                                  "Plik można otworzyć w Excel (separator: Tab)")
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd zapisu: {str(e)}")


class MultiObjectFeatureDialog:
    """Dialog do analizy cech wielu obiektów na obrazie"""
    
    def __init__(self, parent, image: np.ndarray, app_manager):
        self.parent = parent
        self.image = image.copy()
        self.app_manager = app_manager
        self.features_list = []
        self.on_result_callback: Callable = None
        
        # Sprawdź czy obraz jest binarny
        unique_vals = np.unique(image)
        if not (len(unique_vals) <= 2 and (unique_vals.max() == 255 or unique_vals.max() == 1)):
            raise ValueError("Obraz musi być binarny! Użyj progowania najpierw.")
        
        self._create_dialog()
        self._perform_analysis()
        
    def _create_dialog(self):
        """Tworzy okno dialogowe"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Analiza wielu obiektów - Lab 4 Zadanie 1")
        self.dialog.geometry("900x600")
        
        # Główny kontener
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tytuł
        title_label = ttk.Label(main_frame, 
                               text="Analiza cech wielu obiektów binarnych",
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Info
        info_label = ttk.Label(main_frame, 
                              text="Wykryto następujące obiekty (posortowane wg. wielkości):",
                              font=('Arial', 9))
        info_label.pack(pady=(0, 5))
        
        # Treeview
        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Area', 'Perimeter', 'AspectRatio', 'Extent', 'Solidity', 'EquivDiam')
        self.tree = ttk.Treeview(self.results_frame, columns=columns, show='headings', height=15)
        
        # Nagłówki
        self.tree.heading('ID', text='ID')
        self.tree.heading('Area', text='Pole')
        self.tree.heading('Perimeter', text='Obwód')
        self.tree.heading('AspectRatio', text='Aspect Ratio')
        self.tree.heading('Extent', text='Extent')
        self.tree.heading('Solidity', text='Solidity')
        self.tree.heading('EquivDiam', text='Equiv. Diam.')
        
        # Szerokości kolumn
        self.tree.column('ID', width=50)
        self.tree.column('Area', width=100)
        self.tree.column('Perimeter', width=100)
        self.tree.column('AspectRatio', width=100)
        self.tree.column('Extent', width=100)
        self.tree.column('Solidity', width=100)
        self.tree.column('EquivDiam', width=120)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.count_label = ttk.Label(button_frame, text="", font=('Arial', 9, 'bold'))
        self.count_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Zapisz wszystkie do CSV", 
                  command=self._save_all_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zamknij", 
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _perform_analysis(self):
        """Wykonuje analizę wszystkich obiektów"""
        import cv2
        from backend.FeatureAnalysis import FeatureAnalysis
        
        try:
            # Upewnij się że obraz jest w formacie uint8
            img = self.image.copy()
            if img.max() == 1:
                img = img * 255
            img = img.astype(np.uint8)
            
            # Znajdź wszystkie kontury
            contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Dla każdego konturu, utwórz osobny obraz binarny i analizuj
            for idx, cnt in enumerate(contours):
                # Pomiń bardzo małe obiekty (szum)
                if cv2.contourArea(cnt) < 10:
                    continue
                
                # Utwórz maskę dla tego obiektu
                mask = np.zeros_like(img)
                cv2.drawContours(mask, [cnt], -1, 255, -1)
                
                # Analizuj
                features = FeatureAnalysis.analyze_binary_object(mask)
                self.features_list.append(features)
            
            # Sortuj według pola (malejąco)
            self.features_list.sort(key=lambda x: x['area'], reverse=True)
            
            # Wyświetl wyniki
            self._display_results()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas analizy: {str(e)}")
            self.dialog.destroy()
    
    def _display_results(self):
        """Wyświetla wyniki w tabeli"""
        # Wyczyść
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Dodaj każdy obiekt
        for idx, feat in enumerate(self.features_list, 1):
            sc = feat['shape_coefficients']
            self.tree.insert('', 'end', values=(
                idx,
                f"{feat['area']:.2f}",
                f"{feat['perimeter']:.2f}",
                f"{sc['aspectRatio']:.3f}",
                f"{sc['extent']:.3f}",
                f"{sc['solidity']:.3f}",
                f"{sc['equivalentDiameter']:.2f}"
            ))
        
        # Aktualizuj liczbę obiektów
        self.count_label.config(text=f"Znaleziono obiektów: {len(self.features_list)}")
    
    def _save_all_to_csv(self):
        """Zapisuje wszystkie obiekty do CSV"""
        if not self.features_list:
            messagebox.showwarning("Uwaga", "Brak obiektów do zapisania")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="multi_object_analysis.csv"
        )
        
        if filename:
            try:
                from backend.FeatureAnalysis import FeatureAnalysis
                FeatureAnalysis.save_features_to_csv(self.features_list, filename)
                messagebox.showinfo("Sukces", 
                                  f"Zapisano {len(self.features_list)} obiektów do:\n{filename}\n\n"
                                  "Plik można otworzyć w Excel (separator: Tab)")
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd zapisu: {str(e)}")