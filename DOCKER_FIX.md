# 🐛 Correction du fichier docker-compose.yml

## Problème identifié

Le fichier `docker-compose.yml` contenait une **incohérence de configuration** entre les services `nginx` et `db`.

### ❌ Configuration incorrecte (avant)

Le service **nginx** tentait de se connecter avec :
- `DB_MYSQL_USER: "admin"`
- `DB_MYSQL_PASSWORD: "Admin77123$"`

Mais le service **db** créait un utilisateur avec :
- `MYSQL_USER: 'SqlManager'`
- `MYSQL_PASSWORD: 'UserSql77123$'`

### ⚠️ Conséquence

Les identifiants ne correspondaient pas, ce qui empêchait le service **nginx-proxy-manager** de se connecter à la base de données MariaDB.

## ✅ Solution appliquée

Les identifiants du service **nginx** ont été corrigés pour correspondre à ceux du service **db** :

```yaml
nginx:
  environment:
    DB_MYSQL_USER: "SqlManager"      # ✅ Correspond à MYSQL_USER
    DB_MYSQL_PASSWORD: "UserSql77123$"  # ✅ Correspond à MYSQL_PASSWORD
```

**Autres améliorations** :
- Suppression du champ `version: '3'` obsolète (recommandation Docker Compose moderne)
- Le fichier suit maintenant le format Compose Specification actuel

## 🚀 Utilisation

Pour lancer les services avec Docker Compose :

```bash
docker-compose up -d
```

Pour vérifier que les services fonctionnent :

```bash
docker-compose ps
docker-compose logs nginx
docker-compose logs db
```

## 📝 Notes

- Les ports **80** et **443** ne doivent pas être modifiés (utilisés pour HTTP/HTTPS)
- Le port **81** est utilisé pour l'interface d'administration de nginx-proxy-manager
- Pensez à modifier les mots de passe en production pour des valeurs plus sécurisées
- Les volumes sont montés dans `/docker/ngxmanager/` pour la persistance des données

## 🔐 Sécurité

⚠️ **Important** : Les mots de passe actuels sont des exemples. En production :
1. Utilisez des mots de passe forts et uniques
2. Stockez les secrets dans des variables d'environnement ou un vault
3. Ne commitez jamais de secrets dans Git

---

**Date de correction** : Février 2026  
**Auteur** : ArnaudP17000
