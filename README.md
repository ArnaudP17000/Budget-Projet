# 💰 Budget-Projet - Application de Gestion Budgétaire

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2.1-green.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)](https://www.sqlite.org/)

Application professionnelle de gestion budgétaire avec interface graphique moderne en dark theme.

## 📋 Description

Budget-Projet est une application complète de gestion budgétaire développée en Python avec CustomTkinter. Elle permet de gérer :
- 💰 **Budgets** (Fonctionnement & Investissement)
- 📄 **Contrats** avec alertes d'expiration
- 🛒 **Bons de commande** avec imputation automatique
- 📁 **Projets** avec FAP et investissements
- 👥 **Clients** et **Contacts**
- ✅ **To-Do List** synchronisée avec les contrats
- 💾 **Sauvegarde/Restauration** de la base de données

## ✨ Fonctionnalités Principales

### 🎯 Dashboard
- Vue d'ensemble avec 4 KPIs principaux
- Budgets Fonctionnement et Investissement
- Contrats actifs et alertes
- Projets en cours et sans FAP

### 💰 Gestion des Budgets
- Filtrage par année et nature
- Barres de progression visuelles
- Report automatique d'une année à l'autre
- Imputation automatique des bons de commande

### 📄 Gestion des Contrats
- Alertes visuelles pour expiration < 6 mois
- Filtrage par statut (Actif/Expiré/Résilié)
- Liaison avec clients et contacts

### 🛒 Bons de Commande
- Numérotation automatique (BC-YYYY-NNNN)
- Validation avec imputation au budget
- Vérification de disponibilité budgétaire
- Impossible de modifier un BC validé

### 📁 Projets
- Suivi complet du cycle de vie
- Gestion des investissements prévisionnels
- Contacts sourcing
- Popup détaillée pour chaque projet

### ✅ To-Do List
- Deux sections : En cours / Complétées
- Priorités avec codes couleur
- Synchronisation automatique avec les contrats
- Liaison optionnelle à un contrat

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/ArnaudP17000/Budget-Projet.git
cd Budget-Projet
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Lancer l'application**
```bash
python main.py
```

## 📂 Structure du Projet

```
Budget-Projet/
├── main.py                 # Point d'entrée de l'application
├── requirements.txt        # Dépendances Python
├── .gitignore             # Fichiers à ignorer par Git
├── README.md              # Ce fichier
│
├── database/              # Couche base de données
│   ├── __init__.py
│   ├── db_manager.py      # Gestionnaire SQLite avec triggers
│   └── models.py          # Modèles de données (dataclasses)
│
├── business/              # Couche logique métier
│   ├── __init__.py
│   ├── budget_manager.py
│   ├── contrat_manager.py
│   ├── bc_manager.py
│   ├── projet_manager.py
│   ├── client_manager.py
│   ├── contact_manager.py
│   ├── todo_manager.py
│   └── alert_manager.py
│
├── ui/                    # Interface utilisateur
│   ├── __init__.py
│   ├── main_window.py     # Fenêtre principale avec menu
│   ├── dashboard.py       # Tableau de bord
│   ├── budgets_view.py
│   ├── contrats_view.py
│   ├── bons_commande_view.py
│   ├── projets_view.py
│   ├── clients_view.py
│   ├── contacts_view.py
│   ├── todo_view.py
│   ├── sauvegarde_view.py
│   └── components/
│
├── utils/                 # Utilitaires
│   ├── __init__.py
│   ├── constants.py       # Constantes de l'application
│   ├── formatters.py      # Formateurs (montants, dates)
│   └── validators.py      # Validateurs (email, téléphone, etc.)
│
├── assets/                # Ressources (logos, images)
└── backups/               # Sauvegardes de la base de données
```

## 🗄️ Base de Données

L'application utilise SQLite avec les tables suivantes :
- **clients** : Gestion des clients
- **contacts** : Contacts associés aux clients
- **contrats** : Contrats avec alertes automatiques
- **budgets** : Budgets annuels par nature
- **bons_commande** : Bons de commande avec validation
- **projets** : Projets avec FAP et investissements
- **investissements_projets** : Investissements prévisionnels
- **contacts_sourcing** : Contacts pour le sourcing
- **todo_list** : Tâches à réaliser
- **sauvegardes** : Historique des sauvegardes

### Triggers Automatiques
- **update_budget_disponible** : Calcule automatiquement le montant disponible
- **imputer_bc_au_budget** : Impute le BC au budget lors de la validation

## 🎨 Interface Utilisateur

### Thème Dark
- Couleur principale : `#0d7377` (Turquoise foncé)
- Succès : `#4ecdc4` (Turquoise clair)
- Danger : `#ff6b6b` (Rouge)
- Warning : `#ffa500` (Orange)
- Fond : `#0a0a0a` et `#1a1a1a`

### Navigation
- Menu latéral gauche avec 9 sections
- Highlight du bouton actif
- Navigation fluide entre les vues

## 🔧 Technologies Utilisées

- **Python 3.10+** : Langage de programmation
- **CustomTkinter 5.2.1** : Interface graphique moderne
- **SQLite** : Base de données locale
- **Pillow** : Manipulation d'images
- **Matplotlib** : Graphiques (optionnel)
- **python-dateutil** : Gestion des dates

## 📊 Statistiques du Projet

- **29 fichiers Python**
- **~7,200 lignes de code**
- **11 tables de base de données**
- **8 managers métier**
- **10 vues UI**
- **Architecture MVC complète**

## 🛠️ Développement

### Lancer les tests
```bash
# Tester les imports et la base de données
python3 -c "
from database.db_manager import DatabaseManager
db = DatabaseManager('test.db')
db.initialize_database()
print('✅ Tests réussis')
"
```

### Code quality
- Docstrings pour toutes les classes et méthodes principales
- Gestion d'erreurs avec try-except
- Nommage explicite (snake_case)
- Séparation des couches (MVC)

## 📝 Licence

Ce projet est développé pour un usage interne. Tous droits réservés.

## 👤 Auteur

**ArnaudP17000**
- GitHub: [@ArnaudP17000](https://github.com/ArnaudP17000)

## 🤝 Contribution

Ce projet est actuellement maintenu par une seule personne. Les suggestions et améliorations sont les bienvenues via les issues GitHub.

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

---

**Version** : 1.0.0  
**Dernière mise à jour** : Février 2026  
**Statut** : ✅ Production Ready
