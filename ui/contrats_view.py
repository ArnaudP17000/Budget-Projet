"""
Contrats View - Gestion complète des contrats.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date, timedelta
from typing import Optional
from database.db_manager import DatabaseManager
from business.contrat_manager import ContratManager
from business.client_manager import ClientManager
from business.contact_manager import ContactManager
from database.models import Contrat
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD, STATUTS_CONTRAT, STATUT_ACTIF
)
from utils.formatters import format_montant, format_date, parse_date
from utils.validators import validate_montant, validate_date_range, validate_required_field


class ContratsView(ctk.CTkFrame):
    """Contracts management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize contracts view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.contrat_manager = ContratManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        self.contact_manager = ContactManager(db_manager)
        
        self.create_widgets()
        self.load_contrats()
    
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
            text="📄 Gestion des Contrats",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        new_btn = ctk.CTkButton(
            header_frame,
            text="➕ Nouveau Contrat",
            command=self.show_create_dialog,
            width=180,
            height=36,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        new_btn.grid(row=0, column=2, padx=5)
        
        update_alerts_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Actualiser Alertes",
            command=self.update_alerts,
            width=180,
            height=36,
            fg_color=COLOR_WARNING,
            hover_color=COLOR_PRIMARY
        )
        update_alerts_btn.grid(row=0, column=3, padx=5)
        
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
            values=["Tous"] + STATUTS_CONTRAT,
            width=120,
            command=lambda _: self.load_contrats()
        )
        self.statut_filter.set("Tous")
        self.statut_filter.pack(side="left", padx=5)
        
        self.alerte_only_var = ctk.BooleanVar(value=False)
        alerte_check = ctk.CTkCheckBox(
            filter_frame,
            text="Alertes uniquement",
            variable=self.alerte_only_var,
            command=self.load_contrats
        )
        alerte_check.pack(side="left", padx=20)
        
        # Scrollable frame for contracts
        self.contrats_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.contrats_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.contrats_scroll.grid_columnconfigure(0, weight=1)
    
    def load_contrats(self):
        """Load and display contracts."""
        # Clear existing
        for widget in self.contrats_scroll.winfo_children():
            widget.destroy()
        
        # Get filters
        statut = self.statut_filter.get()
        statut = None if statut == "Tous" else statut
        alerte_only = self.alerte_only_var.get()
        
        # Load contracts
        contrats = self.contrat_manager.get_all_contrats(statut=statut, alerte_only=alerte_only)
        
        if not contrats:
            no_data_label = ctk.CTkLabel(
                self.contrats_scroll,
                text="Aucun contrat trouvé",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            )
            no_data_label.pack(pady=50)
            return
        
        # Display contracts
        for contrat in contrats:
            self.create_contrat_card(contrat)
    
    def create_contrat_card(self, contrat: Contrat):
        """Create a contract card."""
        # Determine card color based on alert status
        if contrat.alerte_6_mois and contrat.statut == STATUT_ACTIF and contrat.date_fin:
            # Calculate days until expiration
            days_until_expiry = (contrat.date_fin - date.today()).days
            if days_until_expiry < 30:
                card_color = "#2d1a1a"  # Dark red tint
            elif days_until_expiry < 90:
                card_color = "#2d2414"  # Dark orange tint
            else:
                card_color = "#2d2814"  # Dark yellow tint
        else:
            card_color = COLOR_BG_CARD
        
        card = ctk.CTkFrame(self.contrats_scroll, fg_color=card_color, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=15)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Alert indicator
        if contrat.alerte_6_mois and contrat.statut == STATUT_ACTIF:
            alert_label = ctk.CTkLabel(
                info_frame,
                text="⚠️ ALERTE",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLOR_DANGER
            )
            alert_label.grid(row=0, column=0, sticky="w")
        
        # Contract number and client
        numero_label = ctk.CTkLabel(
            info_frame,
            text=f"📄 {contrat.numero_contrat}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        numero_label.grid(row=1, column=0, sticky="w", columnspan=2, pady=(5, 0))
        
        # Get client name
        client = self.client_manager.get_client_by_id(contrat.client_id)
        client_name = client.nom if client else "Client inconnu"
        
        client_label = ctk.CTkLabel(
            info_frame,
            text=f"🏢 {client_name}",
            font=ctk.CTkFont(size=13),
            text_color="gray70"
        )
        client_label.grid(row=2, column=0, sticky="w", columnspan=2, pady=(2, 0))
        
        # Status badge
        statut_color = COLOR_SUCCESS if contrat.statut == STATUT_ACTIF else COLOR_DANGER
        statut_label = ctk.CTkLabel(
            info_frame,
            text=contrat.statut,
            font=ctk.CTkFont(size=11),
            text_color=statut_color
        )
        statut_label.grid(row=1, column=2, sticky="e", padx=5)
        
        # Contract details
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Date debut
        ctk.CTkLabel(
            details_frame,
            text="Date Début",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            details_frame,
            text=format_date(contrat.date_debut),
            font=ctk.CTkFont(size=13),
            text_color="white"
        ).grid(row=1, column=0, sticky="w")
        
        # Date fin
        ctk.CTkLabel(
            details_frame,
            text="Date Fin",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=1)
        
        date_fin_color = COLOR_DANGER if contrat.alerte_6_mois else "white"
        ctk.CTkLabel(
            details_frame,
            text=format_date(contrat.date_fin),
            font=ctk.CTkFont(size=13, weight="bold" if contrat.alerte_6_mois else "normal"),
            text_color=date_fin_color
        ).grid(row=1, column=1)
        
        # Montant
        ctk.CTkLabel(
            details_frame,
            text="Montant",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=2, sticky="e")
        
        ctk.CTkLabel(
            details_frame,
            text=format_montant(contrat.montant),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_SUCCESS
        ).grid(row=1, column=2, sticky="e")
        
        # Days until expiry (if alert)
        if contrat.alerte_6_mois and contrat.date_fin and contrat.statut == STATUT_ACTIF:
            days_left = (contrat.date_fin - date.today()).days
            if days_left >= 0:
                days_label = ctk.CTkLabel(
                    info_frame,
                    text=f"⏰ Expire dans {days_left} jours",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLOR_WARNING
                )
                days_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))
        
        # Description
        if contrat.description:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=f"📋 {contrat.description[:100]}{'...' if len(contrat.description) > 100 else ''}",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            desc_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Modifier",
            command=lambda c=contrat: self.show_edit_dialog(c),
            width=100,
            height=28,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        edit_btn.pack(side="right", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Supprimer",
            command=lambda c=contrat: self.delete_contrat(c),
            width=100,
            height=28,
            fg_color=COLOR_DANGER,
            hover_color="#cc0000"
        )
        delete_btn.pack(side="right", padx=5)
    
    def show_create_dialog(self):
        """Show dialog to create a new contract."""
        dialog = ContratDialog(self, self.db_manager, title="Créer un Contrat")
        dialog.wait_window()
        if dialog.result:
            self.load_contrats()
    
    def show_edit_dialog(self, contrat: Contrat):
        """Show dialog to edit a contract."""
        dialog = ContratDialog(self, self.db_manager, contrat=contrat, title="Modifier le Contrat")
        dialog.wait_window()
        if dialog.result:
            self.load_contrats()
    
    def delete_contrat(self, contrat: Contrat):
        """Delete a contract."""
        client = self.client_manager.get_client_by_id(contrat.client_id)
        client_name = client.nom if client else "Client inconnu"
        
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce contrat?\n\n"
            f"Numéro: {contrat.numero_contrat}\n"
            f"Client: {client_name}\n"
            f"Montant: {format_montant(contrat.montant)}"
        ):
            success, msg = self.contrat_manager.delete_contrat(contrat.id)
            if success:
                messagebox.showinfo("Succès", msg)
                self.load_contrats()
            else:
                messagebox.showerror("Erreur", msg)
    
    def update_alerts(self):
        """Update contract alerts."""
        count = self.contrat_manager.update_alerts()
        messagebox.showinfo("Alertes Mises à Jour", f"{count} alerte(s) détectée(s)")
        self.load_contrats()


