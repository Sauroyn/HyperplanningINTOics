# Structure Modulaire du Projet

## 📁 Organisation des fichiers

Le script a été refactorisé en plusieurs modules pour une meilleure maintenabilité :

### Modules principaux

- **`config.py`** : Configuration et constantes globales
  - Chemins des fichiers (PDF, Excel, seuils, banlist)
  - Liste blanche des paramètres biologiques

- **`dev_logger.py`** : Gestionnaire de logs pour le mode développement
  - Enregistre le texte brut des PDF
  - Enregistre les résultats après filtrage
  - Écrit dans `dev.txt`

- **`pdf_extractor.py`** : Extraction des données depuis les PDF
  - Parsing des fichiers PDF avec pdfplumber
  - Extraction de la date de prélèvement
  - Filtrage selon la whitelist et la banlist
  - Support du mode développement

- **`thresholds_manager.py`** : Gestion des seuils de référence
  - Chargement depuis JSON ou Excel
  - Sauvegarde automatique
  - Mise à jour depuis les intervalles détectés dans les PDF

- **`excel_manager.py`** : Gestion du fichier Excel
  - Mise à jour des données
  - Colorisation des valeurs hors normes (vert/rouge)
  - Génération des graphiques d'évolution

- **`main_new.py`** : Point d'entrée principal
  - Orchestre tous les modules
  - Gestion des arguments en ligne de commande
  - Traitement séquentiel des PDF

## 🚀 Utilisation

### Mode normal
```bash
python main_new.py
```

### Mode développement (avec logs détaillés)
```bash
python main_new.py --dev
```
Génère un fichier `dev.txt` contenant :
- Le texte brut extrait de chaque PDF
- La date détectée
- Les résultats filtrés après application de la whitelist/banlist
- Le nombre de paramètres retenus

### Forcer la ré-extraction
```bash
python main_new.py --force
```

### Combiner les options
```bash
python main_new.py --dev --force
```

## 📊 Fichier dev.txt

En mode `--dev`, le fichier contient :

```
=== MODE DÉVELOPPEMENT - 2025-10-23 14:30:00 ===

================================================================================
  BANLIST CHARGÉE
================================================================================

Nombre d'éléments dans la banlist: X
  - élément1
  - élément2
  ...

================================================================================
  TEXTE BRUT DU PDF: fichier.pdf
================================================================================

[Tout le texte extrait du PDF]

Date extraite pour fichier.pdf: 01-01-2025

================================================================================
  RÉSULTATS FILTRÉS POUR: fichier.pdf
================================================================================

Nombre de paramètres retenus: 15

• Hématies:
    Valeur: 5.2 T/L
    Intervalle: 4.5-5.9
    Min: 4.5, Max: 5.9

• Hémoglobine:
    Valeur: 15.3 g/dL
    Intervalle: 13.0-17.0
    Min: 13.0, Max: 17.0

[etc.]
```

## 🔄 Migration depuis l'ancien script

L'ancien `main.py` est conservé. Pour utiliser la nouvelle version :

```bash
# Renommer l'ancien (optionnel)
mv main.py main_old.py

# Renommer le nouveau
mv main_new.py main.py
```

Ou simplement utiliser directement `main_new.py`.

## 🎯 Avantages de la structure modulaire

1. **Séparation des responsabilités** : Chaque module a un rôle clairement défini
2. **Testabilité** : Chaque module peut être testé indépendamment
3. **Maintenabilité** : Plus facile de localiser et corriger les bugs
4. **Réutilisabilité** : Les modules peuvent être importés dans d'autres scripts
5. **Lisibilité** : Code plus court et plus clair dans chaque fichier
6. **Mode développement** : Facilite le débogage avec `--dev`
