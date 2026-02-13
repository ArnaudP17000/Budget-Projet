"""
Budget Manager - Business logic for budget management.
"""
from typing import List, Optional
from datetime import datetime
from database.db_manager import DatabaseManager
from database.models import Budget
from utils.validators import validate_montant, validate_annee, validate_required_field
from utils.constants import NATURES_BUDGET


class BudgetManager:
    """Manages budget business logic."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_all_budgets(self, annee: Optional[int] = None, nature: Optional[str] = None) -> List[Budget]:
        """Get all budgets with optional filters."""
        query = """
            SELECT b.*, c.nom as client_nom
            FROM budgets b
            JOIN clients c ON b.client_id = c.id
            WHERE 1=1
        """
        params = []
        
        if annee:
            query += " AND b.annee = ?"
            params.append(annee)
        
        if nature:
            query += " AND b.nature = ?"
            params.append(nature)
        
        query += " ORDER BY b.annee DESC, c.nom"
        
        rows = self.db.execute_query(query, tuple(params))
        return [self._row_to_budget(row) for row in rows]
    
    def get_budget_by_id(self, budget_id: int) -> Optional[Budget]:
        """Get budget by ID."""
        query = "SELECT * FROM budgets WHERE id = ?"
        rows = self.db.execute_query(query, (budget_id,))
        if rows:
            return self._row_to_budget(rows[0])
        return None
    
    def get_budget_by_client_year_nature(self, client_id: int, annee: int, nature: str) -> Optional[Budget]:
        """Get budget for specific client, year, and nature."""
        query = "SELECT * FROM budgets WHERE client_id = ? AND annee = ? AND nature = ?"
        rows = self.db.execute_query(query, (client_id, annee, nature))
        if rows:
            return self._row_to_budget(rows[0])
        return None
    
    def create_budget(self, budget: Budget) -> tuple[bool, str, Optional[int]]:
        """Create new budget."""
        # Validate required fields
        if not budget.client_id:
            return False, "Client requis", None
        
        valid, msg = validate_required_field(str(budget.annee), "Année")
        if not valid:
            return False, msg, None
        
        if not validate_annee(budget.annee):
            return False, "Année invalide", None
        
        valid, msg = validate_required_field(budget.nature, "Nature")
        if not valid:
            return False, msg, None
        
        if budget.nature not in NATURES_BUDGET:
            return False, f"Nature invalide. Valeurs acceptées: {', '.join(NATURES_BUDGET)}", None
        
        if not validate_montant(budget.montant_initial):
            return False, "Montant initial invalide", None
        
        # Check if budget already exists for this client/year/nature
        existing = self.get_budget_by_client_year_nature(budget.client_id, budget.annee, budget.nature)
        if existing:
            return False, "Un budget existe déjà pour ce client, cette année et cette nature", None
        
        try:
            query = """
                INSERT INTO budgets (client_id, annee, nature, montant_initial, montant_consomme, service_demandeur)
                VALUES (?, ?, ?, ?, 0, ?)
            """
            budget_id = self.db.execute_update(
                query,
                (budget.client_id, budget.annee, budget.nature, budget.montant_initial,
                 budget.service_demandeur)
            )
            return True, "Budget créé avec succès", budget_id
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_budget(self, budget: Budget) -> tuple[bool, str]:
        """Update existing budget."""
        if not budget.id:
            return False, "ID budget requis"
        
        # Validate fields
        if not validate_annee(budget.annee):
            return False, "Année invalide"
        
        if budget.nature not in NATURES_BUDGET:
            return False, f"Nature invalide. Valeurs acceptées: {', '.join(NATURES_BUDGET)}"
        
        if not validate_montant(budget.montant_initial):
            return False, "Montant initial invalide"
        
        try:
            # Recalculate montant_disponible
            montant_disponible = budget.montant_initial - budget.montant_consomme
            
            query = """
                UPDATE budgets
                SET annee = ?, nature = ?, montant_initial = ?, 
                    montant_disponible = ?, service_demandeur = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (budget.annee, budget.nature, budget.montant_initial,
                 montant_disponible, budget.service_demandeur, budget.id)
            )
            return True, "Budget mis à jour avec succès"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def delete_budget(self, budget_id: int) -> tuple[bool, str]:
        """Delete budget if no BC are associated."""
        # Check if there are validated BCs using this budget
        query = """
            SELECT COUNT(*) as count FROM bons_commande b
            JOIN budgets bu ON b.client_id = bu.client_id AND b.nature = bu.nature
            WHERE bu.id = ? AND b.valide = 1
        """
        result = self.db.execute_query(query, (budget_id,))
        if result and result[0]['count'] > 0:
            return False, "Impossible de supprimer: des bons de commande sont associés à ce budget"
        
        try:
            query = "DELETE FROM budgets WHERE id = ?"
            self.db.execute_update(query, (budget_id,))
            return True, "Budget supprimé avec succès"
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    def report_budget_to_next_year(self, budget_id: int) -> tuple[bool, str]:
        """Report budget to next year with remaining amount."""
        budget = self.get_budget_by_id(budget_id)
        if not budget:
            return False, "Budget introuvable"
        
        if budget.montant_disponible <= 0:
            return False, "Aucun montant disponible à reporter"
        
        next_year = budget.annee + 1
        
        # Check if budget already exists for next year
        existing = self.get_budget_by_client_year_nature(budget.client_id, next_year, budget.nature)
        if existing:
            return False, f"Un budget existe déjà pour l'année {next_year}"
        
        # Create new budget for next year
        new_budget = Budget(
            client_id=budget.client_id,
            annee=next_year,
            nature=budget.nature,
            montant_initial=budget.montant_disponible,
            montant_consomme=0,
            montant_disponible=budget.montant_disponible,
            service_demandeur=budget.service_demandeur
        )
        
        success, msg, _ = self.create_budget(new_budget)
        if success:
            return True, f"Budget reporté avec succès sur l'année {next_year}"
        return False, f"Erreur lors du report: {msg}"
    
    def check_disponibilite(self, client_id: int, nature: str, montant: float) -> tuple[bool, str]:
        """Check if budget is available for a given amount."""
        current_year = datetime.now().year
        budget = self.get_budget_by_client_year_nature(client_id, current_year, nature)
        
        if not budget:
            return False, f"Aucun budget {nature} trouvé pour l'année {current_year}"
        
        if budget.montant_disponible < montant:
            return False, f"Budget insuffisant. Disponible: {budget.montant_disponible:.2f} €, Demandé: {montant:.2f} €"
        
        return True, "Budget disponible"
    
    def get_budget_statistics(self, annee: Optional[int] = None) -> dict:
        """Get budget statistics."""
        if not annee:
            annee = datetime.now().year
        
        query = """
            SELECT 
                nature,
                COUNT(*) as nb_budgets,
                SUM(montant_initial) as total_initial,
                SUM(montant_consomme) as total_consomme,
                SUM(montant_disponible) as total_disponible
            FROM budgets
            WHERE annee = ?
            GROUP BY nature
        """
        rows = self.db.execute_query(query, (annee,))
        
        stats = {}
        for row in rows:
            stats[row['nature']] = {
                'nb_budgets': row['nb_budgets'],
                'total_initial': row['total_initial'],
                'total_consomme': row['total_consomme'],
                'total_disponible': row['total_disponible']
            }
        
        return stats
    
    def _row_to_budget(self, row) -> Budget:
        """Convert database row to Budget object."""
        return Budget(
            id=row['id'],
            client_id=row['client_id'],
            annee=row['annee'],
            nature=row['nature'],
            montant_initial=row['montant_initial'],
            montant_consomme=row['montant_consomme'],
            montant_disponible=row['montant_disponible'],
            service_demandeur=row['service_demandeur'] or ""
        )