class ContratDialog(ctk.CTkToplevel):
    """Dialog for creating/editing contracts."""
    
    def __init__(self, parent, db_manager: DatabaseManager, contrat: Optional[Contrat] = None, title: str = "Contrat"):
        super().__init__(parent)
        self.db_manager = db_manager
        self.contrat_manager = ContratManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        self.contact_manager = ContactManager(db_manager)
        self.contrat = contrat
        self.result = None
        
        self.title(title)
        self.geometry("550x700")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if contrat:
            self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame with scrolling
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Contract number
        ctk.CTkLabel(main_frame, text="Numéro de Contrat *", anchor="w").pack(fill="x", pady=(0, 5))
        self.numero_entry = ctk.CTkEntry(main_frame, placeholder_text="CTR-2024-001")
        self.numero_entry.pack(fill="x", pady=(0, 15))
        
        # Client
        ctk.CTkLabel(main_frame, text="Client *", anchor="w").pack(fill="x", pady=(0, 5))
        clients = self.client_manager.get_all_clients()
        client_names = {c.nom: c.id for c in clients if c.actif}
        self.client_combo = ctk.CTkComboBox(main_frame, values=list(client_names.keys()))
        self.client_combo.pack(fill="x", pady=(0, 15))
        self.client_combo.client_names = client_names
        self.client_combo.configure(command=self.on_client_change)
        
        # Contact
        ctk.CTkLabel(main_frame, text="Contact", anchor="w").pack(fill="x", pady=(0, 5))
        self.contact_combo = ctk.CTkComboBox(main_frame, values=["Aucun"])
        self.contact_combo.pack(fill="x", pady=(0, 15))
        self.contact_combo.contact_map = {}
        
        # Status
        ctk.CTkLabel(main_frame, text="Statut *", anchor="w").pack(fill="x", pady=(0, 5))
        self.statut_combo = ctk.CTkComboBox(main_frame, values=STATUTS_CONTRAT)
        self.statut_combo.set(STATUT_ACTIF)
        self.statut_combo.pack(fill="x", pady=(0, 15))
        
        # Dates frame
        dates_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        dates_frame.pack(fill="x", pady=(0, 15))
        dates_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Date debut
        ctk.CTkLabel(dates_frame, text="Date Début *", anchor="w").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.date_debut_entry = ctk.CTkEntry(dates_frame, placeholder_text="YYYY-MM-DD")
        self.date_debut_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        # Date fin
        ctk.CTkLabel(dates_frame, text="Date Fin *", anchor="w").grid(row=0, column=1, sticky="w", padx=(5, 0))
        self.date_fin_entry = ctk.CTkEntry(dates_frame, placeholder_text="YYYY-MM-DD")
        self.date_fin_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Amount
        ctk.CTkLabel(main_frame, text="Montant (€) *", anchor="w").pack(fill="x", pady=(0, 5))
        self.montant_entry = ctk.CTkEntry(main_frame, placeholder_text="0.00")
        self.montant_entry.pack(fill="x", pady=(0, 15))
        
        # Description
        ctk.CTkLabel(main_frame, text="Description", anchor="w").pack(fill="x", pady=(0, 5))
        self.description_text = ctk.CTkTextbox(main_frame, height=100)
        self.description_text.pack(fill="x", pady=(0, 15))
        
        # Buttons frame (fixed at bottom)
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
    
    def on_client_change(self, choice):
        """Update contact list when client changes."""
        if choice in self.client_combo.client_names:
            client_id = self.client_combo.client_names[choice]
            contacts = self.contact_manager.get_all_contacts(client_id=client_id)
            
            self.contact_combo.contact_map = {f"{c.prenom} {c.nom}": c.id for c in contacts}
            contact_values = ["Aucun"] + list(self.contact_combo.contact_map.keys())
            self.contact_combo.configure(values=contact_values)
            self.contact_combo.set("Aucun")
    
    def populate_data(self):
        """Populate form with contract data."""
        if self.contrat:
            self.numero_entry.insert(0, self.contrat.numero_contrat)
            
            # Set client
            client = self.client_manager.get_client_by_id(self.contrat.client_id)
            if client:
                self.client_combo.set(client.nom)
                self.on_client_change(client.nom)
            
            # Set contact if exists
            if self.contrat.contact_id:
                contact = self.contact_manager.get_contact_by_id(self.contrat.contact_id)
                if contact:
                    contact_name = f"{contact.prenom} {contact.nom}"
                    if contact_name in self.contact_combo.contact_map:
                        self.contact_combo.set(contact_name)
            
            self.statut_combo.set(self.contrat.statut)
            
            if self.contrat.date_debut:
                self.date_debut_entry.insert(0, format_date(self.contrat.date_debut))
            if self.contrat.date_fin:
                self.date_fin_entry.insert(0, format_date(self.contrat.date_fin))
            
            self.montant_entry.insert(0, str(self.contrat.montant))
            
            if self.contrat.description:
                self.description_text.insert("1.0", self.contrat.description)
    
    def save(self):
        """Save the contract."""
        try:
            # Validate
            numero = self.numero_entry.get().strip()
            valid, msg = validate_required_field(numero, "Numéro de contrat")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            client_nom = self.client_combo.get()
            if not client_nom or client_nom not in self.client_combo.client_names:
                messagebox.showerror("Erreur", "Veuillez sélectionner un client")
                return
            
            client_id = self.client_combo.client_names[client_nom]
            
            # Get contact ID
            contact_id = None
            contact_nom = self.contact_combo.get()
            if contact_nom != "Aucun" and contact_nom in self.contact_combo.contact_map:
                contact_id = self.contact_combo.contact_map[contact_nom]
            
            statut = self.statut_combo.get()
            
            # Parse dates
            date_debut = parse_date(self.date_debut_entry.get().strip())
            date_fin = parse_date(self.date_fin_entry.get().strip())
            
            if not date_debut or not date_fin:
                messagebox.showerror("Erreur", "Dates invalides (format: YYYY-MM-DD)")
                return
            
            if not validate_date_range(date_debut, date_fin):
                messagebox.showerror("Erreur", "La date de fin doit être postérieure à la date de début")
                return
            
            montant = float(self.montant_entry.get().replace(',', '.'))
            if not validate_montant(montant):
                messagebox.showerror("Erreur", "Montant invalide")
                return
            
            description = self.description_text.get("1.0", "end-1c").strip()
            
            # Create or update contract
            if self.contrat:
                # Update
                self.contrat.numero_contrat = numero
                self.contrat.client_id = client_id
                self.contrat.contact_id = contact_id
                self.contrat.statut = statut
                self.contrat.date_debut = date_debut
                self.contrat.date_fin = date_fin
                self.contrat.montant = montant
                self.contrat.description = description
                
                success, msg = self.contrat_manager.update_contrat(self.contrat)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
            else:
                # Create
                new_contrat = Contrat(
                    numero_contrat=numero,
                    client_id=client_id,
                    contact_id=contact_id,
                    statut=statut,
                    date_debut=date_debut,
                    date_fin=date_fin,
                    montant=montant,
                    description=description
                )
                
                success, msg, contrat_id = self.contrat_manager.create_contrat(new_contrat)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
                    
        except ValueError as e:
            messagebox.showerror("Erreur", f"Valeur invalide: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")
