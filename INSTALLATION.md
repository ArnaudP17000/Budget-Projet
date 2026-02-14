# 📦 Guide d'Installation - Budget-Projet

## 🎯 Prérequis

### Système d'exploitation
- Linux (Ubuntu, Debian, Fedora, etc.)
- macOS 10.14+
- Windows 10/11

### Logiciels requis
- **Python 3.10 ou supérieur**
- **pip** (gestionnaire de paquets Python)
- **git** (pour cloner le repository)

### Vérifier Python
```bash
python3 --version
# Devrait afficher Python 3.10.x ou supérieur
```

## 🚀 Installation Rapide

### 1. Cloner le Repository
```bash
git clone https://github.com/ArnaudP17000/Budget-Projet.git
cd Budget-Projet
```

### 2. Créer un Environnement Virtuel (Recommandé)

**Sur Linux/macOS :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Sur Windows :**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

Les dépendances installées :
- `customtkinter==5.2.1` - Interface graphique moderne
- `pillow==10.1.0` - Manipulation d'images
- `matplotlib==3.8.2` - Graphiques (optionnel)
- `python-dateutil==2.8.2` - Gestion des dates

### 4. Lancer l'Application
```bash
python main.py
```

## 🎉 Première Utilisation

Au premier lancement :
1. L'application créera automatiquement la base de données `budget_projet.db`
2. Les tables et triggers seront initialisés
3. L'interface s'ouvrira avec le dashboard
4. Vous pouvez commencer à créer des clients, budgets, contrats, etc.

## 📁 Structure Créée

Après installation, vous aurez :
```
Budget-Projet/
├── budget_projet.db    # Base de données SQLite (créée au 1er lancement)
├── backups/            # Sauvegardes (vide au départ)
├── assets/             # Ressources (vide au départ)
└── venv/               # Environnement virtuel (si créé)
```

## 🔧 Résolution de Problèmes

### Erreur : "No module named 'tkinter'"

**Sur Ubuntu/Debian :**
```bash
sudo apt-get install python3-tk
```

**Sur Fedora :**
```bash
sudo dnf install python3-tkinter
```

**Sur macOS :**
Tkinter est normalement inclus avec Python. Si problème :
```bash
brew install python-tk
```

### Erreur : "pip: command not found"

**Installer pip :**
```bash
# Ubuntu/Debian
sudo apt-get install python3-pip

# Fedora
sudo dnf install python3-pip

# macOS (avec Homebrew)
brew install python
```

### Erreur de permissions

**Sur Linux/macOS :**
```bash
# Utiliser --user si vous n'avez pas les droits admin
pip install --user -r requirements.txt
```

### L'application ne se lance pas

1. **Vérifier la version de Python :**
   ```bash
   python3 --version
   # Doit être >= 3.10
   ```

2. **Vérifier que les dépendances sont installées :**
   ```bash
   pip list | grep customtkinter
   pip list | grep pillow
   ```

3. **Lancer en mode debug :**
   ```bash
   python main.py 2>&1 | tee debug.log
   ```

## 📊 Test de l'Installation

Pour vérifier que tout fonctionne :

```bash
python3 -c "
from database.db_manager import DatabaseManager
from business.budget_manager import BudgetManager
db = DatabaseManager(':memory:')
db.initialize_database()
print('✅ Installation réussie!')
"
```

## 🆘 Support

En cas de problème :
1. Consultez la [documentation](README.md)
2. Vérifiez les [issues GitHub](https://github.com/ArnaudP17000/Budget-Projet/issues)
3. Créez une nouvelle issue avec :
   - Version de Python
   - Système d'exploitation
   - Message d'erreur complet

## 🔄 Mise à Jour

Pour mettre à jour l'application :

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python main.py
```

## 💾 Sauvegarde

Il est recommandé de sauvegarder régulièrement :
- `budget_projet.db` - Base de données principale
- `backups/` - Sauvegardes créées par l'application

L'application inclut une fonction de sauvegarde/restauration dans le menu **💾 Sauvegarde**.

---

**Version** : 1.0.0  
**Date** : Février 2026  
**Auteur** : ArnaudP17000
