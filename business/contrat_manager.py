"""
Contrat Manager - Business logic for contract management.
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager
from database.models import Contrat
from utils.validators import validate_montant, validate_date_range, validate_required_field
from utils.constants import STATUTS_CONTRAT
from utils.formatters import parse_date


class ContratManager:
    """Manages contract business logic."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_all_contrats(self, statut: Optional[str] = None, alerte_only: bool = False) -> List[Contrat]:
        """Get all contracts with optional filters."""
        query = """
            SELECT c.*, cl.nom as client_nom, co.nom as contact_nom, co.prenom as contact_prenom
            FROM contrats c
            LEFT JOIN clients cl ON c.client_id = cl.id
            LEFT JOIN contacts co ON c.contact_id = co.id
            WHERE 1=1
        """
        params = []
        
        if statut:
            query += " AND c.statut = ?"
            params.append(statut)
        
        if alerte_only:
            query += " AND c.alerte_6_mois = 1"
        
        query += " ORDER BY c.date_fin ASC"
        
        rows = self.db.execute_query(query, tuple(params))
        return [self._row_to_contrat(row) for row in rows]
    
    def get_contrat_by_id(self, contrat_id: int) -> Optional[Contrat]:
        """Get contract by ID."""
        query = "SELECT * FROM contrats WHERE id = ?"
        rows = self.db.execute_query(query, (contrat_id,))
        if rows:
            return self._row_to_contrat(rows[0])
        return None
    
    def create_contrat(self, contrat: Contrat) -> tuple[bool, str, Optional[int]]:
        """Create new contract."""
        # Validate required fields
        valid, msg = validate_required_field(contrat.numero_contrat, "Numéro de contrat")
        if not valid:
            return False, msg, None
        
        if not contrat.client_id:
            return False, "Client requis", None
        
        if not validate_montant(contrat.montant):
            return False, "Montant invalide", None
        
        if not validate_date_range(contrat.date_debut, contrat.date_fin):
            return False, "La date de fin doit être postérieure à la date de début", None
        
        if contrat.statut not in STATUTS_CONTRAT:
            return False, f"Statut invalide. Valeurs acceptées: {', '.join(STATUTS_CONTRAT)}", None
        
        # Check if contract number already exists
        existing = self.db.execute_query(
            "SELECT id FROM contrats WHERE numero_contrat = ?",
            (contrat.numero_contrat,)
        )
        if existing:
            return False, f"Un contrat avec le numéro '{contrat.numero_contrat}' existe déjà", None
        
        # Check if alert needed (< 6 months to expiration)
        alerte_6_mois = self._check_alert(contrat.date_fin)
        
        try:
            query = """
                INSERT INTO contrats (numero_contrat, client_id, contact_id, date_debut, date_fin,
                                    montant, description, statut, alerte_6_mois)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            contrat_id = self.db.execute_update(
                query,
                (contrat.numero_contrat, contrat.client_id, contrat.contact_id,
                 contrat.date_debut, contrat.date_fin, contrat.montant,
                 contrat.description, contrat.statut, 1 if alerte_6_mois else 0)
            )
            return True, "Contrat créé avec succès", contrat_id
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_contrat(self, contrat: Contrat) -> tuple[bool, str]:
        """Update existing contract."""
        if not contrat.id:
            return False, "ID contrat requis"
        
        # Validate required fields
        valid, msg = validate_required_field(contrat.numero_contrat, "Numéro de contrat")
        if not valid:
            return False, msg
        
        if not contrat.client_id:
            return False, "Client requis"
        
        if not validate_montant(contrat.montant):
            return False, "Montant invalide"
        
        if not validate_date_range(contrat.date_debut, contrat.date_fin):
            return False, "La date de fin doit être postérieure à la date de début"
        
        if contrat.statut not in STATUTS_CONTRAT:
            return False, f"Statut invalide. Valeurs acceptées: {', '.join(STATUTS_CONTRAT)}"
        
        # Check if contract number already exists for another contract
        existing = self.db.execute_query(
            "SELECT id FROM contrats WHERE numero_contrat = ? AND id != ?",
            (contrat.numero_contrat, contrat.id)
        )
        if existing:
            return False, f"Un autre contrat avec le numéro '{contrat.numero_contrat}' existe déjà"
        
        # Check if alert needed
        alerte_6_mois = self._check_alert(contrat.date_fin)
        
        try:
            query = """
                UPDATE contrats
                SET numero_contrat = ?, client_id = ?, contact_id = ?, date_debut = ?,
                    date_fin = ?, montant = ?, description = ?, statut = ?, alerte_6_mois = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (contrat.numero_contrat, contrat.client_id, contrat.contact_id,
                 contrat.date_debut, contrat.date_fin, contrat.montant,
                 contrat.description, contrat.statut, 1 if alerte_6_mois else 0,
                 contrat.id)
            )
            return True, "Contrat mis à jour avec succès"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def delete_contrat(self, contrat_id: int) -> tuple[bool, str]:
        """Delete contract."""
        # Check if there are BCs associated
        query = "SELECT COUNT(*) as count FROM bons_commande WHERE contrat_id = ?"
        result = self.db.execute_query(query, (contrat_id,))
        if result and result[0]['count'] > 0:
            return False, "Impossible de supprimer: des bons de commande sont associés à ce contrat"
        
        try:
            query = "DELETE FROM contrats WHERE id = ?"
            self.db.execute_update(query, (contrat_id,))
            return True, "Contrat supprimé avec succès"
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    def update_alerts(self) -> int:
        """Update alerts for all contracts. Returns number of alerts set."""
        query = """
            SELECT id, date_fin
            FROM contrats
            WHERE statut = 'Actif' AND date_fin IS NOT NULL
        """
        rows = self.db.execute_query(query)
        
        alerts_set = 0
        for row in rows:
            date_fin = parse_date(row['date_fin']) if isinstance(row['date_fin'], str) else row['date_fin']
            if date_fin:
                alerte = self._check_alert(date_fin)
                update_query = "UPDATE contrats SET alerte_6_mois = ? WHERE id = ?"
                self.db.execute_update(update_query, (1 if alerte else 0, row['id']))
                if alerte:
                    alerts_set += 1
        
        return alerts_set
    
    def get_contrats_with_alerts(self) -> List[Contrat]:
        """Get contracts with active alerts."""
        return self.get_all_contrats(alerte_only=True)
    
    def _check_alert(self, date_fin: Optional[date]) -> bool:
        """Check if contract needs alert (< 6 months to expiration)."""
        if not date_fin:
            return False
        
        # Convert string to date if needed
        if isinstance(date_fin, str):
            date_fin = parse_date(date_fin)
        
        if not date_fin:
            return False
        
        today = date.today()
        six_months_from_now = today + timedelta(days=180)
        
        return today <= date_fin <= six_months_from_now
    
    def _row_to_contrat(self, row) -> Contrat:
        """Convert database row to Contrat object."""
        date_debut = parse_date(row['date_debut']) if row['date_debut'] else None
        date_fin = parse_date(row['date_fin']) if row['date_fin'] else None
        
        return Contrat(
            id=row['id'],
            numero_contrat=row['numero_contrat'],
            client_id=row['client_id'],
            contact_id=row['contact_id'],
            date_debut=date_debut,
            date_fin=date_fin,
            montant=row['montant'],
            description=row['description'] or "",
            statut=row['statut'],
            alerte_6_mois=bool(row['alerte_6_mois'])
        )
