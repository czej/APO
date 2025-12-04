"""
Image Processing Application
Laboratorium APO 2025/2026

Główny plik uruchomieniowy aplikacji
"""

import tkinter as tk
from frontend.main_window import MainWindow


def main():
    """Uruchamia aplikację"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()