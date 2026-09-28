# Recherche BOFiP

Petit outil pour chercher dans le BOFiP-Impôts (publications en vigueur) depuis un poste du cabinet, sans Claude ni abonnement.

Il interroge l'API publique du ministère de l'Économie (jeu de données [`bofip-vigueur`](https://data.economie.gouv.fr/explore/dataset/bofip-vigueur/)). Pas de clé, pas de compte, pas de bibliothèque à installer.

## Installation (une fois par poste)

1. Installer Python 3 depuis [python.org](https://www.python.org/downloads/) et cocher **« Add python.exe to PATH »** pendant l'installation.
2. Copier le dossier `bofip` sur le poste ou sur le partage réseau du cabinet.
3. Double-cliquer sur `installer_raccourci.bat` : une icône **Recherche BOFiP** apparaît sur le Bureau.

Si le dossier est ensuite déplacé, relancer `installer_raccourci.bat` depuis son nouvel emplacement.

À la main, sans l'installeur : clic droit sur `rechercher_bofip.bat` → *Afficher d'autres options* (Windows 11) → *Envoyer vers* → *Bureau (créer un raccourci)*.

## Utilisation

**Sous Windows :** double-cliquer sur l'icône **Recherche BOFiP** du Bureau (ou sur `rechercher_bofip.bat`), taper les termes recherchés, puis Entrée. L'outil affiche les 20 publications les plus récentes qui correspondent, avec leur référence BOI et leur lien. Il propose ensuite un export CSV (jusqu'à 500 résultats), qui s'ouvre dans Excel.

**En ligne de commande :**

```
python bofip_recherche.py "crédit d'impôt recherche"
python bofip_recherche.py "location meublée" -n 50 --csv lmnp.csv
python bofip_recherche.py "autoliquidation" --serie TVA
python bofip_recherche.py --champs      # liste les champs fournis par l'API
```

## Limites à connaître

- L'outil liste les publications et donne leur lien, il n'interprète pas la doctrine. Lisez toujours le BOI sur [bofip.impots.gouv.fr](https://bofip.impots.gouv.fr).
- Les données en open data peuvent avoir quelques jours de retard sur le site officiel.
- La recherche est une recherche plein texte : plusieurs mots ramènent les documents qui les contiennent tous, où qu'ils soient.
- Si un proxy d'entreprise bloque l'accès, le message « Impossible de joindre l'API » s'affiche : il faut autoriser `data.economie.gouv.fr`.
