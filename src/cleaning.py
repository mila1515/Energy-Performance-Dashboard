"""Fonctions de nettoyage de texte utilisees par le notebook 02."""

import re

import pandas as pd

# Sigles a conserver en majuscules dans les noms de batiments.
ACRONYMS = {
    'AMC', 'CHI', 'CVS', 'FHCRC', 'HQ', 'IBM', 'II', 'III', 'IV', 'KCTS', 'KOMO',
    'LDS', 'LLC', 'LP', 'MLK', 'NE', 'NW', 'PCC', 'QFC', 'REI', 'SCCA', 'SE',
    'SHA', 'SPS', 'SPU', 'SW', 'UPS', 'US', 'USA', 'UW', 'UWMC', 'VA', 'VI',
    'VII', 'YMCA', 'YWCA',
}

_WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def _format_word(match: re.Match) -> str:
    word = match.group(0)
    start = match.start()
    text = match.string
    # Mot deja en casse mixte ("Parent", "UWMedicine") ou lettre seule ("D", "I") : conserve
    if word != word.upper() or len(word) == 1:
        return word
    # "1ST", "42ND" -> "1st", "42nd"
    if start > 0 and text[start - 1].isdigit():
        return word.lower()
    if word.upper() in ACRONYMS:
        return word.upper()
    # "CHILDREN'S" -> "Children's" (et non "Children'S")
    return word[0].upper() + word[1:].lower()


def format_building_name(name: str) -> str:
    """Met en forme les mots ecrits en MAJUSCULES d'un nom de batiment.

    Les mots deja en casse mixte dans la source sont conserves tels quels,
    les sigles connus restent en majuscules.
    """
    name = re.sub(r'\s+', ' ', str(name)).strip()
    return _WORD.sub(_format_word, name)


def format_building_names(names: pd.Series) -> pd.Series:
    return names.fillna('Unknown').map(format_building_name)
