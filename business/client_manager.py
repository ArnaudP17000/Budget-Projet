"""
Client Manager - Business logic for client management.
"""
from typing import List, Optional
from database.db_manager import DatabaseManager
from database.models import Client
from utils.validators import validate_email, validate_telephone, validate_required_field


class ClientManager:
    """Manages client business logic."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_all_clients(self, include_inactive: bool = False) -> List[Client]:
        """Get all clients."""
        if include_inactive:
            query = "SELECT * FROM clients ORDER BY nom"
        else:
            query = "SELECT * FROM clients WHERE actif = 1 ORDER BY nom"
        
        rows = self.db.execute_query(query)
        return [self._row_to_client(row) for row in rows]
    
    def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID."""
        query = "SELECT * FROM clients WHERE id = ?"
        rows = self.db.execute_query(query, (client_id,))
        if rows:
            return self._row_to_client(rows[0])
        return None
    
    def create_client(self, client: Client) -> tuple[bool, str, Optional[int]]:
        """Create new client."""
        # Validate required fields
        valid, msg = validate_required_field(client.nom, "Nom")
        if not valid:
            return False, msg, None
        
        # Validate email
        if client.email and not validate_email(client.email):
            return False, "Format d'email invalide", None
        
        # Validate telephone
        if client.telephone and not validate_telephone(client.telephone):
            return False, "Format de téléphone invalide", None
        
        # Check if name already exists
        existing = self.db.execute_query("SELECT id FROM clients WHERE nom = ?", (client.nom,))
        if existing:
            return False, f"Un client avec le nom '{client.nom}' existe déjà", None
        
        try:
            query = """
                INSERT INTO clients (nom, raison_sociale, adresse, code_postal, ville, email, telephone, actif)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            client_id = self.db.execute_update(
                query,
                (client.nom, client.raison_sociale, client.adresse, client.code_postal,
                 client.ville, client.email, client.telephone, 1 if client.actif else 0)
            )
            return True, "Client créé avec succès", client_id
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_client(self, client: Client) -> tuple[bool, str]:
        """Update existing client."""
        if not client.id:
            return False, "ID client requis"
        
        # Validate required fields
        valid, msg = validate_required_field(client.nom, "Nom")
        if not valid:
            return False, msg
        
        # Validate email
        if client.email and not validate_email(client.email):
            return False, "Format d'email invalide"
        
        # Validate telephone
        if client.telephone and not validate_telephone(client.telephone):
            return False, "Format de téléphone invalide"
        
        # Check if name already exists for another client
        existing = self.db.execute_query(
            "SELECT id FROM clients WHERE nom = ? AND id != ?",
            (client.nom, client.id)
        )
        if existing:
            return False, f"Un autre client avec le nom '{client.nom}' existe déjà"
        
        try:
            query = """
                UPDATE clients
                SET nom = ?, raison_sociale = ?, adresse = ?, code_postal = ?,
                    ville = ?, email = ?, telephone = ?, actif = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (client.nom, client.raison_sociale, client.adresse, client.code_postal,
                 client.ville, client.email, client.telephone, 1 if client.actif else 0,
                 client.id)
            )
            return True, "Client mis à jour avec succès"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def deactivate_client(self, client_id: int) -> tuple[bool, str]:
        """Deactivate client (soft delete)."""
        try:
            query = "UPDATE clients SET actif = 0 WHERE id = ?"
            self.db.execute_update(query, (client_id,))
            return True, "Client désactivé avec succès"
        except Exception as e:
            return False, f"Erreur lors de la désactivation: {str(e)}"
    
    def activate_client(self, client_id: int) -> tuple[bool, str]:
        """Activate client."""
        try:
            query = "UPDATE clients SET actif = 1 WHERE id = ?"
            self.db.execute_update(query, (client_id,))
            return True, "Client activé avec succès"
        except Exception as e:
            return False, f"Erreur lors de l'activation: {str(e)}"
    
    def _row_to_client(self, row) -> Client:
        """Convert database row to Client object."""
        return Client(
            id=row['id'],
            nom=row['nom'],
            raison_sociale=row['raison_sociale'] or "",
            adresse=row['adresse'] or "",
            code_postal=row['code_postal'] or "",
            ville=row['ville'] or "",
            email=row['email'] or "",
            telephone=row['telephone'] or "",
            actif=bool(row['actif'])
        )
