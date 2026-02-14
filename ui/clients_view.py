"""
Clients View - Gestion complète des clients.
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from database.db_manager import DatabaseManager
from business.client_manager import ClientManager
from database.models import Client
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD
)
from utils.validators import validate_email, validate_telephone, validate_required_field


class ClientsView(ctk.CTkFrame):
    """Clients management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize clients view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.client_manager = ClientManager(db_manager)
        
        self.create_widgets()
        self.load_clients()
    
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
            text="🏢 Gestion des Clients",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        new_btn = ctk.CTkButton(
            header_frame,
            text="➕ Nouveau Client",
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
        
        self.show_inactive_var = ctk.BooleanVar(value=False)
        inactive_check = ctk.CTkCheckBox(
            filter_frame,
            text="Afficher les clients inactifs",
            variable=self.show_inactive_var,
            command=self.load_clients
        )
        inactive_check.pack(side="left", padx=5)
        
        # Scrollable frame for clients
        self.clients_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.clients_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.clients_scroll.grid_columnconfigure(0, weight=1)
    
    def load_clients(self):
        """Load and display clients."""
        # Clear existing
        for widget in self.clients_scroll.winfo_children():
            widget.destroy()
        
        # Get filter
        include_inactive = self.show_inactive_var.get()
        
        # Load clients
        clients = self.client_manager.get_all_clients(include_inactive=include_inactive)
        
        if not clients:
            no_data_label = ctk.CTkLabel(
                self.clients_scroll,
                text="Aucun client trouvé",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            )
            no_data_label.pack(pady=50)
            return
        
        # Display clients
        for client in clients:
            self.create_client_card(client)
    
    def create_client_card(self, client: Client):
        """Create a client card."""
        # Card color based on active status
        card_color = COLOR_BG_CARD if client.actif else "#1a1a1a"
        
        card = ctk.CTkFrame(self.clients_scroll, fg_color=card_color, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=15)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Status badge
        if not client.actif:
            status_label = ctk.CTkLabel(
                info_frame,
                text="❌ INACTIF",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLOR_DANGER
            )
            status_label.grid(row=0, column=0, sticky="w")
        
        # Client name
        nom_label = ctk.CTkLabel(
            info_frame,
            text=f"🏢 {client.nom}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white" if client.actif else "gray60"
        )
        nom_label.grid(row=1, column=0, sticky="w", columnspan=2, pady=(5, 0))
        
        # Raison sociale
        if client.raison_sociale:
            raison_label = ctk.CTkLabel(
                info_frame,
                text=client.raison_sociale,
                font=ctk.CTkFont(size=12),
                text_color="gray70"
            )
            raison_label.grid(row=2, column=0, sticky="w", columnspan=2, pady=(2, 0))
        
        # Details frame
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        details_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Address section
        if client.adresse or client.code_postal or client.ville:
            addr_parts = []
            if client.adresse:
                addr_parts.append(client.adresse)
            if client.code_postal or client.ville:
                city_part = f"{client.code_postal} {client.ville}".strip()
                if city_part:
                    addr_parts.append(city_part)
            
            if addr_parts:
                ctk.CTkLabel(
                    details_frame,
                    text="📍 Adresse",
                    font=ctk.CTkFont(size=11),
                    text_color="gray60"
                ).grid(row=0, column=0, sticky="w")
                
                ctk.CTkLabel(
                    details_frame,
                    text="\n".join(addr_parts),
                    font=ctk.CTkFont(size=12),
                    text_color="white" if client.actif else "gray60"
                ).grid(row=1, column=0, sticky="w")
        
        # Contact info section
        contact_info = []
        if client.telephone:
            contact_info.append(f"📞 {client.telephone}")
        if client.email:
            contact_info.append(f"✉️ {client.email}")
        
        if contact_info:
            ctk.CTkLabel(
                details_frame,
                text="Contact",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            ).grid(row=0, column=1, sticky="w", padx=(20, 0))
            
            ctk.CTkLabel(
                details_frame,
                text="\n".join(contact_info),
                font=ctk.CTkFont(size=12),
                text_color="white" if client.actif else "gray60"
            ).grid(row=1, column=1, sticky="w", padx=(20, 0))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Modifier",
            command=lambda c=client: self.show_edit_dialog(c),
            width=100,
            height=28,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        edit_btn.pack(side="right", padx=5)
        
        if client.actif:
            deactivate_btn = ctk.CTkButton(
                btn_frame,
                text="❌ Désactiver",
                command=lambda c=client: self.deactivate_client(c),
                width=120,
                height=28,
                fg_color=COLOR_WARNING,
                hover_color=COLOR_DANGER
            )
            deactivate_btn.pack(side="right", padx=5)
        else:
            activate_btn = ctk.CTkButton(
                btn_frame,
                text="✅ Activer",
                command=lambda c=client: self.activate_client(c),
                width=100,
                height=28,
                fg_color=COLOR_SUCCESS,
                hover_color=COLOR_PRIMARY
            )
            activate_btn.pack(side="right", padx=5)
    
    def show_create_dialog(self):
        """Show dialog to create a new client."""
        dialog = ClientDialog(self, self.db_manager, title="Créer un Client")
        dialog.wait_window()
        if dialog.result:
            self.load_clients()
    
    def show_edit_dialog(self, client: Client):
        """Show dialog to edit a client."""
        dialog = ClientDialog(self, self.db_manager, client=client, title="Modifier le Client")
        dialog.wait_window()
        if dialog.result:
            self.load_clients()
    
    def deactivate_client(self, client: Client):
        """Deactivate a client."""
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment désactiver ce client?\n\n"
            f"Nom: {client.nom}\n\n"
            f"Le client sera masqué par défaut mais ses données seront conservées."
        ):
            success, msg = self.client_manager.deactivate_client(client.id)
            if success:
                messagebox.showinfo("Succès", msg)
                self.load_clients()
            else:
                messagebox.showerror("Erreur", msg)
    
    def activate_client(self, client: Client):
        """Activate a client."""
        success, msg = self.client_manager.activate_client(client.id)
        if success:
            messagebox.showinfo("Succès", msg)
            self.load_clients()
        else:
            messagebox.showerror("Erreur", msg)


