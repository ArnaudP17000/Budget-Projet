"""
Projets View - Gestion complète des projets.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Optional
from database.db_manager import DatabaseManager
from business.projet_manager import ProjetManager
from database.models import Projet, InvestissementProjet, ContactSourcing
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD, STATUTS_PROJET, TYPES_INVESTISSEMENT
)
from utils.formatters import format_montant, format_date, parse_date
from utils.validators import validate_montant, validate_required_field, validate_date_range


class ProjetsView(ctk.CTkFrame):
    """Projects management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize projects view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.projet_manager = ProjetManager(db_manager)
        
        self.create_widgets()
        self.load_projets()
    
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
            text="📁 Gestion des Projets",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        new_btn = ctk.CTkButton(
            header_frame,
            text="➕ Nouveau Projet",
            command=self.show_create_dialog,
            width=180,
            height=36,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        new_btn.grid(row=0, column=2, padx=5)
        
        # Filters
        filter_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=8)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            filter_frame,
            text="🔍 Filtres:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(10, 20))
        
        ctk.CTkLabel(filter_frame, text="Statut:").pack(side="left", padx=(0, 5))
        self.statut_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Tous"] + STATUTS_PROJET,
            width=150,
            command=lambda _: self.load_projets()
        )
        self.statut_filter.set("Tous")
        self.statut_filter.pack(side="left", padx=5)
        
        # Scrollable frame for projects
        self.projets_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.projets_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.projets_scroll.grid_columnconfigure(0, weight=1)
    
    def load_projets(self):
        """Load and display projects."""
        # Clear existing
        for widget in self.projets_scroll.winfo_children():
            widget.destroy()
        
        # Get filters
        statut = self.statut_filter.get()
        statut = None if statut == "Tous" else statut
        
        # Load projects
        projets = self.projet_manager.get_all_projets(statut=statut)
        
        if not projets:
            no_data_label = ctk.CTkLabel(
                self.projets_scroll,
                text="Aucun projet trouvé",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            )
            no_data_label.pack(pady=50)
            return
        
        # Display projects
        for projet in projets:
            self.create_projet_card(projet)
    
    def create_projet_card(self, projet: Projet):
        """Create a project card."""
        card = ctk.CTkFrame(self.projets_scroll, fg_color=COLOR_BG_CARD, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=15)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Project name
        nom_label = ctk.CTkLabel(
            info_frame,
            text=f"📁 {projet.nom_projet}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        nom_label.grid(row=0, column=0, sticky="w", columnspan=2)
        
        # FAP badge
        if projet.fap_redigee:
            fap_label = ctk.CTkLabel(
                info_frame,
                text="📋 FAP",
                font=ctk.CTkFont(size=11),
                text_color=COLOR_SUCCESS
            )
            fap_label.grid(row=0, column=2, sticky="e", padx=5)
        else:
            fap_label = ctk.CTkLabel(
                info_frame,
                text="⚠️ Sans FAP",
                font=ctk.CTkFont(size=11),
                text_color=COLOR_WARNING
            )
            fap_label.grid(row=0, column=2, sticky="e", padx=5)
        
        # Status badge
        statut_colors = {
            "En cours": COLOR_PRIMARY,
            "Terminé": COLOR_SUCCESS,
            "Suspendu": COLOR_DANGER
        }
        statut_color = statut_colors.get(projet.statut, "white")
        
        statut_label = ctk.CTkLabel(
            info_frame,
            text=projet.statut,
            font=ctk.CTkFont(size=11),
            text_color=statut_color
        )
        statut_label.grid(row=0, column=3, sticky="e", padx=5)
        
        # Project details
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Porteur
        if projet.porteur_projet:
            ctk.CTkLabel(
                details_frame,
                text="👤 Porteur",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            ).grid(row=0, column=0, sticky="w")
            
            ctk.CTkLabel(
                details_frame,
                text=projet.porteur_projet,
                font=ctk.CTkFont(size=13),
                text_color="white"
            ).grid(row=1, column=0, sticky="w")
        
        # Service
        if projet.service_demandeur:
            ctk.CTkLabel(
                details_frame,
                text="🏢 Service",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            ).grid(row=0, column=1)
            
            ctk.CTkLabel(
                details_frame,
                text=projet.service_demandeur,
                font=ctk.CTkFont(size=13),
                text_color="white"
            ).grid(row=1, column=1)
        
        # Dates
        if projet.date_debut:
            ctk.CTkLabel(
                details_frame,
                text="📅 Début",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            ).grid(row=0, column=2, sticky="e")
            
            ctk.CTkLabel(
                details_frame,
                text=format_date(projet.date_debut),
                font=ctk.CTkFont(size=13),
                text_color="white"
            ).grid(row=1, column=2, sticky="e")
        
        # Total investissements
        total_inv = self.projet_manager.get_total_investissements(projet.id)
        if total_inv > 0:
            inv_label = ctk.CTkLabel(
                info_frame,
                text=f"💰 Investissements estimés: {format_montant(total_inv)}",
                font=ctk.CTkFont(size=12),
                text_color=COLOR_SUCCESS
            )
            inv_label.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        details_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Détails",
            command=lambda p=projet: self.show_details_dialog(p),
            width=100,
            height=28,
            fg_color=COLOR_WARNING,
            hover_color=COLOR_PRIMARY
        )
        details_btn.pack(side="right", padx=5)
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Modifier",
            command=lambda p=projet: self.show_edit_dialog(p),
            width=100,
            height=28,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        edit_btn.pack(side="right", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Supprimer",
            command=lambda p=projet: self.delete_projet(p),
            width=100,
            height=28,
            fg_color=COLOR_DANGER,
            hover_color="#cc0000"
        )
        delete_btn.pack(side="right", padx=5)
    
    def show_create_dialog(self):
        """Show dialog to create a new project."""
        dialog = ProjetDialog(self, self.db_manager, title="Créer un Projet")
        dialog.wait_window()
        if dialog.result:
            self.load_projets()
    
    def show_edit_dialog(self, projet: Projet):
        """Show dialog to edit a project."""
        dialog = ProjetDialog(self, self.db_manager, projet=projet, title="Modifier le Projet")
        dialog.wait_window()
        if dialog.result:
            self.load_projets()
    
    def show_details_dialog(self, projet: Projet):
        """Show detailed project information dialog."""
        dialog = ProjetDetailsDialog(self, self.db_manager, projet)
        dialog.wait_window()
    
    def delete_projet(self, projet: Projet):
        """Delete a project."""
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce projet?\n\n"
            f"Nom: {projet.nom_projet}\n\n"
            f"⚠️ Toutes les données associées (investissements, contacts sourcing) seront également supprimées."
        ):
            success, msg = self.projet_manager.delete_projet(projet.id)
            if success:
                messagebox.showinfo("Succès", msg)
                self.load_projets()
            else:
                messagebox.showerror("Erreur", msg)


