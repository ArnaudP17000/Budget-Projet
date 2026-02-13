"""
Todo Manager - Business logic for todo list management.
"""
from typing import List, Optional
from datetime import datetime, date
from database.db_manager import DatabaseManager
from database.models import TodoItem
from utils.validators import validate_required_field
from utils.constants import PRIORITES_TODO
from utils.formatters import parse_date, parse_datetime


class TodoManager:
    """Manages todo list business logic."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_all_todos(self, complete: Optional[bool] = None) -> List[TodoItem]:
        """Get all todos with optional filter."""
        query = "SELECT * FROM todo_list WHERE 1=1"
        params = []
        
        if complete is not None:
            query += " AND complete = ?"
            params.append(1 if complete else 0)
        
        query += " ORDER BY CASE priorite WHEN 'Urgente' THEN 1 WHEN 'Haute' THEN 2 WHEN 'Normale' THEN 3 ELSE 4 END, date_echeance"
        
        rows = self.db.execute_query(query, tuple(params))
        return [self._row_to_todo(row) for row in rows]
    
    def get_todo_by_id(self, todo_id: int) -> Optional[TodoItem]:
        """Get todo by ID."""
        query = "SELECT * FROM todo_list WHERE id = ?"
        rows = self.db.execute_query(query, (todo_id,))
        if rows:
            return self._row_to_todo(rows[0])
        return None
    
    def create_todo(self, todo: TodoItem) -> tuple[bool, str, Optional[int]]:
        """Create new todo."""
        # Validate required fields
        valid, msg = validate_required_field(todo.motif, "Motif")
        if not valid:
            return False, msg, None
        
        if todo.priorite not in PRIORITES_TODO:
            return False, f"Priorité invalide. Valeurs acceptées: {', '.join(PRIORITES_TODO)}", None
        
        try:
            query = """
                INSERT INTO todo_list (motif, description, contrat_id, date_echeance, priorite, complete)
                VALUES (?, ?, ?, ?, ?, 0)
            """
            todo_id = self.db.execute_update(
                query,
                (todo.motif, todo.description, todo.contrat_id, todo.date_echeance, todo.priorite)
            )
            return True, "Tâche créée avec succès", todo_id
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_todo(self, todo: TodoItem) -> tuple[bool, str]:
        """Update existing todo."""
        if not todo.id:
            return False, "ID todo requis"
        
        # Validate required fields
        valid, msg = validate_required_field(todo.motif, "Motif")
        if not valid:
            return False, msg
        
        if todo.priorite not in PRIORITES_TODO:
            return False, f"Priorité invalide. Valeurs acceptées: {', '.join(PRIORITES_TODO)}"
        
        try:
            query = """
                UPDATE todo_list
                SET motif = ?, description = ?, contrat_id = ?, date_echeance = ?, priorite = ?
                WHERE id = ?
            """
            self.db.execute_update(
                query,
                (todo.motif, todo.description, todo.contrat_id, todo.date_echeance,
                 todo.priorite, todo.id)
            )
            return True, "Tâche mise à jour avec succès"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def toggle_complete(self, todo_id: int) -> tuple[bool, str]:
        """Toggle todo completion status."""
        todo = self.get_todo_by_id(todo_id)
        if not todo:
            return False, "Tâche introuvable"
        
        new_status = not todo.complete
        date_completion = datetime.now() if new_status else None
        
        try:
            query = "UPDATE todo_list SET complete = ?, date_completion = ? WHERE id = ?"
            self.db.execute_update(query, (1 if new_status else 0, date_completion, todo_id))
            status_text = "complétée" if new_status else "réactivée"
            return True, f"Tâche {status_text} avec succès"
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    def delete_todo(self, todo_id: int) -> tuple[bool, str]:
        """Delete todo."""
        try:
            query = "DELETE FROM todo_list WHERE id = ?"
            self.db.execute_update(query, (todo_id,))
            return True, "Tâche supprimée avec succès"
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    def sync_contrats_to_todo(self, contrat_manager) -> tuple[bool, str, int]:
        """Synchronize contracts with alerts to todo list."""
        contrats_alerte = contrat_manager.get_contrats_with_alerts()
        
        added_count = 0
        for contrat in contrats_alerte:
            # Check if already exists in todo
            query = "SELECT id FROM todo_list WHERE contrat_id = ? AND complete = 0"
            existing = self.db.execute_query(query, (contrat.id,))
            
            if not existing:
                # Create todo for this contract
                todo = TodoItem(
                    motif=f"Renouvellement contrat {contrat.numero_contrat}",
                    description=f"Le contrat {contrat.numero_contrat} expire le {contrat.date_fin}. Action requise.",
                    contrat_id=contrat.id,
                    date_echeance=contrat.date_fin,
                    priorite="Haute",
                    complete=False
                )
                success, msg, _ = self.create_todo(todo)
                if success:
                    added_count += 1
        
        if added_count > 0:
            return True, f"{added_count} tâche(s) ajoutée(s) depuis les contrats", added_count
        else:
            return True, "Aucune nouvelle tâche à ajouter", 0
    
    def _row_to_todo(self, row) -> TodoItem:
        """Convert database row to TodoItem object."""
        date_echeance = parse_date(row['date_echeance']) if row['date_echeance'] else None
        date_completion = parse_datetime(row['date_completion']) if row['date_completion'] else None
        
        return TodoItem(
            id=row['id'],
            motif=row['motif'],
            description=row['description'] or "",
            contrat_id=row['contrat_id'],
            date_echeance=date_echeance,
            priorite=row['priorite'],
            complete=bool(row['complete']),
            date_completion=date_completion
        )
