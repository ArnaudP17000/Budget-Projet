# 📦 Guide de Compilation - Budget-Projet

Ce guide explique comment compiler l'application Budget-Projet en fichier exécutable Windows (.exe) en utilisant auto-py-to-exe.

## 🔧 Prérequis

Avant de commencer, assurez-vous d'avoir :
- Python 3.8+ installé
- Toutes les dépendances du projet installées
- Le projet cloné localement

## 📥 Installation des outils de compilation

```powershell
# Installer auto-py-to-exe
pip install auto-py-to-exe

# Ou installer PyInstaller directement
pip install pyinstaller
```

## 🚀 Compilation avec auto-py-to-exe

### Étape 1 : Lancer l'interface

```powershell
auto-py-to-exe
```

Une interface web s'ouvrira dans votre navigateur (http://localhost:5000).

### Étape 2 : Configuration de base

#### Script Location
- Cliquez sur **"Browse"**
- Sélectionnez : `main.py` à la racine du projet

#### One Directory or One File
- Sélectionnez : **"One Directory"** (recommandé)
  - Plus rapide au démarrage
  - Plus fiable pour les applications GUI

#### Console Window
- Sélectionnez : **"Window Based (hide the console)"**
  - Pas de console noire en arrière-plan

#### Icon (Optionnel)
- Ajoutez un fichier `.ico` si vous en avez un
- Sinon, laissez vide (icône Python par défaut)

### Étape 3 : Options avancées (IMPORTANT !)

#### Hidden Imports
Copiez-collez cette ligne dans le champ "Hidden Imports" :

```
customtkinter,PIL,PIL._tkinter_finder,PIL.Image,PIL.ImageTk,openpyxl,openpyxl.styles,tkinter,tkinter.ttk,tkinter.filedialog,tkinter.messagebox,sqlite3,dataclasses,datetime,typing,contextlib,traceback,sys,os,re,shutil,pathlib
```

#### Collect All / --collect-all
Ajoutez ces modules :

```
customtkinter,openpyxl,PIL
```

#### Additional Files
Ajoutez ces 4 dossiers (cliquez sur "+ Add Folder" pour chacun) :

| From | To |
|------|-----|
| `database` | `database` |
| `business` | `business` |
| `ui` | `ui` |
| `utils` | `utils` |

**⚠️ NE PAS inclure :**
- ❌ Le dossier `data/` (sera créé automatiquement)
- ❌ Les fichiers `.db`
- ❌ Le dossier `__pycache__`
- ❌ Le dossier `.git`

### Étape 4 : Compilation

1. Faites défiler tout en bas
2. Cliquez sur **"CONVERT .PY TO .EXE"**
3. Attendez 5-10 minutes (la compilation peut être longue)
4. Quand vous voyez "✅ Complete!", c'est terminé !

## 📂 Récupération de l'exécutable

Votre application compilée se trouve dans :
```
output/Budget-Projet/
├── Budget-Projet.exe         ← Exécutable principal
├── _internal/                 ← Bibliothèques (OBLIGATOIRE)
├── database/                  ← Code de l'app (OBLIGATOIRE)
├── business/                  ← Code de l'app (OBLIGATOIRE)
├── ui/                        ← Code de l'app (OBLIGATOIRE)
└── utils/                     ← Code de l'app (OBLIGATOIRE)
```

## 🧪 Test de l'exécutable

```powershell
cd output\Budget-Projet
.\Budget-Projet.exe
```

Vérifications :
- ✅ L'application démarre sans erreur
- ✅ Un dossier `data/` est créé automatiquement
- ✅ Le fichier `data/budget_projet.db` est créé
- ✅ Toutes les vues fonctionnent correctement

## 📦 Distribution

### Créer un fichier ZIP

```powershell
cd output
Compress-Archive -Path "Budget-Projet" -DestinationPath "Budget-Projet-v1.0.zip"
```

### Instructions pour les utilisateurs finaux

1. **Extraire** le fichier ZIP complet
2. **Ouvrir** le dossier `Budget-Projet`
3. **Double-cliquer** sur `Budget-Projet.exe`
4. Au premier lancement, un dossier `data/` sera créé avec la base de données

**⚠️ Important :** Les utilisateurs doivent conserver **TOUT le dossier**, pas seulement le .exe !

## 🔄 Alternative : Compilation en ligne de commande

Si vous préférez la ligne de commande, utilisez ce script :

```powershell
pyinstaller --name="Budget-Projet" `
    --onedir `
    --windowed `
    --hidden-import=customtkinter `
    --hidden-import=PIL `
    --hidden-import=openpyxl `
    --hidden-import=tkinter `
    --hidden-import=sqlite3 `
    --collect-all customtkinter `
    --add-data="database;database" `
    --add-data="business;business" `
    --add-data="ui;ui" `
    --add-data="utils;utils" `
    main.py
```

L'exécutable sera dans `dist/Budget-Projet/`

## ⚠️ Problèmes courants

### Erreur "Module not found"
**Solution :** Ajoutez le module manquant dans "Hidden Imports"

### L'exe ne démarre pas
**Solution :** Changez temporairement en "Console Based" pour voir les erreurs

### Antivirus bloque l'exe
**Solution :** Ajoutez une exception dans votre antivirus (faux positif courant avec PyInstaller)

### Erreur "Failed to execute script"
**Solution :** Vérifiez que tous les dossiers sont dans "Additional Files"

## 📊 Informations techniques

- **Taille approximative :** 150-250 MB (mode "One Directory")
- **Temps de compilation :** 5-10 minutes
- **Temps de démarrage :** 2-5 secondes
- **Python requis pour l'utilisateur :** ❌ NON (tout est inclus)

## 🎯 Notes importantes

1. **Base de données individuelle :** Chaque utilisateur aura sa propre base de données dans le dossier `data/`
2. **Pas d'installation requise :** L'application est portable
3. **Sauvegarde :** Les utilisateurs peuvent sauvegarder leur `data/budget_projet.db`
4. **Mises à jour :** Pour mettre à jour, remplacez tout le dossier sauf `data/`

## 📝 Version

- **Version de l'application :** v1.0.0
- **Date de création :** 2026-02-15
- **Compilé avec :** PyInstaller (via auto-py-to-exe)

## 🆘 Support

En cas de problème lors de la compilation, vérifiez :
1. Que toutes les dépendances sont installées : `pip install -r requirements.txt`
2. Que vous êtes dans le bon répertoire (racine du projet)
3. Que Python 3.8+ est utilisé : `python --version`
4. Les logs de compilation dans l'interface auto-py-to-exe

---

**Compilation réussie avec succès ! 🎉**