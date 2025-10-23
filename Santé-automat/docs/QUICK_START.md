# 🎯 Guide Rapide d'Utilisation

## ⚡ Démarrage rapide (30 secondes)

```bash
# 1. Vérifier l'installation
./check.sh

# 2. Lancer en mode développement
python main_new.py --dev --force

# 3. Consulter les détails
cat dev.txt
```

## 📋 Commandes essentielles

### Mode normal
```bash
python main_new.py
```
**Résultat :** Met à jour `resultats.xlsx` avec les nouveaux PDF

### Mode développement
```bash
python main_new.py --dev
```
**Résultat :** Crée `dev.txt` avec détails d'extraction

### Forcer la ré-extraction
```bash
python main_new.py --force
```
**Résultat :** Ré-extrait même si dates déjà présentes

### Combinaison (recommandé pour déboguer)
```bash
python main_new.py --dev --force
```
**Résultat :** Ré-extrait tout + crée dev.txt avec détails

## 🔍 Que contient dev.txt ?

### Structure du fichier

```
dev.txt
├── Banlist chargée (9 éléments)
├── Pour chaque PDF :
│   ├── Texte brut complet
│   ├── Date extraite
│   └── Résultats filtrés (détaillés)
```

### Exemple concret

```
================================================================================
  BANLIST CHARGÉE
================================================================================
Nombre d'éléments dans la banlist: 9
  - Dossier
  - Prélevé le
  - Le DFG estimé est considéré comme légèrement diminué entre
  [...]

================================================================================
  TEXTE BRUT DU PDF: 25M010055151.pdf
================================================================================
BIOGROUP MAINE ANJOU
Laboratoire LE PRE − CML
[... tout le contenu du PDF ...]

Date extraite pour 25M010055151.pdf: 01-10-2025

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

• Hématocrite:
    Valeur: 46.0 %
    Intervalle: 39−49

• Leucocytes:
    Valeur: 6.51 G/L
    Intervalle: 4,00−11,00

• Plaquettes:
    Valeur: 259.0 G/L
    Intervalle: 150−400

• Créatinine:
    Valeur: 87.0 µmol/L
    Intervalle: 53,0−97,0

[etc. pour les 15 paramètres]
```

## 🎯 Cas d'usage pratiques

### 1️⃣ Déboguer : "Pourquoi ce paramètre n'est pas extrait ?"

```bash
# Étape 1 : Générer dev.txt
python main_new.py --dev --force

# Étape 2 : Chercher dans le texte brut
grep -i "nom_du_parametre" dev.txt

# Étape 3 : Vérifier dans les résultats filtrés
grep -A 3 "RÉSULTATS FILTRÉS" dev.txt
```

**Solutions possibles :**
- Paramètre absent du texte brut → Problème dans le PDF
- Présent dans texte brut mais pas dans résultats → Ajouter à whitelist
- Bloqué par banlist → Ajuster banlist.txt

### 2️⃣ Ajouter un nouveau paramètre

```bash
# 1. Vérifier qu'il apparaît dans le PDF
python main_new.py --dev --force
grep -i "nouveau_parametre" dev.txt

# 2. Ajouter à la whitelist
nano config.py
# Ajouter "Nouveau Paramètre" dans PARAMS_WHITELIST

# 3. Ré-exécuter
python main_new.py --dev --force
```

### 3️⃣ Exclure des lignes indésirables

```bash
# 1. Identifier les lignes à exclure dans dev.txt
cat dev.txt | less

# 2. Ajouter à banlist.txt
echo "Texte à exclure" >> banlist.txt

# 3. Ré-exécuter
python main_new.py --dev --force
```

### 4️⃣ Vérifier les seuils

```bash
# Voir les seuils chargés
cat seuils.json

# Le script met à jour automatiquement les seuils
# depuis les intervalles détectés dans les PDF
```

## 📊 Résultats produits

### resultats.xlsx

```
Onglet 1: Données
┌────────────┬──────┬─────┬─────┬────────────┬────────────┐
│ Paramètre  │ Unité│ Min │ Max │ 29-08-2025 │ 01-10-2025 │
├────────────┼──────┼─────┼─────┼────────────┼────────────┤
│ Hématies   │ T/L  │ 4.28│ 6.00│ 5.05       │ 5.14       │
│ Hémoglobine│ g/dL │13.4 │16.7 │ 14.6       │ 14.9       │
│ ...        │      │     │     │            │            │
└────────────┴──────┴─────┴─────┴────────────┴────────────┘

Couleurs:
  🟢 Vert  = Valeur dans les normes
  🔴 Rouge = Valeur hors normes

Onglet 2: Graphiques
  📈 Un graphique d'évolution par paramètre
```

### dev.txt (en mode --dev)

```
• Banlist complète
• Texte brut de chaque PDF
• Dates extraites
• Résultats filtrés avec détails
```

## 🔧 Configuration

### Modifier la whitelist (paramètres à extraire)

Éditez `config.py` :
```python
PARAMS_WHITELIST = [
    "Hématies",
    "Hémoglobine",
    # ... paramètres existants
    "Nouveau Paramètre",  # ← Ajouter ici
]
```

### Modifier la banlist (lignes à exclure)

Éditez `banlist.txt` :
```
# Commentaire
Texte à exclure 1
Texte à exclure 2
```

### Modifier les seuils

Éditez `seuils.json` :
```json
{
  "Hémoglobine": {
    "min": 13.0,
    "max": 17.0
  },
  "Nouveau Paramètre": {
    "min": 10.0,
    "max": 20.0
  }
}
```

## 📚 Documentation complète

| Fichier | Contenu |
|---------|---------|
| **RECAP.md** | Résumé complet de la refactorisation |
| **ARCHITECTURE.md** | Diagrammes et architecture détaillée |
| **STRUCTURE.md** | Documentation technique des modules |
| **MIGRATION.md** | Guide de migration depuis l'ancien script |
| **QUICK_START.md** | Ce fichier (guide rapide) |

## 🆘 Problèmes courants

### ❌ "No module named 'xxx'"
```bash
# Solution : Installer les dépendances
pip install -r requirements.txt
```

### ❌ Paramètre non extrait
```bash
# 1. Vérifier avec --dev
python main_new.py --dev --force

# 2. Chercher dans dev.txt
grep -i "parametre" dev.txt

# 3. Ajouter à whitelist si nécessaire
```

### ❌ Date non détectée
```bash
# Vérifier le format de date dans dev.txt
# La regex cherche : "Prélevé le DD-MM-YYYY"
```

### ❌ Trop de lignes extraites
```bash
# Ajouter à banlist.txt les textes à exclure
```

## ✅ Checklist avant utilisation

- [ ] Modules créés (6 fichiers .py)
- [ ] Documentation créée (4 fichiers .md)
- [ ] Tests passent (`python test_modules.py`)
- [ ] Vérification OK (`./check.sh`)
- [ ] PDF présents dans `pdfs/`
- [ ] Configuration OK (`.env`, `seuils.json`, `banlist.txt`)

## 🎓 Pour aller plus loin

1. **Tests unitaires**
   ```bash
   python test_modules.py
   ```

2. **Voir l'architecture**
   ```bash
   cat ARCHITECTURE.md
   ```

3. **Comprendre chaque module**
   ```bash
   cat STRUCTURE.md
   ```

4. **Migration complète**
   ```bash
   cat MIGRATION.md
   ```

---

**🚀 Vous êtes prêt !**

Commencez par :
```bash
python main_new.py --dev --force
cat dev.txt
```
