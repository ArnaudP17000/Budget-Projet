"""
Todo View - Gestion de la liste des tâches.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
from typing import Optional
from database.db_manager import DatabaseManager
from business.todo_manager import TodoManager
from business.contrat_manager import ContratManager
from database.models import TodoItem
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD, PRIORITES_TODO, PRIORITY_COLORS
)
from utils.formatters import format_date, format_datetime, parse_date
from utils.validators import validate_required_field


class TodoView(ctk.CTkFrame):
    """Todo list management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize todo view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.todo_manager = TodoManager(db_manager)
        self.contrat_manager = ContratManager(db_manager)
        
        self.create_widgets()
        self.load_todos()
    
    def create_widgets(self):
        """Create view widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header with title and actions
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="✅ Liste des Tâches",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        sync_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Sync Contrats",
            command=self.sync_contrats,
            width=150,
            height=36,
            fg_color=COLOR_WARNING,
            hover_color=COLOR_PRIMARY
        )
        sync_btn.grid(row=0, column=2, padx=5)
        
        new_btn = ctk.CTkButton(
            header_frame,
            text="➕ Nouvelle Tâche",
            command=self.show_create_dialog,
            width=180,
            height=36,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        new_btn.grid(row=0, column=3, padx=5)
        
        # Main container with two sections
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_container.grid_columnconfigure((0, 1), weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # Active tasks section
        active_header = ctk.CTkFrame(main_container, fg_color=COLOR_BG_CARD, corner_radius=8)
        active_header.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        
        ctk.CTkLabel(
            active_header,
            text="📋 Tâches Actives",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(side="left", padx=15, pady=10)
        
        self.active_count_label = ctk.CTkLabel(
            active_header,
            text="0",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        self.active_count_label.pack(side="right", padx=15, pady=10)
        
        self.active_scroll = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.active_scroll.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.active_scroll.grid_columnconfigure(0, weight=1)
        
        # Completed tasks section
        completed_header = ctk.CTkFrame(main_container, fg_color=COLOR_BG_CARD, corner_radius=8)
        completed_header.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        ctk.CTkLabel(
            completed_header,
            text="✅ Tâches Complétées",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLOR_SUCCESS
        ).pack(side="left", padx=15, pady=10)
        
        self.completed_count_label = ctk.CTkLabel(
            completed_header,
            text="0",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        self.completed_count_label.pack(side="right", padx=15, pady=10)
        
        self.completed_scroll = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.completed_scroll.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        self.completed_scroll.grid_columnconfigure(0, weight=1)
    
    def load_todos(self):
        """Load and display todos."""
        # Clear existing
        for widget in self.active_scroll.winfo_children():
            widget.destroy()
        for widget in self.completed_scroll.winfo_children():
            widget.destroy()
        
        # Load todos
        active_todos = self.todo_manager.get_all_todos(complete=False)
        completed_todos = self.todo_manager.get_all_todos(complete=True)
        
        # Update counts
        self.active_count_label.configure(text=str(len(active_todos)))
        self.completed_count_label.configure(text=str(len(completed_todos)))
        
        # Display active todos
        if not active_todos:
            no_data_label = ctk.CTkLabel(
                self.active_scroll,
                text="Aucune tâche active",
                font=ctk.CTkFont(size=14),
                text_color="gray50"
            )
            no_data_label.pack(pady=30)
        else:
            for todo in active_todos:
                self.create_todo_card(todo, self.active_scroll, is_active=True)
        
        # Display completed todos
        if not completed_todos:
            no_data_label = ctk.CTkLabel(
                self.completed_scroll,
                text="Aucune tâche complétée",
                font=ctk.CTkFont(size=14),
                text_color="gray50"
            )
            no_data_label.pack(pady=30)
        else:
            for todo in completed_todos:
                self.create_todo_card(todo, self.completed_scroll, is_active=False)
    
    def create_todo_card(self, todo: TodoItem, parent, is_active: bool):
        """Create a todo card."""
        # Get priority color
        priority_color = PRIORITY_COLORS.get(todo.priorite, "white")
        
        card = ctk.CTkFrame(parent, fg_color=COLOR_BG_CARD, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Priority indicator bar
        priority_bar = ctk.CTkFrame(card, fg_color=priority_color, width=4, corner_radius=2)
        priority_bar.pack(side="left", fill="y", padx=(0, 10))
        
        # Main content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=(0, 15), pady=15)
        
        # Header with checkbox and priority
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        # Checkbox for completion
        checkbox_var = ctk.BooleanVar(value=todo.complete)
        checkbox = ctk.CTkCheckBox(
            header_frame,
            text="",
            variable=checkbox_var,
            command=lambda t=todo: self.toggle_complete(t),
            width=20
        )
        checkbox.pack(side="left")
        
        # Motif (title)
        motif_label = ctk.CTkLabel(
            header_frame,
            text=todo.motif,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray60" if not is_active else "white"
        )
        motif_label.pack(side="left", padx=(5, 10))
        
        # Priority badge
        priority_label = ctk.CTkLabel(
            header_frame,
            text=todo.priorite,
            font=ctk.CTkFont(size=11),
            text_color=priority_color
        )
        priority_label.pack(side="right")
        
        # Description
        if todo.description:
            desc_label = ctk.CTkLabel(
                content_frame,
                text=todo.description[:200] + ('...' if len(todo.description) > 200 else ''),
                font=ctk.CTkFont(size=11),
                text_color="gray60",
                wraplength=400,
                justify="left"
            )
            desc_label.pack(fill="x", pady=(5, 0))
        
        # Details frame
        details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        details_frame.pack(fill="x", pady=(10, 0))
        
        # Due date
        if todo.date_echeance:
            days_until = (todo.date_echeance - date.today()).days if is_active else None
            
            date_text = format_date(todo.date_echeance)
            if is_active and days_until is not None:
                if days_until < 0:
                    date_text += f" (⚠️ en retard de {abs(days_until)} jour(s))"
                    date_color = COLOR_DANGER
                elif days_until == 0:
                    date_text += " (⚠️ aujourd'hui)"
                    date_color = COLOR_WARNING
                elif days_until <= 7:
                    date_text += f" (dans {days_until} jour(s))"
                    date_color = COLOR_WARNING
                else:
                    date_color = "gray60"
            else:
                date_color = "gray60"
            
            ctk.CTkLabel(
                details_frame,
                text=f"📅 Échéance: {date_text}",
                font=ctk.CTkFont(size=11),
                text_color=date_color
            ).pack(side="left")
        
        # Completion date
        if not is_active and todo.date_completion:
            ctk.CTkLabel(
                details_frame,
                text=f"✅ Complété: {format_datetime(todo.date_completion)}",
                font=ctk.CTkFont(size=11),
                text_color="gray60"
            ).pack(side="right")
        
        # Action buttons (only for active tasks)
        if is_active:
            btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(10, 0))
            
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="✏️",
                command=lambda t=todo: self.show_edit_dialog(t),
                width=40,
                height=28,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_SUCCESS
            )
            edit_btn.pack(side="right", padx=2)
            
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️",
                command=lambda t=todo: self.delete_todo(t),
                width=40,
                height=28,
                fg_color=COLOR_DANGER,
                hover_color="#cc0000"
            )
            delete_btn.pack(side="right", padx=2)
    
    def toggle_complete(self, todo: TodoItem):
        """Toggle todo completion status."""
        success, msg = self.todo_manager.toggle_complete(todo.id)
        if success:
            self.load_todos()
        else:
            messagebox.showerror("Erreur", msg)
    
    def show_create_dialog(self):
        """Show dialog to create a new todo."""
        dialog = TodoDialog(self, self.db_manager, title="Créer une Tâche")
        dialog.wait_window()
        if dialog.result:
            self.load_todos()
    
    def show_edit_dialog(self, todo: TodoItem):
        """Show dialog to edit a todo."""
        dialog = TodoDialog(self, self.db_manager, todo=todo, title="Modifier la Tâche")
        dialog.wait_window()
        if dialog.result:
            self.load_todos()
    
    def delete_todo(self, todo: TodoItem):
        """Delete a todo."""
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer cette tâche?\n\n"
            f"Motif: {todo.motif}"
        ):
            success, msg = self.todo_manager.delete_todo(todo.id)
            if success:
                messagebox.showinfo("Succès", msg)
                self.load_todos()
            else:
                messagebox.showerror("Erreur", msg)
    
    def sync_contrats(self):
        """Synchronize contracts with alerts to todo list."""
        if messagebox.askyesno(
            "Synchronisation",
            "Synchroniser les contrats avec alertes vers la liste des tâches?\n\n"
            "Les contrats expirant dans moins de 6 mois seront ajoutés\n"
            "automatiquement à votre liste de tâches."
        ):
            success, msg, count = self.todo_manager.sync_contrats_to_todo(self.contrat_manager)
            if success:
                messagebox.showinfo("Synchronisation", msg)
                self.load_todos()
            else:
                messagebox.showerror("Erreur", msg)


class TodoDialog(ctk.CTkToplevel):
    """Dialog for creating/editing todos."""
    
    def __init__(self, parent, db_manager: DatabaseManager, todo: Optional[TodoItem] = None, title: str = "Tâche"):
        super().__init__(parent)
        self.db_manager = db_manager
        self.todo_manager = TodoManager(db_manager)
        self.contrat_manager = ContratManager(db_manager)
        self.todo = todo
        self.result = None
        
        self.title(title)
        self.geometry("500x550")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
        if todo:
            self.populate_data()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Motif
        ctk.CTkLabel(main_frame, text="Motif *", anchor="w").pack(fill="x", pady=(0, 5))
        self.motif_entry = ctk.CTkEntry(main_frame, placeholder_text="Titre de la tâche")
        self.motif_entry.pack(fill="x", pady=(0, 15))
        
        # Priorité
        ctk.CTkLabel(main_frame, text="Priorité *", anchor="w").pack(fill="x", pady=(0, 5))
        self.priorite_combo = ctk.CTkComboBox(main_frame, values=PRIORITES_TODO)
        self.priorite_combo.set("Normale")
        self.priorite_combo.pack(fill="x", pady=(0, 15))
        
        # Date échéance
        ctk.CTkLabel(main_frame, text="Date d'Échéance", anchor="w").pack(fill="x", pady=(0, 5))
        self.date_entry = ctk.CTkEntry(main_frame, placeholder_text="YYYY-MM-DD (optionnel)")
        self.date_entry.pack(fill="x", pady=(0, 15))
        
        # Contrat (optional)
        ctk.CTkLabel(main_frame, text="Contrat Lié (optionnel)", anchor="w").pack(fill="x", pady=(0, 5))
        contrats = self.contrat_manager.get_all_contrats()
        contrat_nums = ["Aucun"] + [c.numero_contrat for c in contrats if c.statut == "Actif"]
        self.contrat_combo = ctk.CTkComboBox(main_frame, values=contrat_nums)
        self.contrat_combo.set("Aucun")
        self.contrat_combo.pack(fill="x", pady=(0, 15))
        self.contrat_combo.contrat_map = {c.numero_contrat: c.id for c in contrats if c.statut == "Actif"}
        
        # Description
        ctk.CTkLabel(main_frame, text="Description", anchor="w").pack(fill="x", pady=(0, 5))
        self.description_text = ctk.CTkTextbox(main_frame, height=120)
        self.description_text.pack(fill="x", pady=(0, 15))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=self.destroy,
            width=100,
            fg_color="gray40",
            hover_color="gray50"
        )
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Enregistrer",
            command=self.save,
            width=100,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        save_btn.pack(side="right", padx=5)
    
    def populate_data(self):
        """Populate form with todo data."""
        if self.todo:
            self.motif_entry.insert(0, self.todo.motif)
            self.priorite_combo.set(self.todo.priorite)
            
            if self.todo.date_echeance:
                self.date_entry.insert(0, format_date(self.todo.date_echeance))
            
            if self.todo.contrat_id:
                # Find contrat and set in combo
                contrats = self.contrat_manager.get_all_contrats()
                for c in contrats:
                    if c.id == self.todo.contrat_id:
                        self.contrat_combo.set(c.numero_contrat)
                        break
            
            if self.todo.description:
                self.description_text.insert("1.0", self.todo.description)
    
    def save(self):
        """Save the todo."""
        try:
            # Validate
            motif = self.motif_entry.get().strip()
            valid, msg = validate_required_field(motif, "Motif")
            if not valid:
                messagebox.showerror("Erreur", msg)
                return
            
            priorite = self.priorite_combo.get()
            
            # Parse date
            date_echeance = None
            date_str = self.date_entry.get().strip()
            if date_str:
                date_echeance = parse_date(date_str)
                if not date_echeance:
                    messagebox.showerror("Erreur", "Date invalide (format: YYYY-MM-DD)")
                    return
            
            # Get contrat ID
            contrat_id = None
            contrat_num = self.contrat_combo.get()
            if contrat_num != "Aucun" and contrat_num in self.contrat_combo.contrat_map:
                contrat_id = self.contrat_combo.contrat_map[contrat_num]
            
            description = self.description_text.get("1.0", "end-1c").strip()
            
            # Create or update
            if self.todo:
                # Update
                self.todo.motif = motif
                self.todo.priorite = priorite
                self.todo.date_echeance = date_echeance
                self.todo.contrat_id = contrat_id
                self.todo.description = description
                
                success, msg = self.todo_manager.update_todo(self.todo)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
            else:
                # Create
                new_todo = TodoItem(
                    motif=motif,
                    priorite=priorite,
                    date_echeance=date_echeance,
                    contrat_id=contrat_id,
                    description=description,
                    complete=False
                )
                
                success, msg, todo_id = self.todo_manager.create_todo(new_todo)
                if success:
                    messagebox.showinfo("Succès", msg)
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", msg)
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")
