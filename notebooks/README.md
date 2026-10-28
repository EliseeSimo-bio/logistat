# Notebooks

Explorations des blocs 2 et 3. Elles ne font pas partie de l'application : ce qui est
retenu est déplacé dans `src/logistat/` et testé.

Pour importer le code du projet depuis un notebook, installez d'abord le paquet
(`pip install -r requirements.txt`, qui l'installe en mode éditable), puis :

```python
from logistat.donnees import charger_commandes

commandes = charger_commandes().commandes
```
