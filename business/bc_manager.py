"""
Bon de Commande Manager - Business logic for purchase order management.
"""
from typing import List, Optional
from datetime import datetime
from database.db_manager import DatabaseManager
from database.models import BonCommande
from utils.validators import validate_montant, validate_required_field, generate_numero_bc
from utils.constants import NATURES_BUDGET, TYPES_BC
from utils.formatters import parse_datetime


class BCManager:
    """Manages Bon de Commande (purchase order) business logic."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_all_bcs(self, valide: Optional[bool] = None, nature: Optional[str] = None) -> List[BonCommande]:
        """Get all BCs with optional filters."""
        query = """
            SELECT bc.*, c.nom as client_nom
            FROM bons_commande bc
            JOIN clients c ON bc.client_id = c.id
            WHERE 1=1
        """
        params = []
        
        if valide is not None:
            query += " AND bc.valide = ?"
            params.append(1 if valide else 0)
        
        if nature:
            query += " AND bc.nature = ?"
            params.append(nature)
        
        query += " ORDER BY bc.numero_bc DESC"
        
        rows = self.db.execute_query(query, tuple(params))
        return [self._row_to_bc(row) for row in rows]
    
    def get_bc_by_id(self, bc_id: int) -> Optional[BonCommande]:
        """Get BC by ID."""
        query = "SELECT * FROM bons_commande WHERE id = ?"
        rows = self.db.execute_query(query, (bc_id,))
        if rows:
            return self._row_to_bc(rows[0])
        return None
    
    def generate_next_numero(self) -> str:
        """Generate next BC number."""
        current_year = datetime.now().year
        
        # Get last BC number for current year
        query = """
            SELECT numero_bc FROM bons_commande
            WHERE numero_bc LIKE ?
            ORDER BY numero_bc DESC
            LIMIT 1
        """
        rows = self.db.execute_query(query, (f"BC-{current_year}-%",))
        
        if rows:
            # Extract sequence number and increment
            last_numero = rows[0]['numero_bc']
            sequence = int(last_numero.split('-')[-1]) + 1
        else:
            sequence = 1
        
        return generate_numero_bc(current_year, sequence)
    
    def create_bc(self, bc: BonCommande) -> tuple[bool, str, Optional[int]]:
        """Create new BC."""
        # Validate required fields
        if not bc.client_id:
            return False, "Client requis", None
        
        valid, msg = validate_required_field(bc.nature, "Nature")
        if not valid:
            return False, msg, None
        
        if bc.nature not in NATURES_BUDGET:
            return False, f"Nature invalide. Valeurs acceptées: {', '.join(NATURES_BUDGET)}", None
        
        valid, msg = validate_required_field(bc.type, "Type")
        if not valid:
            return False, msg, None
        
        if bc.type not in TYPES_BC:
            return False, f"Type invalide. Valeurs acceptées: {', '.join(TYPES_BC)}", None
        
        if not validate_montant(bc.montant):
            return False, "Montant invalide", None
        
        if bc.montant <= 0:
            return False, "Le montant doit être supérieur à zéro", None
        
        # Generate numero_bc if not provided
        if not bc.numero_bc:
            bc.numero_bc = self.generate_next_numero()
        
        # Check if numero already exists
        existing = self.db.execute_query(
            "SELECT id FROM bons_commande WHERE numero_bc = ?",
            (bc.numero_bc,)
        )
        if existing:
            return False, f"Un BC avec le numéro '{bc.numero_bc}' existe déjà", None
        
        try:
            query = """
                INSERT INTO bons_commande (numero_bc, client_id, contrat_id, nature, type,
                                          service_demandeur, montant, valide, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """
            bc_id = self.db.execute_update(
                query,
                (bc.numero_bc, bc.client_id, bc.contrat_id, bc.nature, bc.type,
                 bc.service_demandeur, bc.montant, bc.description)
            )
            return True, f"BC {bc.numero_bc} créé avec succès", bc_id
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_bc(self, bc: BonCommande) -> tuple[bool, str]:
        """Update existing BC (only if not validated)."""
        if not bc.id:
            return False, "ID BC requis"
        
        # Check if BC is validated
        existing = self.get_bc_by_id(bc.id)
        if not existing:
            return False, "BC introuvable"
        
        if existing.valide:
            return False, "Impossible de modifier un BC validé"
        
        # Validate fields
        if not bc.client_id:
            return False, "Client requis"
        
        if bc.nature not in NATURES_BUDGET:
            return False, f"Nature invalide. Valeurs acceptées: {', '.join(NATURES_BUDGET)}"
        
        if bc.type not in TYPES_BC:
            return False, f"Type invalide. Valeurs acceptées: {', '.join(TYPES_BC)}"
        
        if not validate_montant(bc.montant):
            return False, "Montant invalide"
        
        if bc.montant <= 0:
            return False, "Le montant doit être supérieur à zéro"
        
        try:
            query = """
                UPDATE bons_commande
                SET client_id = ?, contrat_id = ?, nature = ?, type = ?,
                    service_demandeur = ?, montant = ?, description = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (bc.client_id, bc.contrat_id, bc.nature, bc.type,
                 bc.service_demandeur, bc.montant, bc.description, bc.id)
            )
            return True, "BC mis à jour avec succès"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def delete_bc(self, bc_id: int) -> tuple[bool, str]:
        """Delete BC (only if not validated)."""
        bc = self.get_bc_by_id(bc_id)
        if not bc:
            return False, "BC introuvable"
        
        if bc.valide:
            return False, "Impossible de supprimer un BC validé"
        
        try:
            query = "DELETE FROM bons_commande WHERE id = ?"
            self.db.execute_update(query, (bc_id,))
            return True, "BC supprimé avec succès"
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    def valider_bc(self, bc_id: int, budget_manager) -> tuple[bool, str]:
        """Validate BC and impute to budget via trigger."""
        bc = self.get_bc_by_id(bc_id)
        if not bc:
            return False, "BC introuvable"
        
        if bc.valide:
            return False, "BC déjà validé"
        
        # Check budget availability
        success, msg = budget_manager.check_disponibilite(bc.client_id, bc.nature, bc.montant)
        if not success:
            return False, f"Validation impossible: {msg}"
        
        try:
            # Trigger will handle the budget imputation automatically
            query = "UPDATE bons_commande SET valide = 1 WHERE id = ?"
            self.db.execute_update(query, (bc_id,))
            return True, f"BC {bc.numero_bc} validé avec succès. Budget imputé automatiquement."
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    def get_bc_statistics(self) -> dict:
        """Get BC statistics."""
        current_year = datetime.now().year
        
        query = """
            SELECT 
                nature,
                valide,
                COUNT(*) as nb_bcs,
                SUM(montant) as total_montant
            FROM bons_commande
            WHERE numero_bc LIKE ?
            GROUP BY nature, valide
        """
        rows = self.db.execute_query(query, (f"BC-{current_year}-%",))
        
        stats = {
            'total_bcs': 0,
            'bcs_valides': 0,
            'bcs_en_attente': 0,
            'montant_total': 0,
            'by_nature': {}
        }
        
        for row in rows:
            nature = row['nature']
            valide = bool(row['valide'])
            nb = row['nb_bcs']
            montant = row['total_montant']
            
            stats['total_bcs'] += nb
            stats['montant_total'] += montant
            
            if valide:
                stats['bcs_valides'] += nb
            else:
                stats['bcs_en_attente'] += nb
            
            if nature not in stats['by_nature']:
                stats['by_nature'][nature] = {'valides': 0, 'en_attente': 0, 'montant': 0}
            
            if valide:
                stats['by_nature'][nature]['valides'] += nb
            else:
                stats['by_nature'][nature]['en_attente'] += nb
            
            stats['by_nature'][nature]['montant'] += montant
        
        return stats
    
    def _row_to_bc(self, row) -> BonCommande:
        """Convert database row to BonCommande object."""
        date_validation = None
        if row['date_validation']:
            date_validation = parse_datetime(row['date_validation'])
        
        return BonCommande(
            id=row['id'],
            numero_bc=row['numero_bc'],
            client_id=row['client_id'],
            contrat_id=row['contrat_id'],
            nature=row['nature'],
            type=row['type'],
            service_demandeur=row['service_demandeur'] or "",
            montant=row['montant'],
            valide=bool(row['valide']),
            date_validation=date_validation,
            description=row['description'] or ""
        )
