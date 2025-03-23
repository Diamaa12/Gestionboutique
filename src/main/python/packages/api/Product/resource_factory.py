# Créez une classe centrale de ressources
import os
from pathlib import Path


class RessourceFactory:
    _contexte = None
    _ressources = {}
    @staticmethod
    def set_contexte(ctx):
        RessourceFactory._contexte = ctx

    @staticmethod
    def get_contexte():
        if RessourceFactory._contexte is None:
            raise Exception("Le contexte n'a pas été initialisé.")

        return RessourceFactory._contexte

