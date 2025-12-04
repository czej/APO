import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import cv2
import numpy as np


class StretchDialog(tk.Toplevel):
    """Dialog do rozciągania histogramu"""
    
    def __init__(self, parent, img, app_manager):
        """
        Parametry:
            parent: okno rodzica
            img: obraz numpy.ndarray (grayscale)
            app_manager: instancja AppManager
        """
        super().__init__(parent)
        
        self.img = img
        self.app_manager = app_manager
        self.on_result_callback = None
        
        self.title("Enhance Contrast - Histogram Stretching")
        self.geometry("800x650")
        
        self._create_ui()
        
    def _create_ui(self):
        """Tworzy interfejs dialogu"""
        # Nagłówek
        header_frame = tk.Frame(self, bg="#f0f0f0", height=50)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Histogram Stretching - Enhance Contrast",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        ).pack(pady=12)
        
        # Main content with two columns
        content_frame = tk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column - histograms
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Original histogram
        tk.Label(
            left_frame,
            text="Original Histogram",
            font=("Arial", 10, "bold")
        ).pack(pady=(0, 5))
        
        self.fig_orig = Figure(figsize=(5, 2.5))
        self.ax_orig = self.fig_orig.add_subplot(111)
        
        histogram_stats = self.app_manager.calculate_histograms(self.img)
        self.hist_data = histogram_stats[0].histogram
        
        x = np.arange(256)
        self.ax_orig.bar(x, self.hist_data, color='gray', width=1.0, alpha=0.7, edgecolor='none')
        self.ax_orig.set_xlim(0, 255)
        self.ax_orig.set_ylabel("Frequency", fontsize=8)
        self.ax_orig.tick_params(labelsize=8)
        
        canvas_orig = FigureCanvasTkAgg(self.fig_orig, master=left_frame)
        canvas_orig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Stretched histogram preview
        tk.Label(
            left_frame,
            text="Stretched Histogram (Preview)",
            font=("Arial", 10, "bold")
        ).pack(pady=(10, 5))
        
        self.fig_stretched = Figure(figsize=(5, 2.5))
        self.ax_stretched = self.fig_stretched.add_subplot(111)
        
        self.canvas_stretched = FigureCanvasTkAgg(self.fig_stretched, master=left_frame)
        self.canvas_stretched.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Right column - controls
        right_frame = tk.Frame(content_frame, width=250)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Saturation options
        tk.Label(
            right_frame,
            text="Saturation Options",
            font=("Arial", 10, "bold")
        ).pack(pady=(10, 10))
        
        tk.Label(
            right_frame,
            text="Clip percentage:",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10)
        
        self.saturation_var = tk.DoubleVar(value=0)
        
        options = [
            ("No saturation (0%)", 0),
            ("1% saturation", 1),
            ("2% saturation", 2),
            ("5% saturation (max)", 5)
        ]
        
        for text, val in options:
            tk.Radiobutton(
                right_frame,
                text=text,
                variable=self.saturation_var,
                value=val,
                command=self._update_preview
            ).pack(anchor="w", padx=20, pady=3)
        
        # Info box
        info_frame = tk.LabelFrame(right_frame, text="Info", font=("Arial", 9, "bold"))
        info_frame.pack(pady=20, padx=10, fill=tk.X)
        
        info_text = (
            "Histogram stretching enhances\n"
            "contrast by expanding the range\n"
            "of intensity values.\n\n"
            "• 0% = use min/max values\n"
            "• 1-5% = clip outliers for\n"
            "  better contrast"
        )
        
        tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 8),
            justify=tk.LEFT,
            fg="#444"
        ).pack(padx=10, pady=10, anchor="w")
        
        # Statistics
        stats_frame = tk.LabelFrame(right_frame, text="Statistics", font=("Arial", 9, "bold"))
        stats_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Courier", 8),
            justify=tk.LEFT,
            anchor="w"
        )
        self.stats_label.pack(padx=10, pady=10, anchor="w")
        self._update_stats()
        
        # Preview checkbox
        self.preview_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            right_frame,
            text="Auto preview",
            variable=self.preview_var,
            command=self._update_preview
        ).pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=15)
        
        tk.Button(
            button_frame,
            text="Apply",
            command=self._apply,
            width=12,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Reset",
            command=self._reset,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Initial preview
        self._update_preview()
        
    def _update_preview(self):
        """Aktualizuje podgląd rozciągniętego histogramu"""
        if not self.preview_var.get():
            return
        
        saturation = self.saturation_var.get()
        result = self.app_manager.apply_stretch_histogram(self.img, saturation)
        
        # Oblicz histogram wyniku
        hist_result = np.zeros(256, dtype=int)
        for pixel in result.flat:
            hist_result[pixel] += 1
        
        # Aktualizuj wykres
        self.ax_stretched.clear()
        x = np.arange(256)
        self.ax_stretched.bar(x, hist_result, color='blue', width=1.0, alpha=0.7, edgecolor='none')
        self.ax_stretched.set_xlim(0, 255)
        self.ax_stretched.set_ylabel("Frequency", fontsize=8)
        self.ax_stretched.tick_params(labelsize=8)
        
        self.canvas_stretched.draw()
        
        # Aktualizuj statystyki
        self._update_stats(result)
        
    def _update_stats(self, result=None):
        """Aktualizuje statystyki"""
        orig_min = np.min(self.img)
        orig_max = np.max(self.img)
        orig_mean = np.mean(self.img)
        
        stats_text = f"Original:\n"
        stats_text += f"  Min: {orig_min:3d}\n"
        stats_text += f"  Max: {orig_max:3d}\n"
        stats_text += f"  Mean: {orig_mean:.1f}\n"
        
        if result is not None:
            result_min = np.min(result)
            result_max = np.max(result)
            result_mean = np.mean(result)
            
            stats_text += f"\nStretched:\n"
            stats_text += f"  Min: {result_min:3d}\n"
            stats_text += f"  Max: {result_max:3d}\n"
            stats_text += f"  Mean: {result_mean:.1f}"
        
        self.stats_label.config(text=stats_text)
        
    def _reset(self):
        """Resetuje do wartości domyślnych"""
        self.saturation_var.set(0)
        self._update_preview()
        
    def _apply(self):
        """Zastosuj rozciąganie histogramu"""
        try:
            saturation = self.saturation_var.get()
            result = self.app_manager.apply_stretch_histogram(self.img, saturation)
            
            if self.on_result_callback:
                self.on_result_callback(result)
            
            self.destroy()
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e))