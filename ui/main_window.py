"""
Main Window - Application principale avec navigation latérale.
"""
import customtkinter as ctk
from typing import Optional
from database.db_manager import DatabaseManager
from utils.constants import COLOR_PRIMARY, COLOR_BG_DARK, COLOR_BG_CARD


class MainWindow(ctk.CTk):
    """Main application window with sidebar navigation."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Window configuration
        self.title("Budget Management - Gestion Budgétaire")
        self.geometry("1400x800")
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Track active button
        self.active_button = None
        self.current_view = None
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar and main content area
        self.create_sidebar()
        self.create_main_content_area()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_sidebar(self):
        """Create the sidebar with navigation buttons."""
        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLOR_BG_DARK)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(11, weight=1)
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="💰 Budget Projet",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 40))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("💰 Budgets", self.show_budgets),
            ("📄 Contrats", self.show_contrats),
            ("🛒 Bons de Commande", self.show_bons_commande),
            ("📁 Projets", self.show_projets),
            ("👥 Clients", self.show_clients),
            ("👤 Contacts", self.show_contacts),
            ("✅ To-Do List", self.show_todo),
            ("💾 Sauvegarde", self.show_sauvegarde),
        ]
        
        for idx, (text, command) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=command,
                width=210,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color="gray70",
                hover_color=COLOR_BG_CARD,
                anchor="w",
                corner_radius=8
            )
            btn.grid(row=idx, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[text] = btn
        
        # Version label at bottom
        version_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray50"
        )
        version_label.grid(row=12, column=0, padx=20, pady=(0, 20))
    
    def create_main_content_area(self):
        """Create the main content area."""
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG_DARK)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
    
    def clear_main_content(self):
        """Clear the main content area."""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        self.current_view = None
    
    def set_active_button(self, button_text: str):
        """Highlight the active navigation button."""
        # Reset all buttons
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", text_color="gray70")
        
        # Highlight active button
        if button_text in self.nav_buttons:
            self.nav_buttons[button_text].configure(
                fg_color=COLOR_PRIMARY,
                text_color="white"
            )
    
    def show_dashboard(self):
        """Show the dashboard view."""
        from ui.dashboard import DashboardView
        self.clear_main_content()
        self.set_active_button("📊 Dashboard")
        self.current_view = DashboardView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_budgets(self):
        """Show the budgets view."""
        from ui.budgets_view import BudgetsView
        self.clear_main_content()
        self.set_active_button("💰 Budgets")
        self.current_view = BudgetsView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_contrats(self):
        """Show the contracts view."""
        from ui.contrats_view import ContratsView
        self.clear_main_content()
        self.set_active_button("📄 Contrats")
        self.current_view = ContratsView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_bons_commande(self):
        """Show the purchase orders view."""
        from ui.bons_commande_view import BonsCommandeView
        self.clear_main_content()
        self.set_active_button("🛒 Bons de Commande")
        self.current_view = BonsCommandeView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_projets(self):
        """Show the projects view."""
        from ui.projets_view import ProjetsView
        self.clear_main_content()
        self.set_active_button("📁 Projets")
        self.current_view = ProjetsView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_clients(self):
        """Show the clients view."""
        from ui.clients_view import ClientsView
        self.clear_main_content()
        self.set_active_button("👥 Clients")
        self.current_view = ClientsView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_contacts(self):
        """Show the contacts view."""
        from ui.contacts_view import ContactsView
        self.clear_main_content()
        self.set_active_button("👤 Contacts")
        self.current_view = ContactsView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_todo(self):
        """Show the to-do list view."""
        from ui.todo_view import TodoView
        self.clear_main_content()
        self.set_active_button("✅ To-Do List")
        self.current_view = TodoView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
    
    def show_sauvegarde(self):
        """Show the backup/restore view."""
        from ui.sauvegarde_view import SauvegardeView
        self.clear_main_content()
        self.set_active_button("💾 Sauvegarde")
        self.current_view = SauvegardeView(self.main_content, self.db_manager)
        self.current_view.pack(fill="both", expand=True)
