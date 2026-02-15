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
        """Create new budget.
        
        Args:
            budget: Budget object to create
            
        Returns:
            Tuple of (success, message, budget_id)
        """
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
                VALUES (?, ?, ?, ?, ?, ?)
            """
            budget_id = self.db.execute_update(
                query,
                (budget.client_id, budget.annee, budget.nature, budget.montant_initial, 
                 budget.montant_consomme or 0.0, budget.service_demandeur or "")
            )
            return True, "Budget créé avec succès", budget_id
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_budget(self, budget: Budget) -> tuple[bool, str]:
        """Update existing budget."""
        if not budget.id:
            return False, "ID budget requis"
        
        # Validate required fields
        if not budget.client_id:
            return False, "Client requis"
        
        valid, msg = validate_required_field(str(budget.annee), "Année")
        if not valid:
            return False, msg
        
        if not validate_annee(budget.annee):
            return False, "Année invalide"
        
        valid, msg = validate_required_field(budget.nature, "Nature")
        if not valid:
            return False, msg
        
        if budget.nature not in NATURES_BUDGET:
            return False, f"Nature invalide. Valeurs acceptées: {', '.join(NATURES_BUDGET)}"
        
        if not validate_montant(budget.montant_initial):
            return False, "Montant initial invalide"
        
        try:
            query = """
                UPDATE budgets
                SET client_id = ?, annee = ?, nature = ?, 
                    montant_initial = ?, service_demandeur = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (budget.client_id, budget.annee, budget.nature, 
                 budget.montant_initial, budget.service_demandeur or "", budget.id)
            )
            return True, "Budget modifié avec succès"
        except Exception as e:
            return False, f"Erreur lors de la modification: {str(e)}"
    
    def delete_budget(self, budget_id: int) -> tuple[bool, str]:
        """Delete budget."""
        try:
            query = "DELETE FROM budgets WHERE id = ?"
            self.db.execute_update(query, (budget_id,))
            return True, "Budget supprimé avec succès"
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    def report_budgets(self, from_year: int, to_year: int) -> tuple[bool, str]:
        """Report budgets from one year to another."""
        try:
            # Get budgets from source year
            budgets = self.get_all_budgets(annee=from_year)
            
            if not budgets:
                return False, f"Aucun budget trouvé pour l'année {from_year}"
            
            reported_count = 0
            for budget in budgets:
                # Check if budget already exists for target year
                existing = self.get_budget_by_client_year_nature(
                    budget.client_id, to_year, budget.nature
                )
                
                if not existing:
                    # Create new budget for target year
                    new_budget = Budget(
                        client_id=budget.client_id,
                        annee=to_year,
                        nature=budget.nature,
                        montant_initial=budget.montant_disponible,  # Report available amount
                        montant_consomme=0.0,
                        service_demandeur=budget.service_demandeur
                    )
                    
                    success, _, _ = self.create_budget(new_budget)
                    if success:
                        reported_count += 1
            
            return True, f"{reported_count} budget(s) reporté(s) de {from_year} vers {to_year}"
        except Exception as e:
            return False, f"Erreur lors du report: {str(e)}"
    
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