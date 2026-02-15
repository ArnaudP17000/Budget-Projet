"""
Alert Manager - Business logic for alert management.
"""
from typing import List, Dict
from datetime import datetime
from database.db_manager import DatabaseManager


class AlertManager:
    """Manages alerts for contracts and budgets."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_all_alerts(self) -> Dict[str, List]:
        """Get all alerts (contracts and budgets)."""
        alerts = {
            'contrats': self.get_contrat_alerts(),
            'budgets': self.get_budget_alerts(),
            'bcs_en_attente': self.get_bc_en_attente()
        }
        return alerts
    
    def get_contrat_alerts(self) -> List[Dict]:
        """Get contract alerts (expiring < 6 months)."""
        query = """
            SELECT c.*, cl.nom as client_nom
            FROM contrats c
            JOIN clients cl ON c.client_id = cl.id
            WHERE c.alerte_6_mois = 1 AND c.statut = 'Actif'
            ORDER BY c.date_fin
        """
        rows = self.db.execute_query(query)
        
        alerts = []
        for row in rows:
            alerts.append({
                'id': row['id'],
                'numero_contrat': row['numero_contrat'],
                'client_nom': row['client_nom'],
                'date_fin': row['date_fin'],
                'montant': row['montant'],
                'description': row['description'] or "",
                'type': 'contrat'
            })
        
        return alerts
        
    def get_contrats_expiring(self, days: int = 180) -> List[Dict]:
        """Get contracts expiring within specified days."""
        query = """
            SELECT c.*, cl.nom as client_nom
            FROM contrats c
            JOIN clients cl ON c.client_id = cl.id
            WHERE c.statut = 'Actif' 
            AND date(c.date_fin) <= date('now', '+' || ? || ' days')
            ORDER BY c.date_fin
        """
        rows = self.db.execute_query(query, (days,))

        contracts = []
        for row in rows:
            contracts.append({
                'id': row['id'],
                'numero_contrat': row['numero_contrat'],
                'client_nom': row['client_nom'],
                'date_fin': row['date_fin'],
                'montant': row['montant'],
                'description': row['description'] or "",
                'type': 'contrat'
            })

        return contracts
    
    def get_budget_alerts(self) -> List[Dict]:
        """Get budget alerts (low available amount)."""
        current_year = datetime.now().year
        
        query = """
            SELECT b.*, c.nom as client_nom
            FROM budgets b
            JOIN clients c ON b.client_id = c.id
            WHERE b.annee = ? AND b.montant_disponible < (b.montant_initial * 0.1)
            ORDER BY b.montant_disponible
        """
        rows = self.db.execute_query(query, (current_year,))
        
        alerts = []
        for row in rows:
            pourcentage = (row['montant_disponible'] / row['montant_initial'] * 100) if row['montant_initial'] > 0 else 0
            alerts.append({
                'id': row['id'],
                'client_nom': row['client_nom'],
                'nature': row['nature'],
                'montant_initial': row['montant_initial'],
                'montant_disponible': row['montant_disponible'],
                'pourcentage_disponible': pourcentage,
                'type': 'budget'
            })
        
        return alerts
    
    def get_bc_en_attente(self) -> List[Dict]:
        """Get BCs waiting for validation."""
        query = """
            SELECT bc.*, c.nom as client_nom
            FROM bons_commande bc
            JOIN clients c ON bc.client_id = c.id
            WHERE bc.valide = 0
            ORDER BY bc.numero_bc DESC
        """
        rows = self.db.execute_query(query)
        
        bcs = []
        for row in rows:
            bcs.append({
                'id': row['id'],
                'numero_bc': row['numero_bc'],
                'client_nom': row['client_nom'],
                'nature': row['nature'],
                'type': row['type'],
                'montant': row['montant'],
                'service_demandeur': row['service_demandeur'] or "",
                'type': 'bc'
            })
        
        return bcs
    
    def get_alert_count(self) -> Dict[str, int]:
        """Get count of each type of alert."""
        alerts = self.get_all_alerts()
        return {
            'contrats': len(alerts['contrats']),
            'budgets': len(alerts['budgets']),
            'bcs_en_attente': len(alerts['bcs_en_attente']),
            'total': len(alerts['contrats']) + len(alerts['budgets']) + len(alerts['bcs_en_attente'])
        }
