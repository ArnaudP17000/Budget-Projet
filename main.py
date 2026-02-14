"""
Budget Management Application - Main Entry Point
Application de Gestion Budgétaire
"""
import customtkinter as ctk
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
import sys


def main():
    """Initialize and run the Budget Management Application."""
    try:
        print("🔄 Initialisation de la base de données...")
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        print("✅ Base de données prête")
        
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        print("🚀 Lancement de l'application...")
        app = MainWindow()
        app.mainloop()
        
    except Exception as e:
        print(f"❌ Erreur au démarrage: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