class ProjetDialog(ctk.CTkToplevel):
    """Dialog for creating/editing projects."""
    
    def __init__(self, parent, db_manager: DatabaseManager, projet: Optional[Projet] = None, title: str = "Projet"):
        super().__init__(parent)
        self.db_manager = db_manager
        self.projet_manager = ProjetManager(db_manager)
        self.projet = projet
        self.result = None
        
        self.title(title)
        self.geometry("600x900")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if projet:
            self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nom du projet
        ctk.CTkLabel(main_frame, text="Nom du Projet *", anchor="w").pack(fill="x", pady=(0, 5))
        self.nom_entry = ctk.CTkEntry(main_frame, placeholder_text="Nom du projet")
        self.nom_entry.pack(fill="x", pady=(0, 15))
        
        # FAP
        self.fap_var = ctk.BooleanVar(value=False)
        fap_check = ctk.CTkCheckBox(main_frame, text="FAP rédigée", variable=self.fap_var)
        fap_check.pack(anchor="w", pady=(0, 15))
        
        # Statut
        ctk.CTkLabel(main_frame, text="Statut *", anchor="w").pack(fill="x", pady=(0, 5))
        self.statut_combo = ctk.CTkComboBox(main_frame, values=STATUTS_PROJET)
        self.statut_combo.set("En cours")
        self.statut_combo.pack(fill="x", pady=(0, 15))
        
        # Porteur du projet
        ctk.CTkLabel(main_frame, text="Porteur du Projet", anchor="w").pack(fill="x", pady=(0, 5))
        self.porteur_entry = ctk.CTkEntry(main_frame, placeholder_text="Nom du porteur")
        self.porteur_entry.pack(fill="x", pady=(0, 15))
        
        # Service demandeur
        ctk.CTkLabel(main_frame, text="Service Demandeur", anchor="w").pack(fill="x", pady=(0, 5))
        self.service_entry = ctk.CTkEntry(main_frame, placeholder_text="Service")
        self.service_entry.pack(fill="x", pady=(0, 15))
        
        # Dates frame
        dates_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        dates_frame.pack(fill="x", pady=(0, 15))
        dates_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(dates_frame, text="Date Début", anchor="w").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.date_debut_entry = ctk.CTkEntry(dates_frame, placeholder_text="YYYY-MM-DD")
        self.date_debut_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        ctk.CTkLabel(dates_frame, text="Date Fin Estimée", anchor="w").grid(row=0, column=1, sticky="w", padx=(5, 0))
        self.date_fin_entry = ctk.CTkEntry(dates_frame, placeholder_text="YYYY-MM-DD")
        self.date_fin_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Date mise en service
        ctk.CTkLabel(main_frame, text="Date Mise en Service", anchor="w").pack(fill="x", pady=(0, 5))
        self.date_service_entry = ctk.CTkEntry(main_frame, placeholder_text="YYYY-MM-DD")
        self.date_service_entry.pack(fill="x", pady=(0, 15))
        
        # Section Technologies
        ctk.CTkLabel(main_frame, text="Technologies utilisées", anchor="w").pack(fill="x", pady=(0, 5))
        self.tech_text = ctk.CTkTextbox(main_frame, height=60)
        self.tech_text.pack(fill="x", pady=(0, 15))
        
        # Section Investissements
        invest_label = ctk.CTkLabel(
            main_frame, 
            text="📊 INVESTISSEMENTS", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=COLOR_PRIMARY
        )
        invest_label.pack(fill="x", pady=(10, 10))
        
        # Investissement Licence
        ctk.CTkLabel(main_frame, text="Investissement Licence (€)", anchor="w").pack(fill="x", pady=(0, 5))
        self.licence_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.licence_entry.pack(fill="x", pady=(0, 10))
        
        # Investissement Matériel
        ctk.CTkLabel(main_frame, text="Investissement Matériel (€)", anchor="w").pack(fill="x", pady=(0, 5))
        self.materiel_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.materiel_entry.pack(fill="x", pady=(0, 10))
        
        # Investissement Logiciel
        ctk.CTkLabel(main_frame, text="Investissement Logiciel (€)", anchor="w").pack(fill="x", pady=(0, 5))
        self.logiciel_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.logiciel_entry.pack(fill="x", pady=(0, 10))
        
        # Coût Formation
        ctk.CTkLabel(main_frame, text="Coût Formation (€)", anchor="w").pack(fill="x", pady=(0, 5))
        self.formation_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.formation_entry.pack(fill="x", pady=(0, 10))
        
        # Frais Maintenance
        ctk.CTkLabel(main_frame, text="Frais de Maintenance (€)", anchor="w").pack(fill="x", pady=(0, 5))
        self.maintenance_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.maintenance_entry.pack(fill="x", pady=(0, 10))
        
        # Total automatique (lecture seule)
        total_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        total_frame.pack(fill="x", pady=(5, 15))
        ctk.CTkLabel(total_frame, text="TOTAL ESTIMÉ:", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left")
        self.total_label = ctk.CTkLabel(
            total_frame, 
            text="0.00 €", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="#4ecdc4",
            anchor="w"
        )
        self.total_label.pack(side="left", padx=(10, 0))
        
        # Bind calculation
        for entry in [self.licence_entry, self.materiel_entry, self.logiciel_entry, 
                     self.formation_entry, self.maintenance_entry]:
            entry.bind('<KeyRelease>', lambda e: self.calculate_total())
        
        # Contacts pris
        ctk.CTkLabel(main_frame, text="Contacts Pris", anchor="w").pack(fill="x", pady=(0, 5))
        self.contacts_text = ctk.CTkTextbox(main_frame, height=60)
        self.contacts_text.pack(fill="x", pady=(0, 10))
        
        # Sourcing
        ctk.CTkLabel(main_frame, text="Sourcing", anchor="w").pack(fill="x", pady=(0, 5))
        self.sourcing_text = ctk.CTkTextbox(main_frame, height=60)
        self.sourcing_text.pack(fill="x", pady=(0, 10))
        
        # Remarques
        ctk.CTkLabel(main_frame, text="Remarques", anchor="w").pack(fill="x", pady=(0, 5))
        self.remarques_text = ctk.CTkTextbox(main_frame, height=80)
        self.remarques_text.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(btn_container, fg_color="transparent")
        btn_frame.pack(fill="x")
        
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
    
    def calculate_total(self):
        """Calculate and display total investment."""
        try:
            licence = float(self.licence_entry.get() or 0)
            materiel = float(self.materiel_entry.get() or 0)
            logiciel = float(self.logiciel_entry.get() or 0)
            formation = float(self.formation_entry.get() or 0)
            maintenance = float(self.maintenance_entry.get() or 0)
            
            total = licence + materiel + logiciel + formation + maintenance
            self.total_label.configure(text=f"{total:.2f} €")
        except ValueError:
            self.total_label.configure(text="0.00 €")
    
    def populate_data(self):
        """Populate form with project data."""
        if self.projet:
            self.nom_entry.insert(0, self.projet.nom_projet)
            self.fap_var.set(self.projet.fap_redigee)
            self.statut_combo.set(self.projet.statut)
            
            if self.projet.porteur_projet:
                self.porteur_entry.insert(0, self.projet.porteur_projet)
            if self.projet.service_demandeur:
                self.service_entry.insert(0, self.projet.service_demandeur)
            
            if self.projet.date_debut:
                self.date_debut_entry.insert(0, format_date(self.projet.date_debut))
            if self.projet.date_fin_estimee:
                self.date_fin_entry.insert(0, format_date(self.projet.date_fin_estimee))
            if self.projet.date_mise_service:
                self.date_service_entry.insert(0, format_date(self.projet.date_mise_service))
            
            # Technologies
            if self.projet.technologies_utilisees:
                self.tech_text.insert("1.0", self.projet.technologies_utilisees)
            
            # Financial fields
            self.licence_entry.insert(0, str(self.projet.investissement_licence))
            self.materiel_entry.insert(0, str(self.projet.investissement_materiel))
            self.logiciel_entry.insert(0, str(self.projet.investissement_logiciel))
            self.formation_entry.insert(0, str(self.projet.cout_formation))
            self.maintenance_entry.insert(0, str(self.projet.frais_maintenance))
            
            self.calculate_total()
            
            if self.projet.contacts_pris:
                self.contacts_text.insert("1.0", self.projet.contacts_pris)
            if self.projet.sourcing:
                self.sourcing_text.insert("1.0", self.projet.sourcing)
            if self.projet.remarques_1:
                self.remarques_text.insert("1.0", self.projet.remarques_1)
    
    def save(self):
        """Save the project."""
        try:
            # Validate
            nom = self.nom_entry.get().strip()
            valid, msg = validate_required_field(nom, "Nom du projet")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            fap_redigee = self.fap_var.get()
            statut = self.statut_combo.get()
            porteur = self.porteur_entry.get().strip()
            service = self.service_entry.get().strip()
            
            # Parse dates
            date_debut = None
            date_debut_str = self.date_debut_entry.get().strip()
            if date_debut_str:
                date_debut = parse_date(date_debut_str)
            
            date_fin = None
            date_fin_str = self.date_fin_entry.get().strip()
            if date_fin_str:
                date_fin = parse_date(date_fin_str)
            
            date_service = None
            date_service_str = self.date_service_entry.get().strip()
            if date_service_str:
                date_service = parse_date(date_service_str)
            
            if date_debut and date_fin:
                if not validate_date_range(date_debut, date_fin):
                    messagebox.showerror("Erreur", "La date de fin doit être postérieure à la date de début")
                    return
            
            contacts_pris = self.contacts_text.get("1.0", "end-1c").strip()
            sourcing = self.sourcing_text.get("1.0", "end-1c").strip()
            remarques = self.remarques_text.get("1.0", "end-1c").strip()
            technologies = self.tech_text.get("1.0", "end-1c").strip()
            
            # Parse financial values
            try:
                investissement_licence = float(self.licence_entry.get() or 0)
                investissement_materiel = float(self.materiel_entry.get() or 0)
                investissement_logiciel = float(self.logiciel_entry.get() or 0)
                cout_formation = float(self.formation_entry.get() or 0)
                frais_maintenance = float(self.maintenance_entry.get() or 0)
            except ValueError:
                messagebox.showerror("Erreur", "Les montants financiers doivent être des nombres valides")
                return
            
            # Create or update
            if self.projet:
                # Update
                self.projet.nom_projet = nom
                self.projet.fap_redigee = fap_redigee
                self.projet.statut = statut
                self.projet.porteur_projet = porteur
                self.projet.service_demandeur = service
                self.projet.date_debut = date_debut
                self.projet.date_fin_estimee = date_fin
                self.projet.date_mise_service = date_service
                self.projet.contacts_pris = contacts_pris
                self.projet.sourcing = sourcing
                self.projet.remarques_1 = remarques
                self.projet.technologies_utilisees = technologies
                self.projet.investissement_licence = investissement_licence
                self.projet.investissement_materiel = investissement_materiel
                self.projet.investissement_logiciel = investissement_logiciel
                self.projet.cout_formation = cout_formation
                self.projet.frais_maintenance = frais_maintenance
                
                success, msg = self.projet_manager.update_projet(self.projet)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
            else:
                # Create
                new_projet = Projet(
                    nom_projet=nom,
                    fap_redigee=fap_redigee,
                    statut=statut,
                    porteur_projet=porteur,
                    service_demandeur=service,
                    date_debut=date_debut,
                    date_fin_estimee=date_fin,
                    date_mise_service=date_service,
                    contacts_pris=contacts_pris,
                    sourcing=sourcing,
                    remarques_1=remarques,
                    technologies_utilisees=technologies,
                    investissement_licence=investissement_licence,
                    investissement_materiel=investissement_materiel,
                    investissement_logiciel=investissement_logiciel,
                    cout_formation=cout_formation,
                    frais_maintenance=frais_maintenance
                )
                
                success, msg, projet_id = self.projet_manager.create_projet(new_projet)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")


class ProjetDetailsDialog(ctk.CTkToplevel):
    """Dialog showing detailed project information with investissements and contacts sourcing."""
    
    def __init__(self, parent, db_manager: DatabaseManager, projet: Projet):
        super().__init__(parent)
        self.db_manager = db_manager
        self.projet_manager = ProjetManager(db_manager)
        self.projet = projet
        
        self.title(f"Détails - {projet.nom_projet}")
        self.geometry("800x700")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main container with tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs
        self.tab_info = self.tabview.add("📋 Informations")
        self.tab_invest = self.tabview.add("💰 Investissements")
        self.tab_contacts = self.tabview.add("👥 Contacts Sourcing")
        
        # Info tab
        self.create_info_tab()
        
        # Investissements tab
        self.create_investissements_tab()
        
        # Contacts tab
        self.create_contacts_tab()
        
        # Action buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 10))
        
        # Prospects button
        prospects_btn = ctk.CTkButton(
            btn_frame,
            text="👥 Gérer les Prospects / Fournisseurs",
            command=self.open_prospects_window,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color="#0a5a5d",
            height=40
        )
        prospects_btn.pack(fill="x", pady=(0, 10))
        
        # Export Excel button
        export_btn = ctk.CTkButton(
            btn_frame,
            text="📊 Export Excel (Comparatif)",
            command=self.export_to_excel,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4ecdc4",
            hover_color="#3db5ad",
            height=40
        )
        export_btn.pack(fill="x", pady=(0, 10))
        
        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Fermer",
            command=self.destroy,
            width=100,
            fg_color="gray40",
            hover_color="gray50"
        )
        close_btn.pack(pady=(0, 20))
    
    def create_info_tab(self):
        """Create information tab."""
        scroll = ctk.CTkScrollableFrame(self.tab_info, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Project name
        ctk.CTkLabel(
            scroll,
            text=self.projet.nom_projet,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        # Create info fields
        info_fields = [
            ("Statut", self.projet.statut),
            ("FAP Rédigée", "Oui" if self.projet.fap_redigee else "Non"),
            ("Porteur du Projet", self.projet.porteur_projet or "-"),
            ("Service Demandeur", self.projet.service_demandeur or "-"),
            ("Date Début", format_date(self.projet.date_debut) if self.projet.date_debut else "-"),
            ("Date Fin Estimée", format_date(self.projet.date_fin_estimee) if self.projet.date_fin_estimee else "-"),
            ("Date Mise en Service", format_date(self.projet.date_mise_service) if self.projet.date_mise_service else "-"),
            ("Technologies utilisées", self.projet.technologies_utilisees or "-"),
        ]
        
        for label, value in info_fields:
            field_frame = ctk.CTkFrame(scroll, fg_color=COLOR_BG_CARD, corner_radius=8)
            field_frame.pack(fill="x", pady=5)
            field_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                field_frame,
                text=label + ":",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=0, sticky="w", padx=10, pady=8)
            
            ctk.CTkLabel(
                field_frame,
                text=value,
                anchor="e"
            ).grid(row=0, column=1, sticky="e", padx=10, pady=8)
        
        # Financial section
        ctk.CTkLabel(
            scroll,
            text="💰 Investissements Projet",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", pady=(20, 10))
        
        financial_fields = [
            ("Investissement Licence", format_montant(self.projet.investissement_licence)),
            ("Investissement Matériel", format_montant(self.projet.investissement_materiel)),
            ("Investissement Logiciel", format_montant(self.projet.investissement_logiciel)),
            ("Coût Formation", format_montant(self.projet.cout_formation)),
            ("Frais de Maintenance", format_montant(self.projet.frais_maintenance)),
        ]
        
        total_investissement = (
            self.projet.investissement_licence +
            self.projet.investissement_materiel +
            self.projet.investissement_logiciel +
            self.projet.cout_formation +
            self.projet.frais_maintenance
        )
        
        for label, value in financial_fields:
            field_frame = ctk.CTkFrame(scroll, fg_color=COLOR_BG_CARD, corner_radius=8)
            field_frame.pack(fill="x", pady=5)
            field_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                field_frame,
                text=label + ":",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=0, sticky="w", padx=10, pady=8)
            
            ctk.CTkLabel(
                field_frame,
                text=value,
                anchor="e"
            ).grid(row=0, column=1, sticky="e", padx=10, pady=8)
        
        # Total
        total_frame = ctk.CTkFrame(scroll, fg_color="#4ecdc4", corner_radius=8)
        total_frame.pack(fill="x", pady=10)
        total_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            total_frame,
            text="TOTAL ESTIMÉ:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=12)
        
        ctk.CTkLabel(
            total_frame,
            text=format_montant(total_investissement),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
            anchor="e"
        ).grid(row=0, column=1, sticky="e", padx=10, pady=12)
        
        # Text fields
        if self.projet.contacts_pris:
            self.create_text_section(scroll, "Contacts Pris", self.projet.contacts_pris)
        
        if self.projet.sourcing:
            self.create_text_section(scroll, "Sourcing", self.projet.sourcing)
        
        if self.projet.remarques_1:
            self.create_text_section(scroll, "Remarques", self.projet.remarques_1)
    
    def create_text_section(self, parent, title, content):
        """Create a text section."""
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", pady=(15, 5))
        
        text_frame = ctk.CTkFrame(parent, fg_color=COLOR_BG_CARD, corner_radius=8)
        text_frame.pack(fill="x", pady=5)
        
        text_box = ctk.CTkTextbox(text_frame, height=100)
        text_box.pack(fill="both", padx=10, pady=10)
        text_box.insert("1.0", content)
        text_box.configure(state="disabled")
    
    def create_investissements_tab(self):
        """Create investissements tab."""
        # Header with add button
        header = ctk.CTkFrame(self.tab_invest, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Liste des Investissements",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Scrollable list
        self.invest_scroll = ctk.CTkScrollableFrame(self.tab_invest, fg_color="transparent")
        self.invest_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_contacts_tab(self):
        """Create contacts sourcing tab."""
        # Header
        header = ctk.CTkFrame(self.tab_contacts, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Contacts Sourcing",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Scrollable list
        self.contacts_scroll = ctk.CTkScrollableFrame(self.tab_contacts, fg_color="transparent")
        self.contacts_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_data(self):
        """Load investissements and contacts data."""
        self.load_investissements()
        self.load_contacts()
    
    def load_investissements(self):
        """Load and display investissements."""
        # Clear existing
        for widget in self.invest_scroll.winfo_children():
            widget.destroy()
        
        investissements = self.projet_manager.get_investissements(self.projet.id)
        
        if not investissements:
            ctk.CTkLabel(
                self.invest_scroll,
                text="Aucun investissement enregistré",
                text_color="gray60"
            ).pack(pady=20)
            return
        
        # Display investissements
        total = 0
        for inv in investissements:
            card = ctk.CTkFrame(self.invest_scroll, fg_color=COLOR_BG_CARD, corner_radius=8)
            card.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=10)
            info_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                info_frame,
                text=inv.type,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLOR_PRIMARY
            ).grid(row=0, column=0, sticky="w")
            
            ctk.CTkLabel(
                info_frame,
                text=format_montant(inv.montant_estime),
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLOR_SUCCESS
            ).grid(row=0, column=1, sticky="e")
            
            if inv.description:
                ctk.CTkLabel(
                    info_frame,
                    text=inv.description,
                    font=ctk.CTkFont(size=11),
                    text_color="gray70"
                ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
            
            total += inv.montant_estime
        
        # Total
        total_frame = ctk.CTkFrame(self.invest_scroll, fg_color=COLOR_PRIMARY, corner_radius=8)
        total_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Estimé: {format_montant(total)}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(padx=15, pady=10)
    
    def load_contacts(self):
        """Load and display contacts sourcing."""
        # Clear existing
        for widget in self.contacts_scroll.winfo_children():
            widget.destroy()
        
        contacts = self.projet_manager.get_contacts_sourcing(self.projet.id)
        
        if not contacts:
            ctk.CTkLabel(
                self.contacts_scroll,
                text="Aucun contact sourcing enregistré",
                text_color="gray60"
            ).pack(pady=20)
            return
        
        # Display contacts
        for contact in contacts:
            card = ctk.CTkFrame(self.contacts_scroll, fg_color=COLOR_BG_CARD, corner_radius=8)
            card.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=f"👤 {contact.prenom} {contact.nom}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white"
            ).pack(anchor="w")
            
            if contact.entreprise:
                ctk.CTkLabel(
                    info_frame,
                    text=f"🏢 {contact.entreprise}",
                    font=ctk.CTkFont(size=11),
                    text_color="gray70"
                ).pack(anchor="w", pady=(2, 0))
            
            if contact.telephone:
                ctk.CTkLabel(
                    info_frame,
                    text=f"📞 {contact.telephone}",
                    font=ctk.CTkFont(size=11),
                    text_color="gray70"
                ).pack(anchor="w", pady=(2, 0))
            
            if contact.email:
                ctk.CTkLabel(
                    info_frame,
                    text=f"✉️ {contact.email}",
                    font=ctk.CTkFont(size=11),
                    text_color="gray70"
                ).pack(anchor="w", pady=(2, 0))
            
            if contact.notes:
                ctk.CTkLabel(
                    info_frame,
                    text=f"📝 {contact.notes}",
                    font=ctk.CTkFont(size=11),
                    text_color="gray60"
                ).pack(anchor="w", pady=(5, 0))
    
    def open_prospects_window(self):
        """Open prospects management window."""
        from tkinter import filedialog
        import os
        
        window = ctk.CTkToplevel(self)
        window.title("Gestion des Prospects / Fournisseurs")
        window.geometry("1200x700")
        
        # Make modal
        window.transient(self)
        window.grab_set()
        
        # Titre
        title = ctk.CTkLabel(
            window, 
            text="👥 Prospects / Fournisseurs", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color=COLOR_PRIMARY
        )
        title.pack(pady=20)
        
        # Bouton Ajouter
        add_btn = ctk.CTkButton(
            window,
            text="➕ Ajouter un Prospect",
            command=lambda: self.add_prospect_dialog(window),
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_PRIMARY,
            height=40
        )
        add_btn.pack(pady=10, padx=20, fill="x")
        
        # Frame pour la liste des prospects
        self.prospects_frame = ctk.CTkScrollableFrame(window, fg_color="transparent")
        self.prospects_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Charger les prospects
        self.refresh_prospects_list(window)
    
    def refresh_prospects_list(self, window):
        """Refresh the prospects list."""
        # Clear existing
        for widget in self.prospects_frame.winfo_children():
            widget.destroy()
        
        # Get prospects
        prospects = self.projet_manager.get_prospects_by_projet(self.projet.id)
        
        if not prospects:
            empty_label = ctk.CTkLabel(
                self.prospects_frame, 
                text="Aucun prospect ajouté", 
                font=ctk.CTkFont(size=14), 
                text_color="gray60"
            )
            empty_label.pack(pady=50)
        else:
            # Create header
            header_frame = ctk.CTkFrame(self.prospects_frame, fg_color=COLOR_PRIMARY, height=40)
            header_frame.pack(fill="x", pady=(0, 10))
            header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
            
            headers = ['Prospect', 'Licence', 'Matériel', 'Logiciel', 'Formation', 'Maintenance', 'TOTAL', 'Actions']
            for col, header in enumerate(headers):
                label = ctk.CTkLabel(
                    header_frame, 
                    text=header, 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="white"
                )
                label.grid(row=0, column=col, padx=5, pady=10)
            
            # Data rows
            for prospect in prospects:
                row_frame = ctk.CTkFrame(self.prospects_frame, fg_color=COLOR_BG_CARD)
                row_frame.pack(fill="x", pady=2)
                row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
                
                # Prospect name
                ctk.CTkLabel(row_frame, text=prospect['nom_prospect']).grid(row=0, column=0, padx=5, pady=10)
                
                # Montants
                ctk.CTkLabel(row_frame, text=format_montant(prospect['investissement_licence'])).grid(row=0, column=1, padx=5, pady=10)
                ctk.CTkLabel(row_frame, text=format_montant(prospect['investissement_materiel'])).grid(row=0, column=2, padx=5, pady=10)
                ctk.CTkLabel(row_frame, text=format_montant(prospect['investissement_logiciel'])).grid(row=0, column=3, padx=5, pady=10)
                ctk.CTkLabel(row_frame, text=format_montant(prospect['cout_formation'])).grid(row=0, column=4, padx=5, pady=10)
                ctk.CTkLabel(row_frame, text=format_montant(prospect['frais_maintenance'])).grid(row=0, column=5, padx=5, pady=10)
                
                # Total en gras
                total_label = ctk.CTkLabel(
                    row_frame, 
                    text=format_montant(prospect['total_estime']), 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color="#4ecdc4"
                )
                total_label.grid(row=0, column=6, padx=5, pady=10)
                
                # Actions
                actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                actions_frame.grid(row=0, column=7, padx=5, pady=5)
                
                edit_btn = ctk.CTkButton(
                    actions_frame, 
                    text="✏️", 
                    width=40,
                    command=lambda p=prospect: self.edit_prospect_dialog(p, window)
                )
                edit_btn.pack(side="left", padx=2)
                
                del_btn = ctk.CTkButton(
                    actions_frame, 
                    text="🗑️", 
                    width=40, 
                    fg_color=COLOR_DANGER,
                    command=lambda p=prospect: self.delete_prospect_confirm(p['id'], window)
                )
                del_btn.pack(side="left", padx=2)
    
    def add_prospect_dialog(self, parent_window):
        """Show dialog to add a prospect."""
        dialog = ctk.CTkToplevel(parent_window)
        dialog.title("Ajouter un Prospect")
        dialog.geometry("500x650")
        dialog.transient(parent_window)
        dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nom prospect
        ctk.CTkLabel(main_frame, text="Nom du Prospect *", anchor="w").pack(fill="x", pady=(0, 5))
        nom_entry = ctk.CTkEntry(main_frame, placeholder_text="Nom du prospect/fournisseur")
        nom_entry.pack(fill="x", pady=(0, 10))
        
        # Description offre
        ctk.CTkLabel(main_frame, text="Description de l'offre", anchor="w").pack(fill="x", pady=(0, 5))
        desc_text = ctk.CTkTextbox(main_frame, height=60)
        desc_text.pack(fill="x", pady=(0, 10))
        
        # Technologies
        ctk.CTkLabel(main_frame, text="Technologies proposées", anchor="w").pack(fill="x", pady=(0, 5))
        tech_text = ctk.CTkTextbox(main_frame, height=60)
        tech_text.pack(fill="x", pady=(0, 10))
        
        # Financial fields
        ctk.CTkLabel(main_frame, text="Investissement Licence (€)", anchor="w").pack(fill="x", pady=(0, 5))
        licence_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        licence_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Investissement Matériel (€)", anchor="w").pack(fill="x", pady=(0, 5))
        materiel_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        materiel_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Investissement Logiciel (€)", anchor="w").pack(fill="x", pady=(0, 5))
        logiciel_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        logiciel_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Coût Formation (€)", anchor="w").pack(fill="x", pady=(0, 5))
        formation_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        formation_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Frais de Maintenance (€)", anchor="w").pack(fill="x", pady=(0, 5))
        maintenance_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        maintenance_entry.pack(fill="x", pady=(0, 10))
        
        # Notes
        ctk.CTkLabel(main_frame, text="Notes", anchor="w").pack(fill="x", pady=(0, 5))
        notes_text = ctk.CTkTextbox(main_frame, height=60)
        notes_text.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save_prospect():
            nom = nom_entry.get().strip()
            if not nom:
                messagebox.showerror("Erreur", "Le nom du prospect est requis")
                return
            
            try:
                licence = float(licence_entry.get() or 0)
                materiel = float(materiel_entry.get() or 0)
                logiciel = float(logiciel_entry.get() or 0)
                formation = float(formation_entry.get() or 0)
                maintenance = float(maintenance_entry.get() or 0)
            except ValueError:
                messagebox.showerror("Erreur", "Les montants doivent être des nombres valides")
                return
            
            success, msg = self.projet_manager.add_prospect(
                self.projet.id,
                nom,
                desc_text.get("1.0", "end-1c").strip(),
                licence, materiel, logiciel, formation, maintenance,
                tech_text.get("1.0", "end-1c").strip(),
                notes_text.get("1.0", "end-1c").strip()
            )
            
            if success:
                messagebox.showinfo("Succès", msg)
                self.refresh_prospects_list(parent_window)
                dialog.destroy()
            else:
                messagebox.showerror("Erreur", msg)
        
        ctk.CTkButton(
            btn_frame, 
            text="Annuler", 
            command=dialog.destroy,
            fg_color="gray40"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Enregistrer", 
            command=save_prospect,
            fg_color=COLOR_SUCCESS
        ).pack(side="right", padx=5)
    
    def edit_prospect_dialog(self, prospect, parent_window):
        """Show dialog to edit a prospect."""
        dialog = ctk.CTkToplevel(parent_window)
        dialog.title("Modifier un Prospect")
        dialog.geometry("500x650")
        dialog.transient(parent_window)
        dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nom prospect
        ctk.CTkLabel(main_frame, text="Nom du Prospect *", anchor="w").pack(fill="x", pady=(0, 5))
        nom_entry = ctk.CTkEntry(main_frame, placeholder_text="Nom du prospect/fournisseur")
        nom_entry.insert(0, prospect['nom_prospect'])
        nom_entry.pack(fill="x", pady=(0, 10))
        
        # Description offre
        ctk.CTkLabel(main_frame, text="Description de l'offre", anchor="w").pack(fill="x", pady=(0, 5))
        desc_text = ctk.CTkTextbox(main_frame, height=60)
        if prospect['description_offre']:
            desc_text.insert("1.0", prospect['description_offre'])
        desc_text.pack(fill="x", pady=(0, 10))
        
        # Technologies
        ctk.CTkLabel(main_frame, text="Technologies proposées", anchor="w").pack(fill="x", pady=(0, 5))
        tech_text = ctk.CTkTextbox(main_frame, height=60)
        if prospect['technologies']:
            tech_text.insert("1.0", prospect['technologies'])
        tech_text.pack(fill="x", pady=(0, 10))
        
        # Financial fields
        ctk.CTkLabel(main_frame, text="Investissement Licence (€)", anchor="w").pack(fill="x", pady=(0, 5))
        licence_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        licence_entry.insert(0, str(prospect['investissement_licence']))
        licence_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Investissement Matériel (€)", anchor="w").pack(fill="x", pady=(0, 5))
        materiel_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        materiel_entry.insert(0, str(prospect['investissement_materiel']))
        materiel_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Investissement Logiciel (€)", anchor="w").pack(fill="x", pady=(0, 5))
        logiciel_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        logiciel_entry.insert(0, str(prospect['investissement_logiciel']))
        logiciel_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Coût Formation (€)", anchor="w").pack(fill="x", pady=(0, 5))
        formation_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        formation_entry.insert(0, str(prospect['cout_formation']))
        formation_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Frais de Maintenance (€)", anchor="w").pack(fill="x", pady=(0, 5))
        maintenance_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        maintenance_entry.insert(0, str(prospect['frais_maintenance']))
        maintenance_entry.pack(fill="x", pady=(0, 10))
        
        # Notes
        ctk.CTkLabel(main_frame, text="Notes", anchor="w").pack(fill="x", pady=(0, 5))
        notes_text = ctk.CTkTextbox(main_frame, height=60)
        if prospect['notes']:
            notes_text.insert("1.0", prospect['notes'])
        notes_text.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save_prospect():
            nom = nom_entry.get().strip()
            if not nom:
                messagebox.showerror("Erreur", "Le nom du prospect est requis")
                return
            
            try:
                licence = float(licence_entry.get() or 0)
                materiel = float(materiel_entry.get() or 0)
                logiciel = float(logiciel_entry.get() or 0)
                formation = float(formation_entry.get() or 0)
                maintenance = float(maintenance_entry.get() or 0)
            except ValueError:
                messagebox.showerror("Erreur", "Les montants doivent être des nombres valides")
                return
            
            success, msg = self.projet_manager.update_prospect(
                prospect['id'],
                nom_prospect=nom,
                description_offre=desc_text.get("1.0", "end-1c").strip(),
                investissement_licence=licence,
                investissement_materiel=materiel,
                investissement_logiciel=logiciel,
                cout_formation=formation,
                frais_maintenance=maintenance,
                technologies=tech_text.get("1.0", "end-1c").strip(),
                notes=notes_text.get("1.0", "end-1c").strip()
            )
            
            if success:
                messagebox.showinfo("Succès", msg)
                self.refresh_prospects_list(parent_window)
                dialog.destroy()
            else:
                messagebox.showerror("Erreur", msg)
        
        ctk.CTkButton(
            btn_frame, 
            text="Annuler", 
            command=dialog.destroy,
            fg_color="gray40"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Enregistrer", 
            command=save_prospect,
            fg_color=COLOR_SUCCESS
        ).pack(side="right", padx=5)
    
    def delete_prospect_confirm(self, prospect_id, parent_window):
        """Confirm and delete a prospect."""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce prospect ?"):
            success, msg = self.projet_manager.delete_prospect(prospect_id)
            if success:
                messagebox.showinfo("Succès", msg)
                self.refresh_prospects_list(parent_window)
            else:
                messagebox.showerror("Erreur", msg)
    
    def export_to_excel(self):
        """Export project to Excel."""
        from tkinter import filedialog
        import os
        from datetime import datetime
        
        # Demander où sauvegarder
        filename = f"Projet_{self.projet.nom_projet}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        # Clean filename
        filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.')).rstrip()
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=filename
        )
        
        if filepath:
            success, message = self.projet_manager.export_projet_to_excel(self.projet.id, filepath)
            
            if success:
                messagebox.showinfo("Succès", message)
                # Ouvrir le fichier
                if messagebox.askyesno("Ouvrir", "Voulez-vous ouvrir le fichier Excel ?"):
                    try:
                        if os.name == 'nt':  # Windows
                            os.startfile(filepath)
                        elif os.name == 'posix':  # macOS and Linux
                            import subprocess
                            subprocess.call(['open' if os.uname()[0] == 'Darwin' else 'xdg-open', filepath])
                    except Exception as e:
                        messagebox.showwarning("Avertissement", f"Impossible d'ouvrir le fichier: {e}")
            else:
                messagebox.showerror("Erreur", message)
