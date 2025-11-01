# 🔍 Guide d'utilisation du script de diagnostic

Ce script permet d'analyser en détail comment pdfplumber extrait les tableaux de vos liasses fiscales et d'identifier les problèmes potentiels.

## 📋 Utilisation

### Commande de base

```bash
python diagnostic_extraction.py chemin/vers/votre_liasse.pdf
```

### Exemples

```bash
# Analyser une liasse dans le dossier liasse/
python diagnostic_extraction.py liasse/liasse_2024.pdf

# Analyser une liasse vierge
python diagnostic_extraction.py liasse/liasse_vierge.pdf

# Sauvegarder les résultats dans un fichier
python diagnostic_extraction.py liasse/liasse_2024.pdf > diagnostic_2024.txt
```

## 📊 Ce que le diagnostic affiche

Pour chaque formulaire (Actif, Passif, Compte de Résultat, Échéances, Affectation), le script affiche:

### 1. Informations générales
- Nombre de lignes extraites
- Nombre de colonnes détectées

### 2. Tableau brut
- Les 10 premières lignes du tableau tel qu'extrait par pdfplumber
- Permet de voir la structure exacte des données

### 3. Colonnes numériques
- Liste des colonnes contenant des nombres
- Position de la 1ère, 2ème, 3ème colonne numérique

### 4. Recherche des codes fiscaux
- Nombre de codes attendus vs trouvés
- Position exacte de chaque code trouvé (ligne, colonne)
- Ligne complète où le code apparaît

### 5. Cellules courtes
- Si aucun code n'est trouvé, affiche toutes les cellules courtes (≤4 caractères)
- Permet de comparer avec les codes attendus et identifier les différences

### 6. En-têtes des colonnes
- Contenu de la première ligne (en-tête du tableau)

## 🎯 Cas d'usage

### Cas 1: Comprendre pourquoi les codes ne sont pas détectés

```bash
python diagnostic_extraction.py liasse/ma_liasse.pdf
```

Regardez la section "Recherche des codes fiscaux":
- Si "Codes trouvés: 0/X" → Les codes ne sont pas extraits correctement
- Vérifiez "Cellules courtes trouvées" pour voir ce qui est réellement extrait
- Comparez avec les codes attendus (DA, DL, DM, etc.)

### Cas 2: Vérifier la détection des colonnes numériques

Regardez la section "Détection des colonnes numériques":
- Pour l'Actif: doit trouver au moins 3 colonnes (Brut, Amort, Net)
- Pour le Passif: doit trouver au moins 1 colonne (Exercice N)

### Cas 3: Comparer plusieurs PDF

Exécutez le diagnostic sur plusieurs liasses pour identifier les variations:

```bash
python diagnostic_extraction.py liasse/liasse_A.pdf > diagnostic_A.txt
python diagnostic_extraction.py liasse/liasse_B.pdf > diagnostic_B.txt
python diagnostic_extraction.py liasse/liasse_vierge.pdf > diagnostic_vierge.txt

# Comparer les fichiers
diff diagnostic_A.txt diagnostic_B.txt
```

## 🐛 Problèmes courants identifiés par le diagnostic

### Problème 1: "Aucune colonne numérique détectée"
**Cause**: Les montants ne sont pas reconnus comme des nombres
**Solution**: Vérifier le format des montants dans le PDF (espaces, virgules, etc.)

### Problème 2: "AUCUN CODE TROUVÉ"
**Causes possibles**:
- Les codes sont fusionnés avec d'autres cellules (ex: "DA Capital" au lieu de "DA")
- Les codes ont des espaces (ex: "D A" au lieu de "DA")
- Les codes sont dans un format non standard
- Le tableau est mal extrait par pdfplumber (fusion de cellules)

**Solution**: Regardez "Cellules courtes trouvées" et "Les 10 premières lignes du tableau brut"

### Problème 3: "Codes trouvés: 2/30"
**Cause**: Seulement quelques codes sont détectés
**Solution**: Comparez les codes trouvés vs non trouvés pour identifier le pattern

### Problème 4: "Impossible de trouver la 3ème colonne numérique"
**Cause**: Le Bilan Actif a moins de 3 colonnes numériques
**Solution**:
- Vérifiez si le PDF contient bien Brut, Amort, Net
- Ou si certaines colonnes sont vides (et donc non détectées comme numériques)

## 📝 Exemples de sortie

### Exemple 1: Extraction réussie

```
================================================================================
  DIAGNOSTIC: BILAN PASSIF (2051)
================================================================================

📊 Informations générales:
   - Nombre de lignes: 45
   - Nombre de colonnes (max): 12

🔢 Détection des colonnes numériques:
   - Colonnes numériques détectées: [9, 10]
   - 1ère colonne numérique: index 9

🔍 Recherche des codes fiscaux attendus:
   - Codes attendus: 30 codes
   ✅ Codes trouvés: 28/30

   📍 Détails des codes trouvés:
      - DA (Capital social ou individuel)
        Position: ligne 5, colonne 2
        Ligne complète: ['', '', 'DA', 'Capital social...', '100000', ...]
```

### Exemple 2: Problème détecté

```
================================================================================
  DIAGNOSTIC: BILAN ACTIF (2050)
================================================================================

📊 Informations générales:
   - Nombre de lignes: 50
   - Nombre de colonnes (max): 8

🔢 Détection des colonnes numériques:
   - Colonnes numériques détectées: [4, 5]
   ⚠️ Impossible de trouver la 3ème colonne numérique!

🔍 Recherche des codes fiscaux attendus:
   - Codes attendus: 40 codes
   ❌ Codes trouvés: 0/40

   ❌ AUCUN CODE TROUVÉ!

   🔍 Analyse des cellules (20 premières lignes):
      Cellules courtes trouvées: ['1', '2', 'A', 'AB', 'BIS', 'CD', 'N', 'X']
```

## 💡 Conseils d'utilisation

1. **Testez d'abord avec une liasse vierge** (formulaire officiel vide)
   - Cela établit une référence de base

2. **Testez avec plusieurs liasses réelles**
   - Identifiez les variations entre différents PDFs

3. **Sauvegardez les résultats**
   - Utilisez `> diagnostic_xxx.txt` pour garder une trace

4. **Comparez les diagnostics**
   - Identifiez ce qui fonctionne vs ce qui échoue

5. **Partagez les résultats**
   - Si vous avez besoin d'aide, partagez le fichier diagnostic_xxx.txt

## 🔧 Prochaines étapes après le diagnostic

Selon les résultats, nous pourrons:
1. Ajuster la logique de détection des codes
2. Améliorer la normalisation des codes (gestion des espaces, etc.)
3. Adapter la détection des colonnes numériques
4. Ajouter des stratégies de fallback pour les PDF mal structurés
