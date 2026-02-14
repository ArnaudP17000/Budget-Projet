"""
Sauvegarde View - Gestion des sauvegardes et restaurations.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import shutil
import os
from typing import Optional, List
from database.db_manager import DatabaseManager
from utils.constants import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    COLOR_BG_CARD
)
from utils.formatters import format_datetime, format_size_kb


class SauvegardeView(ctk.CTkFrame):
    """Backup and restore management view."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize sauvegarde view."""
        super().__init__(parent, fg_color="transparent")
        self.db_manager = db_manager
        self.backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.create_widgets()
        self.load_backups()
    
    def create_widgets(self):
        """Create view widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header with title and actions
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="💾 Sauvegarde et Restauration",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Actualiser",
            command=self.load_backups,
            width=140,
            height=36,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        refresh_btn.grid(row=0, column=2, padx=5)
        
        new_backup_btn = ctk.CTkButton(
            header_frame,
            text="💾 Créer Sauvegarde",
            command=self.show_create_backup_dialog,
            width=180,
            height=36,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        new_backup_btn.grid(row=0, column=3, padx=5)
        
        # Info panel
        info_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=8)
        info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        info_text = (
            "ℹ️ Les sauvegardes créent une copie complète de la base de données.\n"
            "⚠️ La restauration remplacera toutes les données actuelles par celles de la sauvegarde.\n"
            "💡 Il est recommandé de créer une sauvegarde régulièrement."
        )
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color="gray70",
            justify="left"
        ).pack(padx=15, pady=12, anchor="w")
        
        # Scrollable frame for backups
        self.backups_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.backups_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.backups_scroll.grid_columnconfigure(0, weight=1)
    
    def load_backups(self):
        """Load and display available backups."""
        # Clear existing
        for widget in self.backups_scroll.winfo_children():
            widget.destroy()
        
        # Get list of backup files
        backups = self.get_backup_list()
        
        if not backups:
            no_data_label = ctk.CTkLabel(
                self.backups_scroll,
                text="Aucune sauvegarde trouvée\n\n💡 Créez votre première sauvegarde",
                font=ctk.CTkFont(size=16),
                text_color="gray50"
            )
            no_data_label.pack(pady=50)
            return
        
        # Display backups (most recent first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        for backup in backups:
            self.create_backup_card(backup)
    
    def get_backup_list(self) -> List[dict]:
        """Get list of available backup files."""
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.db') or filename.endswith('.sqlite'):
                    filepath = os.path.join(self.backup_dir, filename)
                    stats = os.stat(filepath)
                    
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'timestamp': datetime.fromtimestamp(stats.st_mtime),
                        'size_kb': stats.st_size / 1024
                    })
        except Exception as e:
            print(f"Erreur lors de la lecture des sauvegardes: {e}")
        
        return backups
    
    def create_backup_card(self, backup: dict):
        """Create a backup card."""
        card = ctk.CTkFrame(self.backups_scroll, fg_color=COLOR_BG_CARD, corner_radius=10)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=15)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Filename
        filename_label = ctk.CTkLabel(
            info_frame,
            text=f"💾 {backup['filename']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        filename_label.grid(row=0, column=0, sticky="w", columnspan=3)
        
        # Details frame
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Date
        ctk.CTkLabel(
            details_frame,
            text="Date de Création",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            details_frame,
            text=format_datetime(backup['timestamp']),
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).grid(row=1, column=0, sticky="w")
        
        # Size
        ctk.CTkLabel(
            details_frame,
            text="Taille",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).grid(row=0, column=1)
        
        ctk.CTkLabel(
            details_frame,
            text=f"{backup['size_kb']:.2f} KB",
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).grid(row=1, column=1)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        restore_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Restaurer",
            command=lambda b=backup: self.restore_backup(b),
            width=110,
            height=28,
            fg_color=COLOR_WARNING,
            hover_color=COLOR_PRIMARY
        )
        restore_btn.pack(side="right", padx=5)
        
        export_btn = ctk.CTkButton(
            btn_frame,
            text="📤 Exporter",
            command=lambda b=backup: self.export_backup(b),
            width=110,
            height=28,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_SUCCESS
        )
        export_btn.pack(side="right", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Supprimer",
            command=lambda b=backup: self.delete_backup(b),
            width=110,
            height=28,
            fg_color=COLOR_DANGER,
            hover_color="#cc0000"
        )
        delete_btn.pack(side="right", padx=5)
    
    def show_create_backup_dialog(self):
        """Show dialog to create a new backup."""
        dialog = CreateBackupDialog(self, self.backup_dir)
        dialog.wait_window()
        if dialog.result:
            self.load_backups()
    
    def restore_backup(self, backup: dict):
        """Restore from a backup."""
        if messagebox.askyesno(
            "⚠️ ATTENTION - Restauration",
            f"Êtes-vous sûr de vouloir restaurer cette sauvegarde?\n\n"
            f"Fichier: {backup['filename']}\n"
            f"Date: {format_datetime(backup['timestamp'])}\n\n"
            f"⚠️ CETTE ACTION EST IRRÉVERSIBLE!\n"
            f"Toutes les données actuelles seront remplacées par celles de cette sauvegarde.\n\n"
            f"💡 Conseil: Créez d'abord une sauvegarde des données actuelles.",
            icon='warning'
        ):
            # Double confirmation
            if messagebox.askyesno(
                "⚠️ CONFIRMATION FINALE",
                "Dernière confirmation nécessaire.\n\n"
                "Confirmez-vous la restauration de cette sauvegarde?",
                icon='warning'
            ):
                try:
                    # Get current database path
                    db_path = self.db_manager.db_path
                    
                    # Close current connection
                    self.db_manager.close()
                    
                    # Create backup of current database before restoring
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    pre_restore_backup = os.path.join(self.backup_dir, f"pre_restore_{timestamp}.db")
                    shutil.copy2(db_path, pre_restore_backup)
                    
                    # Restore from backup
                    shutil.copy2(backup['filepath'], db_path)
                    
                    # Reconnect
                    self.db_manager.connect()
                    
                    messagebox.showinfo(
                        "Succès",
                        f"Sauvegarde restaurée avec succès!\n\n"
                        f"Une copie de sécurité des données précédentes a été créée:\n"
                        f"{os.path.basename(pre_restore_backup)}\n\n"
                        f"⚠️ L'application va redémarrer pour appliquer les changements."
                    )
                    
                    # Request application restart
                    self.event_generate("<<RestartRequired>>")
                    
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la restauration:\n{e}")
                    # Try to reconnect
                    try:
                        self.db_manager.connect()
                    except:
                        pass
    
    def export_backup(self, backup: dict):
        """Export a backup to a chosen location."""
        # Ask user where to save
        export_path = filedialog.asksaveasfilename(
            title="Exporter la sauvegarde",
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile=backup['filename']
        )
        
        if export_path:
            try:
                shutil.copy2(backup['filepath'], export_path)
                messagebox.showinfo(
                    "Succès",
                    f"Sauvegarde exportée avec succès vers:\n{export_path}"
                )
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")
    
    def delete_backup(self, backup: dict):
        """Delete a backup file."""
        if messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment supprimer cette sauvegarde?\n\n"
            f"Fichier: {backup['filename']}\n"
            f"Date: {format_datetime(backup['timestamp'])}\n\n"
            f"Cette action est irréversible."
        ):
            try:
                os.remove(backup['filepath'])
                messagebox.showinfo("Succès", "Sauvegarde supprimée avec succès")
                self.load_backups()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{e}")


class CreateBackupDialog(ctk.CTkToplevel):
    """Dialog for creating a new backup."""
    
    def __init__(self, parent, backup_dir: str):
        super().__init__(parent)
        self.backup_dir = backup_dir
        self.result = None
        
        self.title("Créer une Sauvegarde")
        self.geometry("500x350")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Get database manager from parent
        self.db_manager = parent.db_manager
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="💾 Créer une Nouvelle Sauvegarde",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Info
        info_label = ctk.CTkLabel(
            main_frame,
            text="La sauvegarde créera une copie complète de la base de données\n"
                 "avec un horodatage pour faciliter l'identification.\n\n"
                 "Vous pouvez ajouter un commentaire optionnel pour décrire\n"
                 "le contexte de cette sauvegarde.",
            font=ctk.CTkFont(size=12),
            text_color="gray70",
            justify="left"
        )
        info_label.pack(pady=(0, 20))
        
        # Suggested filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suggested_name = f"backup_{timestamp}.db"
        
        ctk.CTkLabel(
            main_frame,
            text=f"Nom du fichier: {suggested_name}",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        ).pack(anchor="w", pady=(0, 15))
        
        # Comment
        ctk.CTkLabel(main_frame, text="Commentaire (optionnel):", anchor="w").pack(fill="x", pady=(0, 5))
        self.comment_entry = ctk.CTkEntry(main_frame, placeholder_text="Ex: Avant migration, fin de mois, etc.")
        self.comment_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=self.destroy,
            width=100,
            fg_color="gray40",
            hover_color="gray50"
        )
        cancel_btn.pack(side="right", padx=5)
        
        create_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Créer",
            command=self.create_backup,
            width=100,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_PRIMARY
        )
        create_btn.pack(side="right", padx=5)
    
    def create_backup(self):
        """Create the backup."""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comment = self.comment_entry.get().strip()
            
            # Create safe filename from comment
            if comment:
                # Remove invalid characters
                safe_comment = "".join(c for c in comment if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_comment = safe_comment.replace(' ', '_')[:30]  # Limit length
                filename = f"backup_{timestamp}_{safe_comment}.db"
            else:
                filename = f"backup_{timestamp}.db"
            
            backup_path = os.path.join(self.backup_dir, filename)
            
            # Get current database path
            db_path = self.db_manager.db_path
            
            # Create backup
            shutil.copy2(db_path, backup_path)
            
            # Get file size
            file_size = os.path.getsize(backup_path) / 1024  # KB
            
            messagebox.showinfo(
                "Succès",
                f"Sauvegarde créée avec succès!\n\n"
                f"Fichier: {filename}\n"
                f"Taille: {file_size:.2f} KB\n"
                f"Emplacement: {self.backup_dir}"
            )
            
            self.result = True
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la sauvegarde:\n{e}")
