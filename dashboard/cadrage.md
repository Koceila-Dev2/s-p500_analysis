# Cadrage — Dashboard Exoplanètes

## Message clé

> **Le catalogue d'exoplanètes connu est un miroir déformé par nos instruments : 74 % des planètes détectées le sont par transit, une méthode qui favorise mécaniquement les grosses planètes proches de leur étoile — et seule une poignée de candidates rocheuses tombent en zone habitable, sur un échantillon encore trop incomplet pour trancher.**

## Audience cible

Une équipe de recherche en astronomie / des décideurs scientifiques (type comité de sélection de mission spatiale), qui doivent comprendre **ce que le catalogue actuel peut et ne peut pas dire** avant d'investir dans de nouvelles missions (PLATO, JWST, Gaia).

## KPIs retenus

| KPI | Valeur | Vanity ou Actionable ? | Justification |
|---|---|---|---|
| **% de planètes découvertes par transit** | ~74 % | **Actionable** | Ce chiffre est la clé de lecture de tout le dashboard : il explique pourquoi le catalogue est dominé par des grosses planètes à courte période. Il oriente directement l'interprétation de tous les autres graphiques et justifie l'investissement dans des méthodes complémentaires (imagerie, microlensing, astrométrie Gaia). |
| **Nombre de candidates rocheuses en zone habitable** | 18 (sur 5 903 planètes) | **Actionable** | Répond directement à la question scientifique centrale et cadre l'ampleur réelle de la recherche d'habitabilité — un chiffre à comparer à un total, pas une statistique brute isolée. Contextualisé par le taux de couverture (14 % seulement des planètes ont une insolation mesurée), ce qui évite la surinterprétation. |
| **Masse médiane par méthode de détection (Transit vs Vitesse radiale)** | 8j / 315 M⊕ | **Actionable** | Comparaison qui matérialise concrètement le biais instrumental : deux méthodes, deux populations de planètes complètement différentes. Sert de preuve, pas de simple décompte. |

*Écarté volontairement : "nombre total d'exoplanètes découvertes" (5 903) en KPI isolé — c'est une vanity metric qui ne dit rien sur la représentativité du catalogue. Il apparaît uniquement en contexte, dans le sous-titre.*

## Structure prévue

- **Titre** : porte le message (biais de détection), pas le nom du dataset.
- **Zone KPIs** (haut de page, sur données filtrées) : les 3 indicateurs ci-dessus, avec contexte chiffré (n total, % couverture).
- **Sidebar / filtres** : méthode de découverte (multiselect), plage d'années de découverte (slider), type planétaire (multiselect) — appliqués à tous les graphiques de détail.
- **Zone détail, en onglets** :
  1. **Biais de détection** — scatter Période × Rayon coloré par méthode (le graphe clé), répartition des méthodes.
  2. **Typologie planétaire** — distribution des types, relation masse-rayon.
  3. **Zone habitable** — scatter insolation × rayon, table des candidates.
  4. **Évolution temporelle** — courbe des découvertes par méthode et par année (effet Kepler/TESS).
