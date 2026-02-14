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
        
        # Get filters
        annee = int(self.year_filter.get())
        nature = self.nature_filter.get()
        nature = None if nature == "Tous" else nature
        
        # Load budgets
        budgets = self.budget_manager.get_all_budgets(annee=annee, nature=nature)
        
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
            text=f"🏢 {budget.client_nom}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        client_label.grid(row=0, column=0, sticky="w", columnspan=2)
        
        nature_color = COLOR_PRIMARY if budget.nature == NATURE_FONCTIONNEMENT else COLOR_SUCCESS
        nature_label = ctk.CTkLabel(
            info_frame,
            text=budget.nature,
            font=ctk.CTkFont(size=12),
            text_color=nature_color
        )
        nature_label.grid(row=0, column=2, sticky="e", padx=5)
        
        # Budget details
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Initial amount
        ctk.CTkLabel(
            details_frame,
            text="Montant Initial",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            details_frame,
            text=format_montant(budget.montant_initial),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).grid(row=1, column=0, sticky="w")
        
        # Consumed amount
        ctk.CTkLabel(
            details_frame,
            text="Consommé",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=1)
        
        ctk.CTkLabel(
            details_frame,
            text=format_montant(budget.montant_consomme),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_DANGER
        ).grid(row=1, column=1)
        
        # Available amount
        ctk.CTkLabel(
            details_frame,
            text="Disponible",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=2, sticky="e")
        
        ctk.CTkLabel(
            details_frame,
            text=format_montant(budget.montant_disponible),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_SUCCESS
        ).grid(row=1, column=2, sticky="e")
        
        # Progress bar
        if budget.montant_initial > 0:
            pct = (budget.montant_consomme / budget.montant_initial) * 100
            progress_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            progress_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
            
            progress_bar = ctk.CTkProgressBar(
                progress_frame,
                width=400,
                height=15,
                progress_color=COLOR_DANGER if pct > 90 else COLOR_WARNING if pct > 75 else COLOR_SUCCESS
            )
            progress_bar.pack(fill="x")
            progress_bar.set(min(pct / 100, 1.0))
            
            pct_label = ctk.CTkLabel(
                progress_frame,
                text=f"{pct:.1f}% consommé",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            pct_label.pack()
        
        # Service
        if budget.service_demandeur:
            service_label = ctk.CTkLabel(
                info_frame,
                text=f"📋 Service: {budget.service_demandeur}",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            service_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Modifier",
            command=lambda b=budget: self.show_edit_dialog(b),
            width=100,
            height=28,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        edit_btn.pack(side="right", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Supprimer",
            command=lambda b=budget: self.delete_budget(b),
            width=100,
            height=28,
            fg_color=COLOR_DANGER,
            hover_color="#cc0000"
        )
        delete_btn.pack(side="right", padx=5)
    
    def show_create_dialog(self):
        """Show dialog to create a new budget."""
        dialog = BudgetDialog(self, self.db_manager, title="Créer un Budget")
        dialog.wait_window()
        if dialog.result:
            self.load_budgets()
    
    def show_edit_dialog(self, budget: Budget):
        """Show dialog to edit a budget."""
        dialog = BudgetDialog(self, self.db_manager, budget=budget, title="Modifier le Budget")
        dialog.wait_window()
        if dialog.result:
            self.load_budgets()
    
    def delete_budget(self, budget: Budget):
        """Delete a budget."""
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce budget?\n\n"
            f"Client: {budget.client_nom}\n"
            f"Année: {budget.annee}\n"
            f"Nature: {budget.nature}"
        ):
            try:
                self.budget_manager.delete_budget(budget.id)
                messagebox.showinfo("Succès", "Budget supprimé avec succès")
                self.load_budgets()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{e}")
    
    def show_report_dialog(self):
        """Show dialog to report budgets to next year."""
        dialog = ReportBudgetDialog(self, self.db_manager)
        dialog.wait_window()
        if dialog.result:
            self.load_budgets()


class BudgetDialog(ctk.CTkToplevel):
    """Dialog for creating/editing budgets."""
    
    def __init__(self, parent, db_manager: DatabaseManager, budget: Optional[Budget] = None, title: str = "Budget"):
        super().__init__(parent)
        self.db_manager = db_manager
        self.budget_manager = BudgetManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        self.budget = budget
        self.result = None
        
        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if budget:
            self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Client
        ctk.CTkLabel(main_frame, text="Client *", anchor="w").pack(fill="x", pady=(0, 5))
        clients = self.client_manager.get_all_clients()
        client_names = {c.nom: c.id for c in clients if c.actif}
        self.client_combo = ctk.CTkComboBox(main_frame, values=list(client_names.keys()))
        self.client_combo.pack(fill="x", pady=(0, 15))
        self.client_combo.client_names = client_names
        
        # Year
        ctk.CTkLabel(main_frame, text="Année *", anchor="w").pack(fill="x", pady=(0, 5))
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 1, current_year + 5)]
        self.year_combo = ctk.CTkComboBox(main_frame, values=years)
        self.year_combo.set(str(current_year))
        self.year_combo.pack(fill="x", pady=(0, 15))
        
        # Nature
        ctk.CTkLabel(main_frame, text="Nature *", anchor="w").pack(fill="x", pady=(0, 5))
        self.nature_combo = ctk.CTkComboBox(main_frame, values=NATURES_BUDGET)
        self.nature_combo.pack(fill="x", pady=(0, 15))
        
        # Initial amount
        ctk.CTkLabel(main_frame, text="Montant Initial (€) *", anchor="w").pack(fill="x", pady=(0, 5))
        self.montant_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.montant_entry.pack(fill="x", pady=(0, 15))
        
        # Service
        ctk.CTkLabel(main_frame, text="Service Demandeur", anchor="w").pack(fill="x", pady=(0, 5))
        self.service_entry = ctk.CTkEntry(main_frame, placeholder_text="Optionnel")
        self.service_entry.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=self.destroy,
            width=100,
            fg_color="gray40",
            hover_color="gray50"
        )
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Enregistrer",
            command=self.save,
            width=100,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        save_btn.pack(side="right", padx=5)
    
    def populate_data(self):
        """Populate form with budget data."""
        if self.budget:
            self.client_combo.set(self.budget.client_nom)
            self.year_combo.set(str(self.budget.annee))
            self.nature_combo.set(self.budget.nature)
            self.montant_entry.insert(0, str(self.budget.montant_initial))
            if self.budget.service_demandeur:
                self.service_entry.insert(0, self.budget.service_demandeur)
    
    def save(self):
        """Save the budget."""
        try:
            # Validate
            client_nom = self.client_combo.get()
            if not client_nom or client_nom not in self.client_combo.client_names:
                messagebox.showerror("Erreur", "Veuillez sélectionner un client")
                return
            
            client_id = self.client_combo.client_names[client_nom]
            annee = int(self.year_combo.get())
            nature = self.nature_combo.get()
            montant = float(self.montant_entry.get().replace(',', '.'))
            service = self.service_entry.get().strip()
            
            if not validate_annee(annee):
                messagebox.showerror("Erreur", "Année invalide")
                return
            
            if not validate_montant(montant):
                messagebox.showerror("Erreur", "Montant invalide")
                return
            
            # Save
            if self.budget:
                # Update
                self.budget.client_id = client_id
                self.budget.annee = annee
                self.budget.nature = nature
                self.budget.montant_initial = montant
                self.budget.service_demandeur = service if service else None
                self.budget_manager.update_budget(self.budget)
                messagebox.showinfo("Succès", "Budget modifié avec succès")
            else:
                # Create
                self.budget_manager.create_budget(
                    client_id=client_id,
                    annee=annee,
                    nature=nature,
                    montant_initial=montant,
                    service_demandeur=service if service else None
                )
                messagebox.showinfo("Succès", "Budget créé avec succès")
            
            self.result = True
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Erreur", f"Valeur invalide: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")