class ClientDialog(ctk.CTkToplevel):
    """Dialog for creating/editing clients."""
    
    def __init__(self, parent, db_manager: DatabaseManager, client: Optional[Client] = None, title: str = "Client"):
        super().__init__(parent)
        self.db_manager = db_manager
        self.client_manager = ClientManager(db_manager)
        self.client = client
        self.result = None
        
        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if client:
            self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Nom
        ctk.CTkLabel(main_frame, text="Nom *", anchor="w").pack(fill="x", pady=(0, 5))
        self.nom_entry = ctk.CTkEntry(main_frame, placeholder_text="Nom du client")
        self.nom_entry.pack(fill="x", pady=(0, 15))
        
        # Raison sociale
        ctk.CTkLabel(main_frame, text="Raison Sociale", anchor="w").pack(fill="x", pady=(0, 5))
        self.raison_entry = ctk.CTkEntry(main_frame, placeholder_text="Optionnel")
        self.raison_entry.pack(fill="x", pady=(0, 15))
        
        # Adresse
        ctk.CTkLabel(main_frame, text="Adresse", anchor="w").pack(fill="x", pady=(0, 5))
        self.adresse_entry = ctk.CTkEntry(main_frame, placeholder_text="Numéro et rue")
        self.adresse_entry.pack(fill="x", pady=(0, 15))
        
        # Code postal and ville
        city_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        city_frame.pack(fill="x", pady=(0, 15))
        city_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(city_frame, text="Code Postal", anchor="w").grid(row=0, column=0, sticky="w")
        self.cp_entry = ctk.CTkEntry(city_frame, placeholder_text="00000", width=100)
        self.cp_entry.grid(row=1, column=0, sticky="w")
        
        ctk.CTkLabel(city_frame, text="Ville", anchor="w").grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.ville_entry = ctk.CTkEntry(city_frame, placeholder_text="Ville")
        self.ville_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        
        # Telephone
        ctk.CTkLabel(main_frame, text="Téléphone", anchor="w").pack(fill="x", pady=(0, 5))
        self.tel_entry = ctk.CTkEntry(main_frame, placeholder_text="01 23 45 67 89")
        self.tel_entry.pack(fill="x", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(main_frame, text="Email", anchor="w").pack(fill="x", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(main_frame, placeholder_text="email@exemple.com")
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Active checkbox
        self.actif_var = ctk.BooleanVar(value=True)
        actif_check = ctk.CTkCheckBox(main_frame, text="Client actif", variable=self.actif_var)
        actif_check.pack(anchor="w", pady=(0, 15))
        
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
    
    def populate_data(self):
        """Populate form with client data."""
        if self.client:
            self.nom_entry.insert(0, self.client.nom)
            if self.client.raison_sociale:
                self.raison_entry.insert(0, self.client.raison_sociale)
            if self.client.adresse:
                self.adresse_entry.insert(0, self.client.adresse)
            if self.client.code_postal:
                self.cp_entry.insert(0, self.client.code_postal)
            if self.client.ville:
                self.ville_entry.insert(0, self.client.ville)
            if self.client.telephone:
                self.tel_entry.insert(0, self.client.telephone)
            if self.client.email:
                self.email_entry.insert(0, self.client.email)
            self.actif_var.set(self.client.actif)
    
    def save(self):
        """Save the client."""
        try:
            # Validate
            nom = self.nom_entry.get().strip()
            valid, msg = validate_required_field(nom, "Nom")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            raison_sociale = self.raison_entry.get().strip()
            adresse = self.adresse_entry.get().strip()
            code_postal = self.cp_entry.get().strip()
            ville = self.ville_entry.get().strip()
            telephone = self.tel_entry.get().strip()
            email = self.email_entry.get().strip()
            actif = self.actif_var.get()
            
            # Validate email
            if email and not validate_email(email):
                messagebox.showerror("Erreur", "Format d'email invalide")
                return
            
            # Validate telephone
            if telephone and not validate_telephone(telephone):
                messagebox.showerror("Erreur", "Format de téléphone invalide")
                return
            
            # Create or update
            if self.client:
                # Update
                self.client.nom = nom
                self.client.raison_sociale = raison_sociale
                self.client.adresse = adresse
                self.client.code_postal = code_postal
                self.client.ville = ville
                self.client.telephone = telephone
                self.client.email = email
                self.client.actif = actif
                
                success, msg = self.client_manager.update_client(self.client)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
            else:
                # Create
                new_client = Client(
                    nom=nom,
                    raison_sociale=raison_sociale,
                    adresse=adresse,
                    code_postal=code_postal,
                    ville=ville,
                    telephone=telephone,
                    email=email,
                    actif=actif
                )
                
                success, msg, client_id = self.client_manager.create_client(new_client)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")
