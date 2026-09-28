#!/usr/bin/env python3
"""Recherche dans le BOFiP-Impôts (publications en vigueur).

Source : open data du ministère de l'Économie, jeu « bofip-vigueur »
https://data.economie.gouv.fr/explore/dataset/bofip-vigueur/
API publique, sans clé. Aucune dépendance : Python 3.8+ suffit.

Usage :
    python bofip_recherche.py                      # mode interactif (double-clic)
    python bofip_recherche.py "crédit d'impôt recherche"
    python bofip_recherche.py "TVA immobilier" -n 50 --csv resultats.csv
    python bofip_recherche.py --champs             # liste les champs disponibles
"""

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/bofip-vigueur"
MAX_PAR_APPEL = 100  # plafond imposé par l'API pour `limit`

# Champs affichés s'ils existent, repérés par morceau de nom (le schéma
# est lu à l'exécution, pour survivre à un renommage côté ministère).
PRIORITES = [
    ("identifiant", ("identifiant_juridique", "identifiant", "boi", "reference")),
    ("titre", ("titre", "title")),
    ("serie", ("serie",)),
    ("date", ("date_de_publication", "date_publication", "debut_de_validite", "date")),
    ("lien", ("permalien", "url", "lien")),
]


def appel(chemin, params=None):
    url = API + chemin
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "bofip-recherche/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        sys.exit(f"Erreur de l'API ({e.code}) : {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"Impossible de joindre l'API ({e.reason}). Vérifiez la connexion "
                 "ou le proxy du cabinet.")


def champs():
    return [(f["name"], f.get("type", ""), f.get("label", ""))
            for f in appel("").get("fields", [])]


def reperer(noms):
    """Associe chaque rôle (titre, date…) au premier champ existant qui correspond."""
    trouves = {}
    for role, candidats in PRIORITES:
        for c in candidats:
            match = next((n for n in noms if n == c), None) or \
                    next((n for n in noms if c in n), None)
            if match and match not in trouves.values():
                trouves[role] = match
                break
    return trouves


def rechercher(termes, nombre, serie=None):
    noms = [n for n, _, _ in champs()]
    roles = reperer(noms)
    # Recherche plein texte : une chaîne entre guillemets dans `where`.
    where = '"{}"'.format(termes.replace('"', " "))
    if serie and "serie" in roles:
        where += ' AND {} like "{}"'.format(roles["serie"], serie.replace('"', ""))
    params = {"where": where}
    if roles:  # évite de rapatrier le texte intégral des BOI
        params["select"] = ",".join(roles.values())
    if "date" in roles:
        params["order_by"] = roles["date"] + " desc"

    resultats, total = [], 0
    while len(resultats) < nombre:
        params["limit"] = min(MAX_PAR_APPEL, nombre - len(resultats))
        params["offset"] = len(resultats)
        page = appel("/records", params)
        total = page.get("total_count", 0)
        lot = page.get("results", [])
        resultats += lot
        if len(lot) < params["limit"]:
            break
    return resultats, total, roles


def afficher(resultats, total, roles):
    print(f"\n{total} publication(s) trouvée(s), {len(resultats)} affichée(s).\n")
    for i, r in enumerate(resultats, 1):
        get = lambda role: str(r.get(roles.get(role, ""), "") or "").strip()
        entete = " | ".join(x for x in (get("identifiant"), get("date")) if x)
        print(f"{i:>3}. {get('titre') or '(sans titre)'}")
        if entete:
            print(f"     {entete}")
        if get("lien"):
            print(f"     {get('lien')}")
        if not roles:  # schéma inattendu : on montre tout
            print("     " + json.dumps(r, ensure_ascii=False)[:300])
        print()


def exporter(resultats, chemin):
    if not resultats:
        return
    colonnes = list(dict.fromkeys(k for r in resultats for k in r))
    # utf-8-sig + « ; » : s'ouvre proprement dans Excel en français
    with open(chemin, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colonnes, delimiter=";")
        w.writeheader()
        w.writerows(resultats)
    print(f"Export : {chemin}")


def interactif():
    print("Recherche BOFiP-Impôts (publications en vigueur)")
    print("Entrée vide pour quitter.\n")
    while True:
        termes = input("Termes recherchés : ").strip()
        if not termes:
            return
        resultats, total, roles = rechercher(termes, 20)
        afficher(resultats, total, roles)
        if resultats and input("Exporter en CSV ? (o/N) ").strip().lower() == "o":
            nom = "bofip_" + "".join(c if c.isalnum() else "_" for c in termes)[:40] + ".csv"
            exporter(rechercher(termes, 500)[0], nom)
        print()


def main():
    p = argparse.ArgumentParser(description="Recherche dans le BOFiP-Impôts en vigueur.")
    p.add_argument("termes", nargs="?", help="mots recherchés (entre guillemets)")
    p.add_argument("-n", "--nombre", type=int, default=20, help="résultats max (défaut 20)")
    p.add_argument("--serie", help="filtre sur la série, ex. TVA, IS, BIC")
    p.add_argument("--csv", metavar="FICHIER", help="exporte les résultats en CSV")
    p.add_argument("--champs", action="store_true", help="liste les champs de l'API")
    a = p.parse_args()

    if a.champs:
        for nom, typ, label in champs():
            print(f"{nom:<35} {typ:<10} {label}")
    elif a.termes:
        resultats, total, roles = rechercher(a.termes, a.nombre, a.serie)
        afficher(resultats, total, roles)
        if a.csv:
            exporter(resultats, a.csv)
    else:
        interactif()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