class ReportBudgetDialog(ctk.CTkToplevel):
    """Dialog for reporting budgets to next year."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.budget_manager = BudgetManager(db_manager)
        self.result = None
        
        self.title("Reporter les Budgets")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Info
        info_label = ctk.CTkLabel(
            main_frame,
            text="Reporter les budgets d'une année à l'autre\n\n"
                 "Les budgets de l'année source seront dupliqués\n"
                 "vers l'année cible avec le montant initial identique.",
            font=ctk.CTkFont(size=12),
            text_color="gray70",
            justify="center"
        )
        info_label.pack(pady=(0, 20))
        
        # Source year
        ctk.CTkLabel(main_frame, text="Année Source:", anchor="w").pack(fill="x", pady=(0, 5))
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 2, current_year + 3)]
        self.source_year = ctk.CTkComboBox(main_frame, values=years)
        self.source_year.set(str(current_year))
        self.source_year.pack(fill="x", pady=(0, 15))
        
        # Target year
        ctk.CTkLabel(main_frame, text="Année Cible:", anchor="w").pack(fill="x", pady=(0, 5))
        self.target_year = ctk.CTkComboBox(main_frame, values=years)
        self.target_year.set(str(current_year + 1))
        self.target_year.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=self.destroy,
            width=100,
            fg_color="gray40",
            hover_color="gray50"
        )
        cancel_btn.pack(side="right", padx=5)
        
        report_btn = ctk.CTkButton(
            btn_frame,
            text="Reporter",
            command=self.report,
            width=100,
            fg_color=COLOR_WARNING,
            hover_color=COLOR_PRIMARY
        )
        report_btn.pack(side="right", padx=5)
    
    def report(self):
        """Report budgets to next year."""
        try:
            source = int(self.source_year.get())
            target = int(self.target_year.get())
            
            if source == target:
                messagebox.showerror("Erreur", "L'année source et l'année cible doivent être différentes")
                return
            
            if messagebox.askyesno(
                "Confirmation",
                f"Reporter les budgets de {source} vers {target}?\n\n"
                f"Cette opération créera de nouveaux budgets pour l'année {target}."
            ):
                count = self.budget_manager.reporter_budgets(source, target)
                messagebox.showinfo("Succès", f"{count} budget(s) reporté(s) avec succès")
                self.result = True
                self.destroy()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du report:\n{e}")
