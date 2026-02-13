"""
Contact Manager - Business logic for contact management.
"""
from typing import List, Optional
from database.db_manager import DatabaseManager
from database.models import Contact
from utils.validators import validate_email, validate_telephone, validate_required_field


class ContactManager:
    """Manages contact business logic."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_all_contacts(self, client_id: Optional[int] = None) -> List[Contact]:
        """Get all contacts, optionally filtered by client."""
        if client_id:
            query = "SELECT * FROM contacts WHERE client_id = ? ORDER BY nom, prenom"
            rows = self.db.execute_query(query, (client_id,))
        else:
            query = "SELECT * FROM contacts ORDER BY nom, prenom"
            rows = self.db.execute_query(query)
        
        return [self._row_to_contact(row) for row in rows]
    
    def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        """Get contact by ID."""
        query = "SELECT * FROM contacts WHERE id = ?"
        rows = self.db.execute_query(query, (contact_id,))
        if rows:
            return self._row_to_contact(rows[0])
        return None
    
    def create_contact(self, contact: Contact) -> tuple[bool, str, Optional[int]]:
        """Create new contact."""
        # Validate required fields
        valid, msg = validate_required_field(contact.nom, "Nom")
        if not valid:
            return False, msg, None
        
        valid, msg = validate_required_field(contact.prenom, "Prénom")
        if not valid:
            return False, msg, None
        
        # Validate email
        if contact.email and not validate_email(contact.email):
            return False, "Format d'email invalide", None
        
        # Validate telephone
        if contact.telephone and not validate_telephone(contact.telephone):
            return False, "Format de téléphone invalide", None
        
        try:
            query = """
                INSERT INTO contacts (client_id, nom, prenom, fonction, telephone, email, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            contact_id = self.db.execute_update(
                query,
                (contact.client_id, contact.nom, contact.prenom, contact.fonction,
                 contact.telephone, contact.email, contact.notes)
            )
            return True, "Contact créé avec succès", contact_id
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_contact(self, contact: Contact) -> tuple[bool, str]:
        """Update existing contact."""
        if not contact.id:
            return False, "ID contact requis"
        
        # Validate required fields
        valid, msg = validate_required_field(contact.nom, "Nom")
        if not valid:
            return False, msg
        
        valid, msg = validate_required_field(contact.prenom, "Prénom")
        if not valid:
            return False, msg
        
        # Validate email
        if contact.email and not validate_email(contact.email):
            return False, "Format d'email invalide"
        
        # Validate telephone
        if contact.telephone and not validate_telephone(contact.telephone):
            return False, "Format de téléphone invalide"
        
        try:
            query = """
                UPDATE contacts
                SET client_id = ?, nom = ?, prenom = ?, fonction = ?,
                    telephone = ?, email = ?, notes = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (contact.client_id, contact.nom, contact.prenom, contact.fonction,
                 contact.telephone, contact.email, contact.notes, contact.id)
            )
            return True, "Contact mis à jour avec succès"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def delete_contact(self, contact_id: int) -> tuple[bool, str]:
        """Delete contact."""
        try:
            query = "DELETE FROM contacts WHERE id = ?"
            self.db.execute_update(query, (contact_id,))
            return True, "Contact supprimé avec succès"
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    def _row_to_contact(self, row) -> Contact:
        """Convert database row to Contact object."""
        return Contact(
            id=row['id'],
            client_id=row['client_id'],
            nom=row['nom'],
            prenom=row['prenom'],
            fonction=row['fonction'] or "",
            telephone=row['telephone'] or "",
            email=row['email'] or "",
            notes=row['notes'] or ""
        )
