"""
Bons de Commande View - Gestion complète des bons de commande.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Optional
from database.db_manager import DatabaseManager
from business.bc_manager import BCManager
from business.budget_manager import BudgetManager
from business.client_manager import ClientManager
from business.contrat_manager import ContratManager
from database.models import BonCommande
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD, NATURES_BUDGET, TYPES_BC
)
from utils.formatters import format_montant, format_datetime
from utils.validators import validate_montant, validate_required_field


class BonsCommandeView(ctk.CTkFrame):
    """Purchase orders management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize bons de commande view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.bc_manager = BCManager(db_manager)
        self.budget_manager = BudgetManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        self.contrat_manager = ContratManager(db_manager)
        
        self.create_widgets()
        self.load_bcs()
    
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
            text="📋 Gestion des Bons de Commande",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        new_btn = ctk.CTkButton(
            header_frame,
            text="➕ Nouveau BC",
            command=self.show_create_dialog,
            width=150,
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
            values=["Tous", "Validés", "En attente"],
            width=120,
            command=lambda _: self.load_bcs()
        )
        self.statut_filter.set("Tous")
        self.statut_filter.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Nature:").pack(side="left", padx=(20, 5))
        self.nature_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Tous"] + NATURES_BUDGET,
            width=150,
            command=lambda _: self.load_bcs()
        )
        self.nature_filter.set("Tous")
        self.nature_filter.pack(side="left", padx=5)
        
        # Scrollable frame for BCs
        self.bcs_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.bcs_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.bcs_scroll.grid_columnconfigure(0, weight=1)
    
    def load_bcs(self):
        """Load and display BCs."""
        # Clear existing
        for widget in self.bcs_scroll.winfo_children():
            widget.destroy()
        
        # Get filters
        statut = self.statut_filter.get()
        valide = None
        if statut == "Validés":
            valide = True
        elif statut == "En attente":
            valide = False
        
        nature = self.nature_filter.get()
        nature = None if nature == "Tous" else nature
        
        # Load BCs
        bcs = self.bc_manager.get_all_bcs(valide=valide, nature=nature)
        
        if not bcs:
            no_data_label = ctk.CTkLabel(
                self.bcs_scroll,
                text="Aucun bon de commande trouvé",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            )
            no_data_label.pack(pady=50)
            return
        
        # Display BCs
        for bc in bcs:
            self.create_bc_card(bc)
    
    def create_bc_card(self, bc: BonCommande):
        """Create a BC card."""
        # Card color based on validation status
        card_color = COLOR_BG_CARD if bc.valide else "#1a1a2e"
        
        card = ctk.CTkFrame(self.bcs_scroll, fg_color=card_color, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=15)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Validation status badge
        if bc.valide:
            status_label = ctk.CTkLabel(
                info_frame,
                text="✅ VALIDÉ",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLOR_SUCCESS
            )
            status_label.grid(row=0, column=0, sticky="w")
        else:
            status_label = ctk.CTkLabel(
                info_frame,
                text="⏳ EN ATTENTE",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLOR_WARNING
            )
            status_label.grid(row=0, column=0, sticky="w")
        
        # BC number
        numero_label = ctk.CTkLabel(
            info_frame,
            text=f"📋 {bc.numero_bc}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        numero_label.grid(row=1, column=0, sticky="w", columnspan=2, pady=(5, 0))
        
        # Get client name
        client = self.client_manager.get_client_by_id(bc.client_id)
        client_name = client.nom if client else "Client inconnu"
        
        client_label = ctk.CTkLabel(
            info_frame,
            text=f"🏢 {client_name}",
            font=ctk.CTkFont(size=13),
            text_color="gray70"
        )
        client_label.grid(row=2, column=0, sticky="w", columnspan=2, pady=(2, 0))
        
        # BC details frame
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Nature
        ctk.CTkLabel(
            details_frame,
            text="Nature",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=0, sticky="w")
        
        nature_color = COLOR_PRIMARY if bc.nature == "Fonctionnement" else COLOR_SUCCESS
        ctk.CTkLabel(
            details_frame,
            text=bc.nature,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=nature_color
        ).grid(row=1, column=0, sticky="w")
        
        # Type
        ctk.CTkLabel(
            details_frame,
            text="Type",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=1)
        
        ctk.CTkLabel(
            details_frame,
            text=bc.type,
            font=ctk.CTkFont(size=13),
            text_color="white"
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
            text=format_montant(bc.montant),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_SUCCESS if bc.valide else COLOR_WARNING
        ).grid(row=1, column=2, sticky="e")
        
        # Service demandeur
        if bc.service_demandeur:
            service_label = ctk.CTkLabel(
                info_frame,
                text=f"📌 Service: {bc.service_demandeur}",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            service_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))
        
        # Validation date if validated
        if bc.valide and bc.date_validation:
            date_label = ctk.CTkLabel(
                info_frame,
                text=f"🕐 Validé le: {format_datetime(bc.date_validation)}",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            date_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=(5, 0))
        
        # Description
        if bc.description:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=f"📝 {bc.description[:100]}{'...' if len(bc.description) > 100 else ''}",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            desc_label.grid(row=6, column=0, columnspan=3, sticky="w", pady=(5, 0))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        if not bc.valide:
            # Show validation button for non-validated BCs
            validate_btn = ctk.CTkButton(
                btn_frame,
                text="✅ Valider",
                command=lambda b=bc: self.validate_bc(b),
                width=100,
                height=28,
                fg_color=COLOR_SUCCESS,
                hover_color=COLOR_PRIMARY
            )
            validate_btn.pack(side="right", padx=5)
            
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="✏️ Modifier",
                command=lambda b=bc: self.show_edit_dialog(b),
                width=100,
                height=28,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_SUCCESS
            )
            edit_btn.pack(side="right", padx=5)
            
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Supprimer",
                command=lambda b=bc: self.delete_bc(b),
                width=100,
                height=28,
                fg_color=COLOR_DANGER,
                hover_color="#cc0000"
            )
            delete_btn.pack(side="right", padx=5)
        else:
            # Show info button for validated BCs
            info_label = ctk.CTkLabel(
                btn_frame,
                text="ℹ️ BC validé - Modification impossible",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            info_label.pack(side="right", padx=5)
    
    def show_create_dialog(self):
        """Show dialog to create a new BC."""
        dialog = BCDialog(self, self.db_manager, title="Créer un Bon de Commande")
        dialog.wait_window()
        if dialog.result:
            self.load_bcs()
    
    def show_edit_dialog(self, bc: BonCommande):
        """Show dialog to edit a BC."""
        dialog = BCDialog(self, self.db_manager, bc=bc, title="Modifier le Bon de Commande")
        dialog.wait_window()
        if dialog.result:
            self.load_bcs()
    
    def delete_bc(self, bc: BonCommande):
        """Delete a BC."""
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce BC?\n\n"
            f"Numéro: {bc.numero_bc}\n"
            f"Montant: {format_montant(bc.montant)}"
        ):
            success, msg = self.bc_manager.delete_bc(bc.id)
            if success:
                messagebox.showinfo("Succès", msg)
                self.load_bcs()
            else:
                messagebox.showerror("Erreur", msg)
    
    def validate_bc(self, bc: BonCommande):
        """Validate a BC and impute to budget."""
        client = self.client_manager.get_client_by_id(bc.client_id)
        client_name = client.nom if client else "Client inconnu"
        
        if messagebox.askyesno(
            "Confirmation",
            f"Valider ce BC?\n\n"
            f"Numéro: {bc.numero_bc}\n"
            f"Client: {client_name}\n"
            f"Nature: {bc.nature}\n"
            f"Montant: {format_montant(bc.montant)}\n\n"
            f"⚠️ Cette action est irréversible et imputera le budget automatiquement."
        ):
            success, msg = self.bc_manager.valider_bc(bc.id, self.budget_manager)
            if success:
                messagebox.showinfo("Succès", msg)
                self.load_bcs()
            else:
                messagebox.showerror("Erreur", msg)


