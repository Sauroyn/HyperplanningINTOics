# 🏥 Santé-automat

Analyseur automatique de résultats médicaux depuis des fichiers PDF vers Excel.

## 📁 Structure du projet

```
Santé-automat/
├── 📄 main_new.py          # Point d'entrée principal
├── 📂 src/                 # Modules Python
│   ├── config.py           # Configuration globale
│   ├── dev_logger.py       # Mode développement
│   ├── pdf_extractor.py    # Extraction PDF
│   ├── thresholds_manager.py  # Gestion des seuils
│   └── excel_manager.py    # Gestion Excel
├── 📂 docs/                # Documentation
│   ├── QUICK_START.md      # ⭐ Guide rapide (commencez ici)
│   ├── RECAP.md            # Résumé complet
│   ├── ARCHITECTURE.md     # Diagrammes
│   ├── STRUCTURE.md        # Doc technique
│   └── MIGRATION.md        # Guide migration
├── 📂 scripts/             # Utilitaires
│   ├── check.sh            # Vérification installation
│   ├── demo.sh             # Démonstration
│   └── test_modules.py     # Tests unitaires
├── 📂 archive/             # Anciens fichiers
├── 📂 pdfs/                # PDF à analyser
├── 📊 resultats.xlsx       # Résultats générés
├── ⚙️ .env                 # Variables d'environnement
├── 📋 banlist.txt          # Lignes à exclure
├── 📊 seuils.json          # Seuils de référence
└── 📦 requirements.txt     # Dépendances Python
```

## 🚀 Démarrage rapide

### 1. Installation
```bash
# Installer les dépendances
pip install -r requirements.txt
```

### 2. Vérification
```bash
# Vérifier que tout fonctionne
./scripts/check.sh
```

### 3. Utilisation
```bash
# Mode normal
python main_new.py

# Mode développement (recommandé)
python main_new.py --dev

# Forcer la ré-extraction
python main_new.py --force
```

## 📖 Documentation

**🌟 Commencez ici :** [docs/QUICK_START.md](docs/QUICK_START.md)

Autres guides :
- **RECAP.md** - Vue d'ensemble complète
- **ARCHITECTURE.md** - Diagrammes et architecture
- **STRUCTURE.md** - Documentation technique
- **MIGRATION.md** - Migration depuis l'ancien script

## 🎯 Mode développement (`--dev`)

Active le mode développement qui crée un fichier `dev.txt` contenant :
- ✓ Texte brut extrait de chaque PDF
- ✓ Date de prélèvement détectée
- ✓ Résultats après filtrage (whitelist/banlist)

**Utilité :** Déboguer l'extraction et comprendre ce que le script voit.

```bash
python main_new.py --dev --force
cat dev.txt
```

## 📊 Résultats produits

### resultats.xlsx
- **Onglet 1 :** Données avec colorisation (🟢 vert = normal, 🔴 rouge = hors normes)
- **Onglet 2 :** Graphiques d'évolution par paramètre

### dev.txt (si mode --dev)
- Texte brut des PDF
- Détails de l'extraction
- Résultats filtrés

## ⚙️ Configuration

### Paramètres à extraire
Éditez `src/config.py` → `PARAMS_WHITELIST`

### Lignes à exclure
Éditez `banlist.txt`

### Seuils de référence
Éditez `seuils.json`

## 🧪 Tests

```bash
# Tests unitaires
python scripts/test_modules.py

# Vérification complète
./scripts/check.sh
```

## 🆘 Support

Consultez la documentation complète dans le dossier `docs/`.

Pour déboguer un problème :
1. Lancez avec `--dev`
2. Consultez `dev.txt`
3. Vérifiez la configuration (whitelist/banlist/seuils)

## 📝 Licence

Usage personnel - Analyse de résultats médicaux

---

**Version :** 2.0.0 - Architecture modulaire avec mode développement
