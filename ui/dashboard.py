"""
Dashboard View - Vue tableau de bord avec KPIs.
"""
import customtkinter as ctk
from datetime import datetime
from database.db_manager import DatabaseManager
from business.budget_manager import BudgetManager
from business.contrat_manager import ContratManager
from business.projet_manager import ProjetManager
from business.alert_manager import AlertManager
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD, NATURE_FONCTIONNEMENT, NATURE_INVESTISSEMENT
)
from utils.formatters import format_montant


class DashboardView(ctk.CTkFrame):
    """Dashboard view with KPIs."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize dashboard view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        
        # Initialize managers
        self.budget_manager = BudgetManager(db_manager)
        self.contrat_manager = ContratManager(db_manager)
        self.projet_manager = ProjetManager(db_manager)
        self.alert_manager = AlertManager(db_manager)
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create dashboard widgets."""
        # Configure grid
        self.grid_columnconfigure((0, 1), weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=f"📅 {datetime.now().strftime('%d/%m/%Y')}",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        date_label.pack(side="left", padx=20)
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Actualiser",
            command=self.load_data,
            width=120,
            height=32,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        refresh_btn.pack(side="right")
        
        # KPI Cards - Row 1
        self.kpi_fonctionnement = self.create_kpi_card(
            row=1, column=0,
            title="💰 Budget Fonctionnement",
            color=COLOR_PRIMARY
        )
        
        self.kpi_investissement = self.create_kpi_card(
            row=1, column=1,
            title="💵 Budget Investissement",
            color=COLOR_SUCCESS
        )
        
        # KPI Cards - Row 2
        self.kpi_contrats = self.create_kpi_card(
            row=2, column=0,
            title="📄 Contrats",
            color=COLOR_WARNING
        )
        
        self.kpi_projets = self.create_kpi_card(
            row=2, column=1,
            title="📁 Projets",
            color=COLOR_DANGER
        )
    
    def create_kpi_card(self, row: int, column: int, title: str, color: str) -> ctk.CTkFrame:
        """Create a KPI card."""
        card = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_CARD,
            corner_radius=12
        )
        card.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=color
        )
        title_label.pack(pady=(20, 10))
        
        # Main value
        value_label = ctk.CTkLabel(
            card,
            text="...",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        value_label.pack(pady=10)
        
        # Secondary value
        secondary_label = ctk.CTkLabel(
            card,
            text="...",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        secondary_label.pack(pady=(0, 20))
        
        # Store references
        card.value_label = value_label
        card.secondary_label = secondary_label
        
        return card
    
    def load_data(self):
        """Load dashboard data."""
        try:
            # Current year
            current_year = datetime.now().year
            
            # Budget Fonctionnement
            budgets_fonc = self.budget_manager.get_all_budgets(
                annee=current_year,
                nature=NATURE_FONCTIONNEMENT
            )
            total_fonc = sum(b.montant_initial for b in budgets_fonc)
            disponible_fonc = sum(b.montant_disponible for b in budgets_fonc)
            
            self.kpi_fonctionnement.value_label.configure(
                text=format_montant(total_fonc)
            )
            self.kpi_fonctionnement.secondary_label.configure(
                text=f"Disponible: {format_montant(disponible_fonc)}"
            )
            
            # Budget Investissement
            budgets_inv = self.budget_manager.get_all_budgets(
                annee=current_year,
                nature=NATURE_INVESTISSEMENT
            )
            total_inv = sum(b.montant_initial for b in budgets_inv)
            disponible_inv = sum(b.montant_disponible for b in budgets_inv)
            
            self.kpi_investissement.value_label.configure(
                text=format_montant(total_inv)
            )
            self.kpi_investissement.secondary_label.configure(
                text=f"Disponible: {format_montant(disponible_inv)}"
            )
            
            # Contrats
            contrats_actifs = self.contrat_manager.get_contrats_actifs()
            alertes_contrats = self.alert_manager.get_contrats_expiring(days=180)
            
            self.kpi_contrats.value_label.configure(
                text=str(len(contrats_actifs))
            )
            alert_text = f"⚠️ {len(alertes_contrats)} alertes" if alertes_contrats else "✅ Aucune alerte"
            self.kpi_contrats.secondary_label.configure(text=alert_text)
            
            # Projets
            projets_en_cours = self.projet_manager.get_projets_by_statut("En cours")
            projets_sans_fap = [p for p in projets_en_cours if not p.fap_redigee]
            
            self.kpi_projets.value_label.configure(
                text=str(len(projets_en_cours))
            )
            fap_text = f"📋 {len(projets_sans_fap)} sans FAP" if projets_sans_fap else "✅ Tous avec FAP"
            self.kpi_projets.secondary_label.configure(text=fap_text)
            
        except Exception as e:
            print(f"Erreur lors du chargement du dashboard: {e}")