class BCDialog(ctk.CTkToplevel):
    """Dialog for creating/editing BCs."""
    
    def __init__(self, parent, db_manager: DatabaseManager, bc: Optional[BonCommande] = None, title: str = "Bon de Commande"):
        super().__init__(parent)
        self.db_manager = db_manager
        self.bc_manager = BCManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        self.contrat_manager = ContratManager(db_manager)
        self.bc = bc
        self.result = None
        
        self.title(title)
        self.geometry("550x650")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if bc:
            self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame with scrolling
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # BC number (auto-generated or display)
        if not self.bc:
            numero_label = ctk.CTkLabel(
                main_frame,
                text=f"Numéro BC: {self.bc_manager.generate_next_numero()} (auto-généré)",
                font=ctk.CTkFont(size=12),
                text_color=COLOR_SUCCESS
            )
            numero_label.pack(fill="x", pady=(0, 15))
        else:
            numero_label = ctk.CTkLabel(
                main_frame,
                text=f"Numéro BC: {self.bc.numero_bc}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            numero_label.pack(fill="x", pady=(0, 15))
        
        # Client
        ctk.CTkLabel(main_frame, text="Client *", anchor="w").pack(fill="x", pady=(0, 5))
        clients = self.client_manager.get_all_clients()
        client_names = {c.nom: c.id for c in clients if c.actif}
        self.client_combo = ctk.CTkComboBox(main_frame, values=list(client_names.keys()))
        self.client_combo.pack(fill="x", pady=(0, 15))
        self.client_combo.client_names = client_names
        self.client_combo.configure(command=self.on_client_change)
        
        # Contrat (optional)
        ctk.CTkLabel(main_frame, text="Contrat (optionnel)", anchor="w").pack(fill="x", pady=(0, 5))
        self.contrat_combo = ctk.CTkComboBox(main_frame, values=["Aucun"])
        self.contrat_combo.pack(fill="x", pady=(0, 15))
        self.contrat_combo.contrat_map = {}
        
        # Nature
        ctk.CTkLabel(main_frame, text="Nature *", anchor="w").pack(fill="x", pady=(0, 5))
        self.nature_combo = ctk.CTkComboBox(main_frame, values=NATURES_BUDGET)
        self.nature_combo.pack(fill="x", pady=(0, 15))
        
        # Type
        ctk.CTkLabel(main_frame, text="Type *", anchor="w").pack(fill="x", pady=(0, 5))
        self.type_combo = ctk.CTkComboBox(main_frame, values=TYPES_BC)
        self.type_combo.pack(fill="x", pady=(0, 15))
        
        # Service demandeur
        ctk.CTkLabel(main_frame, text="Service Demandeur", anchor="w").pack(fill="x", pady=(0, 5))
        self.service_entry = ctk.CTkEntry(main_frame, placeholder_text="Optionnel")
        self.service_entry.pack(fill="x", pady=(0, 15))
        
        # Montant
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
        """Update contract list when client changes."""
        if choice in self.client_combo.client_names:
            client_id = self.client_combo.client_names[choice]
            contrats = self.contrat_manager.get_all_contrats()
            client_contrats = [c for c in contrats if c.client_id == client_id and c.statut == "Actif"]
            
            self.contrat_combo.contrat_map = {c.numero_contrat: c.id for c in client_contrats}
            contrat_values = ["Aucun"] + list(self.contrat_combo.contrat_map.keys())
            self.contrat_combo.configure(values=contrat_values)
            self.contrat_combo.set("Aucun")
    
    def populate_data(self):
        """Populate form with BC data."""
        if self.bc:
            # Set client
            client = self.client_manager.get_client_by_id(self.bc.client_id)
            if client:
                self.client_combo.set(client.nom)
                self.on_client_change(client.nom)
            
            # Set contrat if exists
            if self.bc.contrat_id:
                contrat = self.contrat_manager.get_contrat_by_id(self.bc.contrat_id)
                if contrat and contrat.numero_contrat in self.contrat_combo.contrat_map:
                    self.contrat_combo.set(contrat.numero_contrat)
            
            self.nature_combo.set(self.bc.nature)
            self.type_combo.set(self.bc.type)
            
            if self.bc.service_demandeur:
                self.service_entry.insert(0, self.bc.service_demandeur)
            
            self.montant_entry.insert(0, str(self.bc.montant))
            
            if self.bc.description:
                self.description_text.insert("1.0", self.bc.description)
    
    def save(self):
        """Save the BC."""
        try:
            # Validate
            client_nom = self.client_combo.get()
            if not client_nom or client_nom not in self.client_combo.client_names:
                messagebox.showerror("Erreur", "Veuillez sélectionner un client")
                return
            
            client_id = self.client_combo.client_names[client_nom]
            
            # Get contrat ID
            contrat_id = None
            contrat_num = self.contrat_combo.get()
            if contrat_num != "Aucun" and contrat_num in self.contrat_combo.contrat_map:
                contrat_id = self.contrat_combo.contrat_map[contrat_num]
            
            nature = self.nature_combo.get()
            valid, msg = validate_required_field(nature, "Nature")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            bc_type = self.type_combo.get()
            valid, msg = validate_required_field(bc_type, "Type")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            service = self.service_entry.get().strip()
            
            montant = float(self.montant_entry.get().replace(',', '.'))
            if not validate_montant(montant) or montant <= 0:
                messagebox.showerror("Erreur", "Montant invalide (doit être > 0)")
                return
            
            description = self.description_text.get("1.0", "end-1c").strip()
            
            # Create or update BC
            if self.bc:
                # Update
                self.bc.client_id = client_id
                self.bc.contrat_id = contrat_id
                self.bc.nature = nature
                self.bc.type = bc_type
                self.bc.service_demandeur = service
                self.bc.montant = montant
                self.bc.description = description
                
                success, msg = self.bc_manager.update_bc(self.bc)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
            else:
                # Create
                new_bc = BonCommande(
                    client_id=client_id,
                    contrat_id=contrat_id,
                    nature=nature,
                    type=bc_type,
                    service_demandeur=service,
                    montant=montant,
                    description=description
                )
                
                success, msg, bc_id = self.bc_manager.create_bc(new_bc)
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
