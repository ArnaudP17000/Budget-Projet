# GitHub Copilot Instructions for Budget-Projet

## Project Overview

Budget-Projet is a professional French budget management application with a modern dark-themed GUI built using Python and CustomTkinter. The application manages budgets, contracts, purchase orders, projects, clients, contacts, and todo lists with SQLite database backend.

**Architecture:** Clean MVC pattern with three distinct layers:
- **Database Layer** (`database/`): SQLite with triggers, dataclass models
- **Business Logic Layer** (`business/`): 8 manager classes with validation
- **UI Layer** (`ui/`): CustomTkinter views with sidebar navigation

## Technology Stack

- **Python:** 3.10+ required
- **UI Framework:** CustomTkinter 5.2.1 (modern dark theme)
- **Database:** SQLite with automatic triggers
- **Dependencies:** Pillow, Matplotlib, python-dateutil, openpyxl
- **Entry Point:** `main.py`

## Coding Standards

### Language and Localization

**CRITICAL: This is a French-first application**
- All UI labels, button text, and messages MUST be in French
- All error messages MUST be in French
- Variable names use French terms (e.g., `montant`, `client_nom`, `bons_commande`)
- Comments and docstrings should be in French or English (French preferred for business logic)
- User-facing strings are never in English

### Naming Conventions

- **snake_case** for functions, methods, variables
- **PascalCase** for classes
- **UPPER_CASE** for constants (see `utils/constants.py`)
- French business terms in names (e.g., `contrat`, `projet`, `bon_commande`)

### Code Structure

**File Organization:**
```
module/
├── __init__.py
├── manager_name.py     # Business logic managers
├── model_name.py       # Dataclass models
└── view_name.py        # UI views
```

**Import Order:**
1. Standard library imports
2. Third-party imports (customtkinter, etc.)
3. Local imports (database, business, utils)

### Type Hints

- Always use type hints for function parameters and return values
- Use `Optional[Type]` for nullable values
- Use `tuple[bool, str, Optional[Type]]` for standard operation returns
- Import types from `typing` module

Example:
```python
from typing import Optional, List

def create_client(self, client: Client) -> tuple[bool, str, Optional[int]]:
    """Creates a new client in the database."""
    # Implementation
```

### Docstrings

- Add docstrings to all classes and public methods
- Use simple format: brief description of purpose
- French or English acceptable, but be consistent within a file

Example:
```python
def validate_budget(self, budget_id: int) -> tuple[bool, str]:
    """Valide un budget et met à jour son statut."""
    # Implementation
```

## Error Handling Pattern

**Standard Return Format:** All business logic methods return `tuple[bool, str, Optional[result]]`
- First element: success/failure boolean
- Second element: French message for the user
- Third element (optional): result value (ID, object, etc.)

**Pattern:**
```python
def operation(self, params) -> tuple[bool, str, Optional[int]]:
    # 1. Validation first
    valid, msg = validate_required_field(value, "Nom du champ")
    if not valid:
        return False, msg, None
    
    # 2. Try-except for database operations
    try:
        # perform operation
        return True, "Opération réussie", result_id
    except Exception as e:
        return False, f"Erreur: {str(e)}", None
```

**Never raise exceptions to UI layer** - always catch and return error tuples.

## Database Guidelines

### Connection Management

- Use context manager pattern: `with db_manager.get_connection() as conn:`
- Database manager is dependency-injected into business managers
- All managers accept `DatabaseManager` in `__init__`

### SQLite Best Practices

- Use parameterized queries (NEVER string concatenation)
- Rely on automatic triggers for:
  - `update_budget_disponible`: Auto-calculates available budget
  - `imputer_bc_au_budget`: Auto-imputes purchase orders to budgets
- Foreign key constraints are enabled
- Use transactions for multi-step operations

### Models

- Use Python `dataclass` for all models (see `database/models.py`)
- Models mirror database table structure
- Include type hints and optional default values

Example:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Client:
    id: Optional[int] = None
    nom: str = ""
    secteur: str = ""
    # ... other fields
```

## UI/UX Guidelines

### CustomTkinter Theme

**Colors (defined in `utils/constants.py`):**
- Primary: `#0d7377` (dark turquoise)
- Success: `#4ecdc4` (light cyan)
- Danger: `#ff6b6b` (red)
- Warning: `#ffa500` (orange)
- Background: `#0a0a0a` and `#1a1a1a`

**Always use these color constants** - never hardcode colors.

### UI Patterns

**View Structure:**
- Each view inherits from `ctk.CTkFrame`
- Main window has sidebar navigation (`ui/main_window.py`)
- Active menu button highlighted with primary color
- All views contain title, filters, table, and action buttons

**Component Layout:**
```python
class MyView(ctk.CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        # Filters
        # Table/Content
        # Action buttons
```

**Forms and Dialogs:**
- Use `CTkToplevel` for popup forms
- Include validation before submission
- Show success/error messages with appropriate colors
- Close dialog only on successful operation

### User Feedback

- Success messages: Use success color (green/cyan)
- Error messages: Use danger color (red)
- Warnings: Use warning color (orange)
- Loading states: Display "Chargement..." or spinner
- Confirmation dialogs for destructive actions

