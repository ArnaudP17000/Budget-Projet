import sqlite3

conn = sqlite3.connect('budget.db')
cursor = conn.cursor()

# Créer la table prospects_projets
cursor.execute("""
    CREATE TABLE IF NOT EXISTS prospects_projets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        projet_id INTEGER NOT NULL,
        nom_prospect TEXT NOT NULL,
        description_offre TEXT,
        investissement_licence REAL DEFAULT 0,
        investissement_materiel REAL DEFAULT 0,
        investissement_logiciel REAL DEFAULT 0,
        cout_formation REAL DEFAULT 0,
        frais_maintenance REAL DEFAULT 0,
        total_estime REAL GENERATED ALWAYS AS (
            investissement_licence + investissement_materiel + 
            investissement_logiciel + cout_formation + frais_maintenance
        ) STORED,
        technologies TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (projet_id) REFERENCES projets(id) ON DELETE CASCADE
    )
""")

conn.commit()
print("✅ Table prospects_projets créée avec succès !")

# Vérifier
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prospects_projets'")
result = cursor.fetchone()
if result:
    print(f"✅ Table confirmée : {result[0]}")
else:
    print("❌ Erreur : table non créée")

conn.close()