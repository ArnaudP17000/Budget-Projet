"""Test budget creation."""
from database.db_manager import DatabaseManager
from business.budget_manager import BudgetManager
from database.models import Budget

# Initialize
db = DatabaseManager()
budget_mgr = BudgetManager(db)

# Create test budget
test_budget = Budget(
    client_id=1,
    annee=2026,
    nature="Fonctionnement",
    montant_initial=10000.0,
    montant_consomme=0.0,
    service_demandeur="Test"
)

print("Testing budget creation...")
success, message, budget_id = budget_mgr.create_budget(test_budget)
print(f"Success: {success}")
print(f"Message: {message}")
print(f"ID: {budget_id}")