## Business Logic Patterns

### Manager Classes

All managers follow this structure:

```python
class EntityManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_entity(self, entity: Entity) -> tuple[bool, str, Optional[int]]:
        """Creates a new entity."""
        # Validation
        # Database operation
        # Return tuple
    
    def update_entity(self, entity: Entity) -> tuple[bool, str]:
        """Updates an existing entity."""
        pass
    
    def delete_entity(self, entity_id: int) -> tuple[bool, str]:
        """Deletes an entity."""
        pass
    
    def get_entity(self, entity_id: int) -> Optional[Entity]:
        """Retrieves a single entity."""
        pass
    
    def list_entities(self, filters: dict) -> List[Entity]:
        """Lists entities with optional filters."""
        pass
```

### Validation

- Use validators from `utils/validators.py`
- Validate required fields first
- Validate format (email, phone, postal code)
- Check business rules (budget availability, contract dates, etc.)
- Return French error messages

Available validators:
- `validate_required_field(value, field_name)`
- `validate_email(email)`
- `validate_phone(phone)`
- `validate_postal_code(code)`
- `validate_montant(montant)`

### Status-Based Filtering

Many entities have status fields with specific values:
- **Contracts:** "Actif", "Expiré", "Résilié"
- **Projects:** "En cours", "Terminé", "Suspendu"
- **Purchase Orders:** Validated/Not Validated (boolean)
- **Todos:** Priority levels ("Basse", "Normale", "Haute", "Urgente")

Respect these exact string values.

## Testing and Validation

### Current Testing Approach

- **No formal test framework** (no pytest/unittest)
- Validation occurs at business logic layer
- Database constraints via triggers
- Manual verification via import checks

### Before Committing Changes

1. **Import verification:**
   ```python
   python -c "from module.file import Class; print('✅ Import successful')"
   ```

2. **Database initialization:**
   ```python
   from database.db_manager import DatabaseManager
   db = DatabaseManager('test.db')
   db.initialize_database()
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Visual verification:** Test changed views/features manually

### When Adding New Features

- Add validation methods to `utils/validators.py`
- Add formatting methods to `utils/formatters.py`
- Add constants to `utils/constants.py`
- Follow existing patterns in similar managers/views
- Ensure French messages throughout

## Common Pitfalls to Avoid

1. **❌ DO NOT use English in UI strings** - everything must be in French
2. **❌ DO NOT hardcode colors** - use constants from `utils/constants.py`
3. **❌ DO NOT raise exceptions to UI** - always return error tuples
4. **❌ DO NOT skip validation** - validate before database operations
5. **❌ DO NOT use string concatenation for SQL** - use parameterized queries
6. **❌ DO NOT break the MVC pattern** - UI should not access database directly
7. **❌ DO NOT modify validated purchase orders** - business rule enforced
8. **❌ DO NOT forget context managers** - use `with db_manager.get_connection()`

## Working with Existing Code

### When Modifying Managers

- Maintain the standard return tuple format
- Keep validation logic consistent
- Update related UI views if data structure changes
- Test with the actual UI, not just imports

### When Modifying UI

- Use existing component patterns from other views
- Maintain consistent spacing and layout
- Keep French labels and messages
- Update refresh methods when data changes
- Test navigation between views

### When Modifying Database

- Update both `db_manager.py` schema and `models.py` dataclasses
- Consider trigger impacts
- Add migration logic if needed
- Test with existing data

## Dependencies and Setup

### Installing New Dependencies

- Add to `requirements.txt` with version pinning
- Use stable versions (avoid pre-releases)
- Check compatibility with Python 3.10+
- Test on fresh virtual environment

### Running the Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## File Modification Guidelines

### Small Changes

- Change only what's necessary
- Keep existing patterns and style
- Add comments only if logic is complex
- Test the specific feature changed

### Large Changes

- Consider impact on dependent modules
- Update documentation if architecture changes
- Verify all related views/managers still work
- Test database migrations thoroughly

## Git and Version Control

- **Commit messages:** In English or French, be descriptive
- **Branch naming:** Use lowercase with hyphens (e.g., `feature/add-reports`)
- **File organization:** Don't move files unless absolutely necessary
- **.gitignore:** Excludes `__pycache__`, `*.db` (except schema), backups, venv

## Additional Resources

- **Main documentation:** `README.md` - comprehensive project overview
- **Installation guide:** `INSTALLATION.md` - setup instructions
- **Constants reference:** `utils/constants.py` - all application constants
- **Color scheme:** Dark theme with turquoise primary color
- **Database schema:** `database/db_manager.py` - table definitions and triggers

## Summary for Copilot

When working on this project:
1. **Think in French** - all user-facing content must be in French
2. **Follow MVC** - respect the three-layer architecture
3. **Return tuples** - use `(bool, str, Optional[result])` pattern
4. **Validate early** - check inputs before database operations
5. **Use constants** - never hardcode colors or magic numbers
6. **Maintain patterns** - follow existing code structure
7. **Test manually** - run the UI to verify changes work
8. **Keep it minimal** - make the smallest changes necessary

This is a production-ready application. Maintain its quality and consistency.
