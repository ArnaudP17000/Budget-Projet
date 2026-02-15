"""
Budgets View - Gestion complète des budgets.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Optional
from database.db_manager import DatabaseManager
from business.budget_manager import BudgetManager
from business.client_manager import ClientManager
from database.models import Budget
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD, NATURES_BUDGET, NATURE_FONCTIONNEMENT, NATURE_INVESTISSEMENT
)
from utils.formatters import format_montant
from utils.validators import validate_montant, validate_annee, validate_required_field


class BudgetsView(ctk.CTkFrame):
    """Budgets management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize budgets view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.budget_manager = BudgetManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        
        self.create_widgets()
        self.load_budgets()
    
    def create_widgets(self):
        """Create view widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header with title and actions
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="💰 Gestion des Budgets",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        new_btn = ctk.CTkButton(
            header_frame,
            text="➕ Nouveau Budget",
            command=self.show_create_dialog,
            width=180,
            height=36,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        new_btn.grid(row=0, column=2, padx=5)
        
        report_btn = ctk.CTkButton(
            header_frame,
            text="📊 Reporter budgets N → N+1",
            command=self.show_report_dialog,
            width=220,
            height=36,
            fg_color=COLOR_WARNING,
            hover_color=COLOR_PRIMARY
        )
        report_btn.grid(row=0, column=3, padx=5)
        
        # Filters
        filter_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=8)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            filter_frame,
            text="🔍 Filtres:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(10, 20))
        
        ctk.CTkLabel(filter_frame, text="Année:").pack(side="left", padx=(0, 5))
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 2, current_year + 3)]
        self.year_filter = ctk.CTkComboBox(
            filter_frame,
            values=years,
            width=100,
            command=lambda _: self.load_budgets()
        )
        self.year_filter.set(str(current_year))
        self.year_filter.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Nature:").pack(side="left", padx=(20, 5))
        self.nature_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Tous"] + NATURES_BUDGET,
            width=150,
            command=lambda _: self.load_budgets()
        )
        self.nature_filter.set("Tous")
        self.nature_filter.pack(side="left", padx=5)
        
        # Scrollable frame for budgets
        self.budgets_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.budgets_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.budgets_scroll.grid_columnconfigure(0, weight=1)
    
    def load_budgets(self):
        """Load and display budgets."""
        # Clear existing
        for widget in self.budgets_scroll.winfo_children():
            widget.destroy()
        
        # Force update
        self.budgets_scroll.update_idletasks()
        
        # Get filters
        try:
            year = int(self.year_filter.get())
        except:
            year = datetime.now().year
        
        nature = self.nature_filter.get()
        if nature == "Tous":
            nature = None
        
        # Load budgets
        budgets = self.budget_manager.get_all_budgets(annee=year, nature=nature)
        
        if not budgets:
            no_data_label = ctk.CTkLabel(
                self.budgets_scroll,
                text="Aucun budget trouvé",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            )
            no_data_label.pack(pady=50)
            return
        
        # Display budgets
        for budget in budgets:
            self.create_budget_card(budget)
        
        # Force final update
        self.update_idletasks()
    
    def create_budget_card(self, budget: Budget):
        """Create a budget card."""
        card = ctk.CTkFrame(self.budgets_scroll, fg_color=COLOR_BG_CARD, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=15)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Client and nature
        client_label = ctk.CTkLabel(
            info_frame,
            text=f"🏢 {self.get_client_name(budget.client_id)}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        client_label.grid(row=0, column=0, sticky="w", pady=5)
        
        nature_color = COLOR_PRIMARY if budget.nature == NATURE_FONCTIONNEMENT else COLOR_SUCCESS
        nature_label = ctk.CTkLabel(
            info_frame,
            text=budget.nature,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=nature_color
        )
        nature_label.grid(row=0, column=1, sticky="e", pady=5)
        
        # Year and service
        year_label = ctk.CTkLabel(
            info_frame,
            text=f"📅 Année: {budget.annee}",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        year_label.grid(row=1, column=0, sticky="w", pady=2)
        
        if budget.service_demandeur:
            service_label = ctk.CTkLabel(
                info_frame,
                text=f"🏛️ {budget.service_demandeur}",
                font=ctk.CTkFont(size=14),
                text_color="gray70"
            )
            service_label.grid(row=1, column=1, sticky="e", pady=2)
        
        # Amounts frame
        amounts_frame = ctk.CTkFrame(card, fg_color="transparent")
        amounts_frame.pack(fill="x", padx=15, pady=(0, 10))
        amounts_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Initial amount
        initial_frame = ctk.CTkFrame(amounts_frame, fg_color=COLOR_BG_CARD, corner_radius=5)
        initial_frame.grid(row=0, column=0, sticky="ew", padx=5)
        
        ctk.CTkLabel(
            initial_frame,
            text="Initial",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        ).pack(pady=(5, 0))
        
        ctk.CTkLabel(
            initial_frame,
            text=format_montant(budget.montant_initial),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(pady=(0, 5))
        
        # Consumed amount
        consumed_frame = ctk.CTkFrame(amounts_frame, fg_color=COLOR_BG_CARD, corner_radius=5)
        consumed_frame.grid(row=0, column=1, sticky="ew", padx=5)
        
        ctk.CTkLabel(
            consumed_frame,
            text="Consommé",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        ).pack(pady=(5, 0))
        
        ctk.CTkLabel(
            consumed_frame,
            text=format_montant(budget.montant_consomme),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_WARNING
        ).pack(pady=(0, 5))
        
        # Available amount
        available_frame = ctk.CTkFrame(amounts_frame, fg_color=COLOR_BG_CARD, corner_radius=5)
        available_frame.grid(row=0, column=2, sticky="ew", padx=5)
        
        ctk.CTkLabel(
            available_frame,
            text="Disponible",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        ).pack(pady=(5, 0))
        
        available_color = COLOR_SUCCESS if budget.montant_disponible > 0 else COLOR_DANGER
        ctk.CTkLabel(
            available_frame,
            text=format_montant(budget.montant_disponible),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=available_color
        ).pack(pady=(0, 5))
        
        # Progress bar
        progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        percentage = (budget.montant_consomme / budget.montant_initial * 100) if budget.montant_initial > 0 else 0
        
        progress = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=20,
            corner_radius=10
        )
        progress.pack(fill="x")
        progress.set(percentage / 100)
        
        # Progress color based on percentage
        if percentage >= 90:
            progress.configure(progress_color=COLOR_DANGER)
        elif percentage >= 70:
            progress.configure(progress_color=COLOR_WARNING)
        else:
            progress.configure(progress_color=COLOR_SUCCESS)
        
        percentage_label = ctk.CTkLabel(
            progress_frame,
            text=f"{percentage:.1f}%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        percentage_label.pack(pady=2)
        
        # Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️ Modifier",
            command=lambda: self.show_edit_dialog(budget),
            width=120,
            height=32,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Supprimer",
            command=lambda: self.delete_budget(budget),
            width=120,
            height=32,
            fg_color=COLOR_DANGER,
            hover_color="#cc0000"
        )
        delete_btn.pack(side="left", padx=5)
    
    def get_client_name(self, client_id: int) -> str:
        """Get client name by ID."""
        client = self.client_manager.get_client_by_id(client_id)
        return client.nom if client else "Inconnu"
    
    def show_create_dialog(self):
        """Show dialog to create a new budget."""
        dialog = BudgetDialog(self, self.db_manager, None)
        self.wait_window(dialog)
        if dialog.result:
            # Force reload with a small delay to ensure dialog is fully closed
            self.after(50, self.load_budgets)
    
    def show_edit_dialog(self, budget: Budget):
        """Show dialog to edit a budget."""
        dialog = BudgetDialog(self, self.db_manager, budget)
        self.wait_window(dialog)
        if dialog.result:
            # Force reload with a small delay
            self.after(50, self.load_budgets)
    
    def delete_budget(self, budget: Budget):
        """Delete a budget."""
        confirm = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce budget ?\n\n"
            f"Client: {self.get_client_name(budget.client_id)}\n"
            f"Année: {budget.annee}\n"
            f"Nature: {budget.nature}"
        )
        
        if confirm:
            success, message = self.budget_manager.delete_budget(budget.id)
            if success:
                messagebox.showinfo("Succès", message)
                self.load_budgets()
            else:
                messagebox.showerror("Erreur", message)
    
    def show_report_dialog(self):
        """Show dialog to report budgets from year N to N+1."""
        messagebox.showinfo("Information", "Fonctionnalité à venir")


class BudgetDialog(ctk.CTkToplevel):
    """Dialog for creating/editing budgets."""
    
    def __init__(self, parent, db_manager: DatabaseManager, budget: Optional[Budget] = None):
        """Initialize dialog."""
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.budget_manager = BudgetManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        self.budget = budget
        self.result = False
        
        # Window configuration
        self.title("Modifier le budget" if budget else "Nouveau budget")
        self.geometry("500x550")
        self.resizable(False, True)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f"500x450+{x}+{y}")
        
        self.create_widgets()
        
        if budget:
            self.load_budget_data()
        
        # Focus on first field
        self.after(100, lambda: self.client_combo.focus())
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Client
        ctk.CTkLabel(
            main_frame,
            text="Client *",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        clients = self.client_manager.get_all_clients()
        client_names = [c.nom for c in clients if c.actif]
        
        self.client_combo = ctk.CTkComboBox(
            main_frame,
            values=["Sélectionner..."] + client_names,
            width=460,
            height=35
        )
        self.client_combo.set("Sélectionner...")
        self.client_combo.pack(pady=(0, 15))
        
        # Store client mapping
        self.client_combo.client_map = {c.nom: c.id for c in clients if c.actif}
        
        # Year
        ctk.CTkLabel(
            main_frame,
            text="Année *",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.year_entry = ctk.CTkEntry(
            main_frame,
            width=460,
            height=35,
            placeholder_text="2026"
        )
        self.year_entry.pack(pady=(0, 15))
        
        # Nature
        ctk.CTkLabel(
            main_frame,
            text="Nature *",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.nature_combo = ctk.CTkComboBox(
            main_frame,
            values=["Sélectionner..."] + NATURES_BUDGET,
            width=460,
            height=35
        )
        self.nature_combo.set("Sélectionner...")
        self.nature_combo.pack(pady=(0, 15))
        
        # Montant initial
        ctk.CTkLabel(
            main_frame,
            text="Montant initial *",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.montant_entry = ctk.CTkEntry(
            main_frame,
            width=460,
            height=35,
            placeholder_text="0.00"
        )
        self.montant_entry.pack(pady=(0, 15))
        
        # Service demandeur
        ctk.CTkLabel(
            main_frame,
            text="Service demandeur",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        self.service_entry = ctk.CTkEntry(
            main_frame,
            width=460,
            height=35,
            placeholder_text="Nom du service"
        )
        self.service_entry.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=self.destroy,
            width=220,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Enregistrer",
            command=self.save,
            width=220,
            height=40,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        save_btn.pack(side="right")
    
    def load_budget_data(self):
        """Load budget data into form."""
        if not self.budget:
            return
        
        # Find and set client
        client = self.client_manager.get_client_by_id(self.budget.client_id)
        if client:
            self.client_combo.set(client.nom)
        
        self.year_entry.insert(0, str(self.budget.annee))
        self.nature_combo.set(self.budget.nature)
        self.montant_entry.insert(0, str(self.budget.montant_initial))
        
        if self.budget.service_demandeur:
            self.service_entry.insert(0, self.budget.service_demandeur)
    
    def save(self):
        """Save the budget."""
        # Get values
        client_name = self.client_combo.get()
        if not client_name or client_name == "Sélectionner...":
            messagebox.showerror("Erreur", "Veuillez sélectionner un client")
            return
        
        client_id = self.client_combo.client_map.get(client_name)
        if not client_id:
            messagebox.showerror("Erreur", "Client invalide")
            return
        
        try:
            annee = int(self.year_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Année invalide")
            return
        
        nature = self.nature_combo.get()
        if not nature or nature == "Sélectionner...":
            messagebox.showerror("Erreur", "Veuillez sélectionner une nature")
            return
        
        try:
            montant = float(self.montant_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide")
            return
        
        service = self.service_entry.get()
        
        # Save
        if self.budget:
            # Update
            self.budget.client_id = client_id
            self.budget.annee = annee
            self.budget.nature = nature
            self.budget.montant_initial = montant
            self.budget.service_demandeur = service if service else ""
            
            success, message = self.budget_manager.update_budget(self.budget)
            
            if success:
                messagebox.showinfo("Succès", message)
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Erreur", message)
        else:
            # Create
            new_budget = Budget(
                client_id=client_id,
                annee=annee,
                nature=nature,
                montant_initial=montant,
                montant_consomme=0.0,
                service_demandeur=service if service else ""
            )
            
            success, message, budget_id = self.budget_manager.create_budget(new_budget)
            
            if success:
                messagebox.showinfo("Succès", message)
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Erreur", message)
