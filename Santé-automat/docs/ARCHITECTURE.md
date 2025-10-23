# 🏗️ Architecture du Projet

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                      main_new.py                            │
│                  (Point d'entrée principal)                 │
│                                                             │
│  • Parse les arguments (--dev, --force)                    │
│  • Orchestre tous les modules                              │
│  • Affiche les messages de progression                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ importe et utilise
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐      ┌──────────────┐
│  config.py   │      │dev_logger.py │
│              │      │              │
│ • PDF_FOLDER │      │ • log_raw    │
│ • OUTPUT_FILE│      │ • log_filter │
│ • WHITELIST  │      │ → dev.txt    │
└──────────────┘      └──────────────┘
        │                     │
        │ utilisé par         │ optionnel
        │                     │
        ▼                     ▼
┌─────────────────────────────────────────┐
│         pdf_extractor.py                │
│                                         │
│  • Charge banlist.txt                  │
│  • Extrait texte brut avec pdfplumber │
│  • Parse la date de prélèvement       │
│  • Filtre selon whitelist/banlist     │
│  • Log en mode --dev                  │
└────────────┬────────────────────────────┘
             │
             │ retourne (date, results)
             │
             ▼
┌─────────────────────────────────────────┐
│      thresholds_manager.py              │
│                                         │
│  • Charge seuils.json                  │
│  • Met à jour depuis PDF               │
│  • Sauvegarde automatique              │
│  • Fournit min/max par paramètre       │
└────────────┬────────────────────────────┘
             │
             │ utilisé par
             │
             ▼
┌─────────────────────────────────────────┐
│         excel_manager.py                │
│                                         │
│  • Met à jour resultats.xlsx           │
│  • Réordonne colonnes par date         │
│  • Colorise (vert/rouge)               │
│  • Génère graphiques (onglet séparé)   │
└─────────────────────────────────────────┘
             │
             │ produit
             │
             ▼
      ┌─────────────┐
      │resultats.xlsx│
      │             │
      │ Onglet 1:   │
      │  Données    │
      │  colorisées │
      │             │
      │ Onglet 2:   │
      │  Graphiques │
      └─────────────┘
```

## Flux de données

```
📄 PDF files (pdfs/)
    │
    │ [1] PDFExtractor lit chaque PDF
    │
    ├─→ Texte brut extrait
    │   │
    │   ├─→ 🔍 Mode --dev : écrit dans dev.txt
    │   │
    │   └─→ Parse date + résultats
    │       │
    │       ├─→ Filtre avec WHITELIST
    │       ├─→ Exclut avec banlist.txt
    │       │
    │       └─→ Résultats filtrés
    │           │
    │           └─→ 🔍 Mode --dev : écrit dans dev.txt
    │
    ├─→ [2] ThresholdsManager
    │   │
    │   ├─→ Lit seuils.json
    │   ├─→ Met à jour avec intervalles du PDF
    │   └─→ Sauvegarde seuils.json
    │
    └─→ [3] ExcelManager
        │
        ├─→ Lit resultats.xlsx (si existe)
        ├─→ Ajoute nouvelle colonne (date)
        ├─→ Réordonne colonnes chronologiquement
        ├─→ Colorise avec seuils (vert/rouge)
        ├─→ Génère graphiques d'évolution
        └─→ Sauvegarde resultats.xlsx

📊 resultats.xlsx (mis à jour)
📝 dev.txt (si --dev activé)
```

## Diagramme de dépendances

```
                    ┌─────────────┐
                    │   main.py   │
                    │  (ANCIEN)   │
                    │             │
                    │ Monolithique│
                    │  ~400 lignes│
                    └─────────────┘
                          │
                          │ REFACTORING
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │                                     │
        │    main_new.py (50 lignes)        │
        │                                     │
        └──┬───────┬────────┬─────────┬──────┘
           │       │        │         │
           │       │        │         │
    ┌──────▼─┐  ┌─▼──────┐┌▼────────┐┌▼──────────┐
    │config  │  │dev_    ││pdf_     ││thresholds_│
    │.py     │  │logger  ││extractor││manager.py │
    │        │  │.py     ││.py      ││           │
    │25 lines│  │80 lines││95 lines ││85 lines   │
    └────────┘  └────────┘└─────────┘└───────────┘
                                │
                                │
                        ┌───────▼────────┐
                        │excel_manager.py│
                        │                │
                        │   215 lines    │
                        └────────────────┘

TOTAL: ~550 lignes (vs 400 lignes monolithiques)
BUT: Modularité, testabilité, mode --dev
```

## Mode développement (--dev)

```
$ python main_new.py --dev --force

┌─────────────────────────────────────┐
│      Initialisation                 │
│                                     │
│  ✓ DevLogger activé                │
│  ✓ Charge banlist.txt              │
│  ✓ Charge seuils.json              │
└────────────┬────────────────────────┘
             │
             │ Pour chaque PDF
             │
    ┌────────▼─────────┐
    │ Extraction PDF   │
    │                  │
    │ ↓ Texte brut     │  ─────→ dev.txt
    │ ↓ Date           │  ─────→ dev.txt
    │ ↓ Parse          │
    │ ↓ Filtre         │
    │ ↓ Résultats      │  ─────→ dev.txt
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ Mise à jour      │
    │                  │
    │ ↓ Excel          │
    │ ↓ Seuils         │
    │ ↓ Colorisation   │
    │ ↓ Graphiques     │
    └──────────────────┘
             │
             ▼
    ┌─────────────────┐
    │   Résultats     │
    │                 │
    │ • resultats.xlsx│
    │ • dev.txt       │ ← NOUVEAU !
    └─────────────────┘
```

## Contenu de dev.txt

```
=== MODE DÉVELOPPEMENT - 2025-10-23 17:17:41 ===

┌────────────────────────────────────────────┐
│ Section 1 : BANLIST CHARGÉE                │
│                                            │
│ • Nombre d'éléments : 9                    │
│ • Liste complète des exclusions           │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Section 2 : TEXTE BRUT DU PDF              │
│                                            │
│ [Tout le contenu extrait du PDF]          │
│ → Permet de voir ce que voit le script    │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Section 3 : DATE EXTRAITE                  │
│                                            │
│ Date extraite : 01-10-2025                 │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Section 4 : RÉSULTATS FILTRÉS              │
│                                            │
│ Nombre de paramètres : 15                  │
│                                            │
│ • Hématies: 5.14 T/L (4,28−6,00)          │
│ • Hémoglobine: 14.9 g/dL (13,4−16,7)      │
│ • Hématocrite: 46.0 % (39−49)             │
│ • ...                                      │
│                                            │
│ → Permet de voir ce qui a été retenu      │
└────────────────────────────────────────────┘

[Répété pour chaque PDF traité]
```

## Comparaison Avant/Après

### AVANT (main.py)
```
┌─────────────────────────────────────┐
│         main.py                     │
│                                     │
│  [Tout le code dans un fichier]    │
│                                     │
│  • Difficile à maintenir            │
│  • Pas de visibilité sur l'extract.│
│  • Débogage difficile               │
│  • Code mélangé                     │
└─────────────────────────────────────┘
```

### APRÈS (Structure modulaire)
```
┌─────────────────────────────────────┐
│    Modules séparés + --dev          │
│                                     │
│  ✅ Code organisé par fonction      │
│  ✅ Mode --dev pour voir extraction │
│  ✅ Facile à déboguer avec dev.txt  │
│  ✅ Modules réutilisables           │
│  ✅ Tests unitaires possibles       │
└─────────────────────────────────────┘
```

## Utilisation rapide

```bash
# 🔍 Voir ce que le script extrait et retient
python main_new.py --dev --force

# 📖 Consulter les détails
cat dev.txt

# 📊 Voir les résultats
libreoffice resultats.xlsx
```
