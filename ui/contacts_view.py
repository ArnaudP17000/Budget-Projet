"""
Contacts View - Gestion complète des contacts.
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from database.db_manager import DatabaseManager
from business.contact_manager import ContactManager
from business.client_manager import ClientManager
from database.models import Contact
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD
)
from utils.validators import validate_email, validate_telephone, validate_required_field


class ContactsView(ctk.CTkFrame):
    """Contacts management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize contacts view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.contact_manager = ContactManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        
        self.create_widgets()
        self.load_contacts()
    
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
            text="👥 Gestion des Contacts",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        new_btn = ctk.CTkButton(
            header_frame,
            text="➕ Nouveau Contact",
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
        
        ctk.CTkLabel(filter_frame, text="Client:").pack(side="left", padx=(0, 5))
        
        # Load clients for filter
        clients = self.client_manager.get_all_clients()
        client_names = ["Tous"] + [c.nom for c in clients if c.actif]
        self.client_filter = ctk.CTkComboBox(
            filter_frame,
            values=client_names,
            width=200,
            command=lambda _: self.load_contacts()
        )
        self.client_filter.set("Tous")
        self.client_filter.pack(side="left", padx=5)
        
        # Store client mapping
        self.client_filter.client_map = {c.nom: c.id for c in clients if c.actif}
        
        # Scrollable frame for contacts
        self.contacts_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.contacts_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.contacts_scroll.grid_columnconfigure(0, weight=1)
    
    def load_contacts(self):
        """Load and display contacts."""
        # Clear existing
        for widget in self.contacts_scroll.winfo_children():
            widget.destroy()
        
        # Get filter
        client_filter = self.client_filter.get()
        client_id = None
        if client_filter != "Tous" and client_filter in self.client_filter.client_map:
            client_id = self.client_filter.client_map[client_filter]
        
        # Load contacts
        contacts = self.contact_manager.get_all_contacts(client_id=client_id)
        
        if not contacts:
            no_data_label = ctk.CTkLabel(
                self.contacts_scroll,
                text="Aucun contact trouvé",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            )
            no_data_label.pack(pady=50)
            return
        
        # Display contacts
        for contact in contacts:
            self.create_contact_card(contact)
    
    def create_contact_card(self, contact: Contact):
        """Create a contact card."""
        card = ctk.CTkFrame(self.contacts_scroll, fg_color=COLOR_BG_CARD, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=15)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Contact name
        nom_label = ctk.CTkLabel(
            info_frame,
            text=f"👤 {contact.prenom} {contact.nom}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        nom_label.grid(row=0, column=0, sticky="w", columnspan=2)
        
        # Get client name
        if contact.client_id:
            client = self.client_manager.get_client_by_id(contact.client_id)
            client_name = client.nom if client else "Client inconnu"
            
            client_label = ctk.CTkLabel(
                info_frame,
                text=f"🏢 {client_name}",
                font=ctk.CTkFont(size=12),
                text_color="gray70"
            )
            client_label.grid(row=1, column=0, sticky="w", columnspan=2, pady=(2, 0))
        
        # Function
        if contact.fonction:
            fonction_label = ctk.CTkLabel(
                info_frame,
                text=f"💼 {contact.fonction}",
                font=ctk.CTkFont(size=12),
                text_color=COLOR_PRIMARY
            )
            fonction_label.grid(row=2, column=0, sticky="w", columnspan=2, pady=(5, 0))
        
        # Details frame
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        details_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Contact info
        contact_info_left = []
        contact_info_right = []
        
        if contact.telephone:
            contact_info_left.append(f"📞 {contact.telephone}")
        
        if contact.email:
            contact_info_right.append(f"✉️ {contact.email}")
        
        if contact_info_left:
            ctk.CTkLabel(
                details_frame,
                text="\n".join(contact_info_left),
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).grid(row=0, column=0, sticky="w")
        
        if contact_info_right:
            ctk.CTkLabel(
                details_frame,
                text="\n".join(contact_info_right),
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).grid(row=0, column=1, sticky="w", padx=(20, 0))
        
        # Notes
        if contact.notes:
            notes_label = ctk.CTkLabel(
                info_frame,
                text=f"📝 {contact.notes[:150]}{'...' if len(contact.notes) > 150 else ''}",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            )
            notes_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Modifier",
            command=lambda c=contact: self.show_edit_dialog(c),
            width=100,
            height=28,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        edit_btn.pack(side="right", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Supprimer",
            command=lambda c=contact: self.delete_contact(c),
            width=100,
            height=28,
            fg_color=COLOR_DANGER,
            hover_color="#cc0000"
        )
        delete_btn.pack(side="right", padx=5)
    
    def show_create_dialog(self):
        """Show dialog to create a new contact."""
        dialog = ContactDialog(self, self.db_manager, title="Créer un Contact")
        dialog.wait_window()
        if dialog.result:
            self.load_contacts()
    
    def show_edit_dialog(self, contact: Contact):
        """Show dialog to edit a contact."""
        dialog = ContactDialog(self, self.db_manager, contact=contact, title="Modifier le Contact")
        dialog.wait_window()
        if dialog.result:
            self.load_contacts()
    
    def delete_contact(self, contact: Contact):
        """Delete a contact."""
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce contact?\n\n"
            f"Nom: {contact.prenom} {contact.nom}"
        ):
            success, msg = self.contact_manager.delete_contact(contact.id)
            if success:
                messagebox.showinfo("Succès", msg)
                self.load_contacts()
            else:
                messagebox.showerror("Erreur", msg)


class ContactDialog(ctk.CTkToplevel):
    """Dialog for creating/editing contacts."""
    
    def __init__(self, parent, db_manager: DatabaseManager, contact: Optional[Contact] = None, title: str = "Contact"):
        super().__init__(parent)
        self.db_manager = db_manager
        self.contact_manager = ContactManager(db_manager)
        self.client_manager = ClientManager(db_manager)
        self.contact = contact
        self.result = None
        
        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if contact:
            self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Client (optional)
        ctk.CTkLabel(main_frame, text="Client", anchor="w").pack(fill="x", pady=(0, 5))
        clients = self.client_manager.get_all_clients()
        client_names = ["Aucun"] + [c.nom for c in clients if c.actif]
        self.client_combo = ctk.CTkComboBox(main_frame, values=client_names)
        self.client_combo.set("Aucun")
        self.client_combo.pack(fill="x", pady=(0, 15))
        self.client_combo.client_map = {c.nom: c.id for c in clients if c.actif}
        
        # Nom
        ctk.CTkLabel(main_frame, text="Nom *", anchor="w").pack(fill="x", pady=(0, 5))
        self.nom_entry = ctk.CTkEntry(main_frame, placeholder_text="Nom de famille")
        self.nom_entry.pack(fill="x", pady=(0, 15))
        
        # Prenom
        ctk.CTkLabel(main_frame, text="Prénom *", anchor="w").pack(fill="x", pady=(0, 5))
        self.prenom_entry = ctk.CTkEntry(main_frame, placeholder_text="Prénom")
        self.prenom_entry.pack(fill="x", pady=(0, 15))
        
        # Fonction
        ctk.CTkLabel(main_frame, text="Fonction", anchor="w").pack(fill="x", pady=(0, 5))
        self.fonction_entry = ctk.CTkEntry(main_frame, placeholder_text="Poste/Fonction")
        self.fonction_entry.pack(fill="x", pady=(0, 15))
        
        # Telephone
        ctk.CTkLabel(main_frame, text="Téléphone", anchor="w").pack(fill="x", pady=(0, 5))
        self.tel_entry = ctk.CTkEntry(main_frame, placeholder_text="01 23 45 67 89")
        self.tel_entry.pack(fill="x", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(main_frame, text="Email", anchor="w").pack(fill="x", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(main_frame, placeholder_text="email@exemple.com")
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Notes
        ctk.CTkLabel(main_frame, text="Notes", anchor="w").pack(fill="x", pady=(0, 5))
        self.notes_text = ctk.CTkTextbox(main_frame, height=100)
        self.notes_text.pack(fill="x", pady=(0, 15))
        
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
        """Populate form with contact data."""
        if self.contact:
            # Set client
            if self.contact.client_id:
                client = self.client_manager.get_client_by_id(self.contact.client_id)
                if client and client.nom in self.client_combo.client_map:
                    self.client_combo.set(client.nom)
            
            self.nom_entry.insert(0, self.contact.nom)
            self.prenom_entry.insert(0, self.contact.prenom)
            
            if self.contact.fonction:
                self.fonction_entry.insert(0, self.contact.fonction)
            if self.contact.telephone:
                self.tel_entry.insert(0, self.contact.telephone)
            if self.contact.email:
                self.email_entry.insert(0, self.contact.email)
            if self.contact.notes:
                self.notes_text.insert("1.0", self.contact.notes)
    
    def save(self):
        """Save the contact."""
        try:
            # Get client ID
            client_id = None
            client_nom = self.client_combo.get()
            if client_nom != "Aucun" and client_nom in self.client_combo.client_map:
                client_id = self.client_combo.client_map[client_nom]
            
            # Validate
            nom = self.nom_entry.get().strip()
            valid, msg = validate_required_field(nom, "Nom")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            prenom = self.prenom_entry.get().strip()
            valid, msg = validate_required_field(prenom, "Prénom")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            fonction = self.fonction_entry.get().strip()
            telephone = self.tel_entry.get().strip()
            email = self.email_entry.get().strip()
            notes = self.notes_text.get("1.0", "end-1c").strip()
            
            # Validate email
            if email and not validate_email(email):
                messagebox.showerror("Erreur", "Format d'email invalide")
                return
            
            # Validate telephone
            if telephone and not validate_telephone(telephone):
                messagebox.showerror("Erreur", "Format de téléphone invalide")
                return
            
            # Create or update
            if self.contact:
                # Update
                self.contact.client_id = client_id
                self.contact.nom = nom
                self.contact.prenom = prenom
                self.contact.fonction = fonction
                self.contact.telephone = telephone
                self.contact.email = email
                self.contact.notes = notes
                
                success, msg = self.contact_manager.update_contact(self.contact)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
            else:
                # Create
                new_contact = Contact(
                    client_id=client_id,
                    nom=nom,
                    prenom=prenom,
                    fonction=fonction,
                    telephone=telephone,
                    email=email,
                    notes=notes
                )
                
                success, msg, contact_id = self.contact_manager.create_contact(new_contact)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")
