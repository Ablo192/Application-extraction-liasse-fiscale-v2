# Approche Analytique v2.0 - Extraction de Liasses Fiscales

## 🎯 Problème résolu

L'ancienne approche était **trop rigide** :
- ❌ Supposait des positions fixes pour les colonnes (ex: `index_net`, `index_n + 1`)
- ❌ Ne fonctionnait pas si la structure du PDF variait légèrement
- ❌ Ne détectait pas les montants si le décalage changeait

## ✨ Nouvelle approche : Extraction Analytique en 3 phases

### 📍 PHASE 1 : Détection intelligente des tableaux

**Objectif** : Identifier automatiquement tous les tableaux pertinents dans le PDF

**Comment ça marche** :
- Parcourt toutes les pages du PDF
- Utilise des **signatures** (mots-clés) pour identifier chaque type de tableau
- Détecte : Actif, Passif, Compte de Résultat (pages 1 et 2), État des échéances, Affectation du résultat

**Avantages** :
- ✅ Ne fait aucune hypothèse sur le numéro de page
- ✅ S'adapte aux PDFs de structures différentes
- ✅ Peut détecter plusieurs tableaux du même type

### 📍 PHASE 2 : Analyse de la structure des colonnes

**Objectif** : Comprendre l'organisation des colonnes dans chaque tableau

**Comment ça marche** :
1. **Analyse des en-têtes** : Cherche "Brut", "Net", "Exercice N", "Total", etc.
2. **Identification du type de colonne** :
   - `code` : Colonnes avec codes (AB, DA, FL, etc.)
   - `libelle` : Colonnes avec les descriptions
   - `montant_net`, `montant_brut` : Colonnes de montants
   - `exercice_n`, `exercice_n_moins_1` : Colonnes d'exercices
3. **Score de confiance** : Attribue un score à chaque identification

**Avantages** :
- ✅ Détecte automatiquement les colonnes, peu importe leur position
- ✅ Identifie TOUTES les colonnes de montants
- ✅ Gère les variations de nommage ("Net" vs "NET" vs "net")

### 📍 PHASE 3 : Extraction avec règles métier

**Objectif** : Extraire les bonnes données selon les règles spécifiques à chaque tableau

**Règles métier implémentées** :

| Tableau | Règle |
|---------|-------|
| **Actif** | 3ème colonne de montant (colonne "Net" prioritaire) |
| **Passif** | 1ère colonne de montant (colonne "Exercice N" prioritaire) |
| **Clients douteux** | 1ère colonne de montant |
| **Groupes associés (actif)** | 1ère colonne de montant |
| **Annuités** | 2ème colonne de montant |
| **Groupes associés (passif)** | 1ère colonne de montant |
| **Affectation du résultat** | 1ère colonne de montant |

**Stratégies d'extraction** :
1. **Stratégie 1** : Chercher la colonne par son nom (ex: "Net" pour l'actif)
2. **Stratégie 2** : Utiliser le numéro de colonne de montant (ex: 3ème colonne)
3. **Stratégie 3** : Fallback sur la première colonne de montant

**Avantages** :
- ✅ S'adapte aux variations de structure
- ✅ Respecte les règles métier spécifiques
- ✅ Dégradation gracieuse (fallback si la stratégie 1 échoue)

## 🚀 Utilisation

### Mode 1 : CLI avec version analytique

```bash
# Placer les PDFs dans le dossier 'liasses/'
python main_v2_analytique.py
```

### Mode 2 : Intégration dans le code existant

```python
from extraction_analytique import ExtractionAnalytique
from main import CODES_BILAN_ACTIF, CODES_BILAN_PASSIF, CODES_COMPTE_RESULTAT

# Extraire un PDF
resultats = ExtractionAnalytique.extraire_pdf_complet(
    pdf_path="chemin/vers/liasse.pdf",
    codes_actif=CODES_BILAN_ACTIF,
    codes_passif=CODES_BILAN_PASSIF,
    codes_cr=CODES_COMPTE_RESULTAT
)
```

### Mode 3 : Interface Streamlit (à venir)

Modification de `interface.py` pour utiliser `extraire_un_pdf_analytique` au lieu de `extraire_un_pdf`.

## 📊 Comparaison : Ancienne vs Nouvelle approche

| Aspect | Ancienne approche | Nouvelle approche analytique |
|--------|-------------------|------------------------------|
| **Détection des tableaux** | Cherche des mots-clés fixes sur des pages spécifiques | Scanne tout le PDF, détection par signatures multiples |
| **Identification des colonnes** | Position fixe (ex: Net doit être à l'index X) | Analyse dynamique des en-têtes |
| **Extraction des montants** | Décalage fixe (+1 depuis l'en-tête) | Stratégies multiples avec règles métier |
| **Adaptabilité** | ❌ Faible | ✅ Très élevée |
| **Robustesse** | ❌ Casse si structure change | ✅ S'adapte automatiquement |
| **Maintenance** | ❌ Difficile (ajuster les index) | ✅ Facile (ajouter des règles) |

## 🔧 Architecture des fichiers

```
extraction_analytique.py
├── DetecteurTableaux        # Phase 1
├── AnalyseurStructure       # Phase 2
├── ExtracteurDonnees        # Phase 3
└── ExtractionAnalytique     # Orchestrateur

main_v2_analytique.py
└── Adaptateur pour le code existant
```

## 🧪 Tests et validation

Pour tester la nouvelle approche :

```bash
# 1. Tester avec un seul PDF
python -c "
from main_v2_analytique import extraire_un_pdf_analytique
from pathlib import Path

pdf = Path('liasses/votre_fichier.pdf')
resultats = extraire_un_pdf_analytique(pdf)
print(resultats)
"

# 2. Tester avec tous les PDFs (mode complet)
python main_v2_analytique.py
```

## 📈 Avantages de cette approche

1. **Robustesse** : S'adapte aux variations de structure des PDFs
2. **Maintenabilité** : Code modulaire et facile à étendre
3. **Transparence** : Affiche les étapes et décisions prises
4. **Règles métier claires** : Séparation entre détection et extraction
5. **Évolutivité** : Facile d'ajouter de nouveaux types de tableaux

## 🎓 Concepts clés

### Détection par signatures
Au lieu de chercher un seul mot-clé, on utilise plusieurs mots-clés et on calcule un score :
```python
SIGNATURES_TABLEAUX = {
    TypeTableau.ACTIF: ["Brut", "Amortissements", "Net", "immobilisations"]
}
```

### Analyse multi-stratégies
Pour trouver la bonne colonne, on essaie plusieurs approches dans l'ordre :
1. Chercher par nom de colonne
2. Chercher par position relative
3. Fallback sur la première colonne de montant

### Confiance et dégradation gracieuse
Chaque identification a un score de confiance. Si la confiance est faible, on utilise une méthode de secours.

## 🔮 Évolutions futures possibles

1. **Machine Learning** : Entraîner un modèle pour détecter automatiquement les colonnes
2. **Validation croisée** : Vérifier la cohérence des montants entre tableaux
3. **Détection d'anomalies** : Alerter si les montants semblent incohérents
4. **Export multi-formats** : JSON, CSV, XML en plus d'Excel
5. **API REST** : Exposer l'extraction comme service web

---

**Auteur** : Claude
**Version** : 2.0
**Date** : 2025
