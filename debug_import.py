"""Debug imports to see what's loaded."""
import sys
import importlib

# Force reload
if 'business.budget_manager' in sys.modules:
    del sys.modules['business.budget_manager']

from business.budget_manager import BudgetManager
import inspect

# Get the signature of create_budget
sig = inspect.signature(BudgetManager.create_budget)
print("Signature de create_budget:")
print(sig)

# Get the source file
source_file = inspect.getfile(BudgetManager)
print(f"\nFichier source: {source_file}")

# Get the method source code (first 10 lines)
source = inspect.getsource(BudgetManager.create_budget)
print("\nPremières lignes de create_budget:")
print(source[:500])