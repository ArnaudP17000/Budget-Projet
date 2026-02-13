"""
Database Manager for Budget Management Application.
Handles SQLite database operations, schema creation, and triggers.
"""
import sqlite3
import os
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path: str = "budget_projet.db"):
        """Initialize database manager with database path."""
        self.db_path = db_path
        self._connection = None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return last row id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute multiple queries with different parameters."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
    
    def initialize_database(self):
        """Initialize database with schema and triggers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL UNIQUE,
                    raison_sociale TEXT,
                    adresse TEXT,
                    code_postal TEXT,
                    ville TEXT,
                    email TEXT,
                    telephone TEXT,
                    actif INTEGER DEFAULT 1
                )
            """)
            
            # Create contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    fonction TEXT,
                    telephone TEXT,
                    email TEXT,
                    notes TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
                )
            """)
            
            # Create contrats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contrats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_contrat TEXT NOT NULL UNIQUE,
                    client_id INTEGER,
                    contact_id INTEGER,
                    date_debut DATE,
                    date_fin DATE,
                    montant REAL DEFAULT 0,
                    description TEXT,
                    statut TEXT DEFAULT 'Actif' CHECK(statut IN ('Actif', 'Expiré', 'Résilié')),
                    alerte_6_mois INTEGER DEFAULT 0,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
                )
            """)
            
            # Create budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    annee INTEGER NOT NULL,
                    nature TEXT NOT NULL CHECK(nature IN ('Fonctionnement', 'Investissement')),
                    montant_initial REAL DEFAULT 0,
                    montant_consomme REAL DEFAULT 0,
                    montant_disponible REAL DEFAULT 0,
                    service_demandeur TEXT,
                    UNIQUE(client_id, annee, nature),
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                )
            """)
            
            # Create bons_commande table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bons_commande (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_bc TEXT NOT NULL UNIQUE,
                    client_id INTEGER NOT NULL,
                    contrat_id INTEGER,
                    nature TEXT NOT NULL CHECK(nature IN ('Fonctionnement', 'Investissement')),
                    type TEXT NOT NULL CHECK(type IN ('Assistance', 'Formation', 'Prestation', 'Matériel', 'Licences')),
                    service_demandeur TEXT,
                    montant REAL DEFAULT 0,
                    valide INTEGER DEFAULT 0,
                    date_validation DATETIME,
                    description TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
                    FOREIGN KEY (contrat_id) REFERENCES contrats(id) ON DELETE SET NULL
                )
            """)
            
            # Create projets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_projet TEXT NOT NULL UNIQUE,
                    fap_redigee INTEGER DEFAULT 0,
                    porteur_projet TEXT,
                    service_demandeur TEXT,
                    contacts_pris TEXT,
                    sourcing TEXT,
                    clients_contactes TEXT,
                    pret_materiel_logiciel TEXT,
                    date_debut DATE,
                    date_fin_estimee DATE,
                    date_mise_service DATE,
                    remarques_1 TEXT,
                    remarques_2 TEXT,
                    statut TEXT DEFAULT 'En cours' CHECK(statut IN ('En cours', 'Terminé', 'Suspendu'))
                )
            """)
            
            # Create investissements_projets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investissements_projets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projet_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('Matériel', 'Licence', 'Installation', 'Formation', 'Accompagnement')),
                    description TEXT,
                    montant_estime REAL DEFAULT 0,
                    FOREIGN KEY (projet_id) REFERENCES projets(id) ON DELETE CASCADE
                )
            """)
            
            # Create contacts_sourcing table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts_sourcing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    projet_id INTEGER NOT NULL,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    entreprise TEXT,
                    telephone TEXT,
                    email TEXT,
                    notes TEXT,
                    FOREIGN KEY (projet_id) REFERENCES projets(id) ON DELETE CASCADE
                )
            """)
            
            # Create todo_list table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS todo_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    motif TEXT NOT NULL,
                    description TEXT,
                    contrat_id INTEGER,
                    date_echeance DATE,
                    priorite TEXT DEFAULT 'Normale' CHECK(priorite IN ('Basse', 'Normale', 'Haute', 'Urgente')),
                    complete INTEGER DEFAULT 0,
                    date_completion DATETIME,
                    FOREIGN KEY (contrat_id) REFERENCES contrats(id) ON DELETE SET NULL
                )
            """)
            
            # Create sauvegardes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sauvegardes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_fichier TEXT NOT NULL,
                    chemin TEXT NOT NULL,
                    date_sauvegarde DATETIME DEFAULT CURRENT_TIMESTAMP,
                    taille_ko REAL DEFAULT 0,
                    commentaire TEXT
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contrats_client ON contrats(client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contrats_dates ON contrats(date_debut, date_fin)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_client ON budgets(client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_annee ON budgets(annee)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bc_client ON bons_commande(client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bc_valide ON bons_commande(valide)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_todo_complete ON todo_list(complete)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_client ON contacts(client_id)")
            
            # Create triggers
            
            # Trigger 1: Update budget disponible after insert
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_budget_disponible
                AFTER INSERT ON budgets
                FOR EACH ROW
                BEGIN
                    UPDATE budgets 
                    SET montant_disponible = montant_initial - montant_consomme
                    WHERE id = NEW.id;
                END
            """)
            
            # Trigger 2: Impute BC to budget when validated
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS imputer_bc_au_budget
                AFTER UPDATE OF valide ON bons_commande
                FOR EACH ROW
                WHEN NEW.valide = 1 AND OLD.valide = 0
                BEGIN
                    UPDATE budgets
                    SET montant_consomme = montant_consomme + NEW.montant,
                        montant_disponible = montant_initial - (montant_consomme + NEW.montant)
                    WHERE client_id = NEW.client_id 
                    AND nature = NEW.nature
                    AND annee = CAST(strftime('%Y', 'now') AS INTEGER);
                    
                    UPDATE bons_commande
                    SET date_validation = CURRENT_TIMESTAMP
                    WHERE id = NEW.id;
                END
            """)
            
            conn.commit()
            print("✅ Database schema initialized successfully")
