# 🔄 Guide de Migration

## ✅ Ce qui a été fait

Le script `main.py` a été **refactorisé en 6 modules** pour améliorer la maintenabilité et ajouter le mode développement.

### Nouveaux fichiers créés

| Fichier | Description |
|---------|-------------|
| `config.py` | Configuration globale (chemins, constantes, whitelist) |
| `dev_logger.py` | Gestionnaire de logs pour le mode `--dev` |
| `pdf_extractor.py` | Extraction et parsing des PDF |
| `thresholds_manager.py` | Gestion des seuils min/max |
| `excel_manager.py` | Mise à jour Excel, colorisation, graphiques |
| `main_new.py` | **Nouveau point d'entrée** principal |

### Fichiers conservés

- `main.py` - **Ancien script** (conservé pour référence)
- Tous vos autres fichiers (`.env`, `seuils.json`, `banlist.txt`, etc.)

## 🚀 Utilisation immédiate

### Option 1 : Utiliser le nouveau script directement

```bash
# Mode normal
python main_new.py

# Mode développement (crée dev.txt avec détails)
python main_new.py --dev

# Forcer la ré-extraction
python main_new.py --force

# Combiner les deux
python main_new.py --dev --force
```

### Option 2 : Remplacer l'ancien script

Si vous voulez que `main.py` utilise la nouvelle structure :

```bash
# Sauvegarder l'ancien
mv main.py main_old.py

# Renommer le nouveau
mv main_new.py main.py

# Utiliser comme avant
python main.py --dev
```

## 📊 Nouveau : Mode Développement (`--dev`)

Quand vous lancez avec `--dev`, un fichier **`dev.txt`** est créé contenant :

### 1. Banlist chargée
```
================================================================================
  BANLIST CHARGÉE
================================================================================

Nombre d'éléments dans la banlist: 9
  - Dossier
  - Prélevé le
  - Le DFG estimé est considéré comme légèrement diminué entre
  ...
```

### 2. Texte brut du PDF
```
================================================================================
  TEXTE BRUT DU PDF: 25M010055151.pdf
================================================================================

BIOGROUP MAINE ANJOU
Laboratoire LE PRE − CML
11 AVENUE LAENNEC − 72000 LE MANS
[Tout le contenu extrait du PDF]
```

### 3. Date extraite
```
Date extraite pour 25M010055151.pdf: 01-10-2025
```

### 4. Résultats après filtrage
```
================================================================================
  RÉSULTATS FILTRÉS POUR: 25M010055151.pdf
================================================================================

Nombre de paramètres retenus: 15

• Hématies:
    Valeur: 5.14 T/L
    Intervalle: 4,28−6,00

• Hémoglobine:
    Valeur: 14.9 g/dL
    Intervalle: 13,4−16,7
    
[etc. pour chaque paramètre retenu]
```

## 🎯 Cas d'utilisation du mode `--dev`

### Déboguer l'extraction
Si un paramètre n'est pas détecté :
1. Lancez `python main_new.py --dev --force`
2. Ouvrez `dev.txt`
3. Cherchez le texte brut du PDF
4. Vérifiez si le paramètre apparaît dans le texte brut
5. Comparez avec les résultats filtrés pour voir s'il a été rejeté

### Ajuster la banlist
Si trop de lignes sont extraites :
1. Regardez les résultats filtrés dans `dev.txt`
2. Identifiez les lignes indésirables
3. Ajoutez-les à `banlist.txt`
4. Relancez avec `--dev --force`

### Vérifier la whitelist
Si un paramètre légitime est rejeté :
1. Vérifiez qu'il est dans la whitelist (`config.py` ligne 12-21)
2. Ajoutez-le si nécessaire
3. Relancez

## 🔧 Personnalisation

### Modifier la whitelist
Éditez `config.py` :
```python
PARAMS_WHITELIST = [
    "Hématies", "Hémoglobine", # ... existants
    "Nouveau Paramètre",  # Ajouter ici
]
```

### Changer le nom du fichier de log
Éditez `main_new.py`, ligne 36 :
```python
dev_logger = DevLogger(enabled=args.dev, log_file="mon_log.txt")
```

### Modifier les couleurs Excel
Éditez `excel_manager.py`, lignes 99-100 :
```python
green = PatternFill(start_color="AAFFAA", ...)  # Vert clair
red = PatternFill(start_color="FFAAAA", ...)    # Rouge clair
```

## 📦 Structure du code

```
Santé-automat/
├── config.py                 # ⚙️  Configuration
├── dev_logger.py             # 📝 Logs dev
├── pdf_extractor.py          # 📄 Extraction PDF
├── thresholds_manager.py     # 📊 Gestion seuils
├── excel_manager.py          # 📈 Gestion Excel
├── main_new.py               # 🚀 Point d'entrée
├── main.py                   # 🗂️  Ancien script (conservé)
├── .env                      # Variables d'environnement
├── seuils.json               # Seuils de référence
├── banlist.txt               # Éléments à exclure
├── requirements.txt          # Dépendances Python
└── pdfs/                     # Dossier des PDF
```

## 🆘 Résolution de problèmes

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Les dates ne sont pas détectées
Vérifiez dans `dev.txt` le format de date dans le texte brut.

### Paramètres manquants
1. Vérifiez `dev.txt` → section "TEXTE BRUT"
2. Vérifiez s'il est dans la whitelist (`config.py`)
3. Vérifiez s'il n'est pas dans la banlist (`banlist.txt`)

### Le fichier Excel n'est pas créé
Vérifiez les permissions d'écriture dans le dossier.

## ✨ Avantages de la refactorisation

✅ **Modularité** : Chaque composant a une responsabilité unique  
✅ **Débogage** : Mode `--dev` pour voir ce qui se passe  
✅ **Maintenabilité** : Code plus court et plus clair  
✅ **Testabilité** : Chaque module peut être testé séparément  
✅ **Réutilisabilité** : Les modules peuvent être importés ailleurs  
✅ **Documentation** : Docstrings dans chaque module  

## 📞 Questions ?

Consultez les fichiers :
- `STRUCTURE.md` - Documentation détaillée de la structure
- `demo.sh` - Script de démonstration
- `dev.txt` - Logs de la dernière exécution en mode `--dev`
