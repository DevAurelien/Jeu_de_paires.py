from random import choice, shuffle
from string import ascii_uppercase
from tinydb import TinyDB, Query
import yaml

digits = [l for l in range(1, 11)]
db = TinyDB('db.json')
user = Query()
FICHIER_DE_CONFIG = "config.yml"
SPACE = "  "

LISTE_JOUEURS = [el["nom"] for el in [element for element in db.all()]]
# print(LISTE_JOUEURS)
with open(FICHIER_DE_CONFIG, encoding='UTF-8') as config:
    document = yaml.safe_load(config)
    # print(document)


class Grille_de_jeu:
    def __init__(self, colonnes=2, lignes=2):
        self.colonnes = colonnes
        self.lignes = lignes
        self.level = 0
        self.liste_recto = []
        self.liste_verso = []
        self.liste_smiley_trouve = []
        self.liste_choix_user = []
        self.position_tempo = []
        self.paire_en_cours = []

    def new_grille(self, level):
        self.level = level
        self.lignes, self.colonnes = document["niveau"][level], document["niveau"][level]

        liste_all_smiley = [choice(document["recto"]) for _ in range(0, round((self.lignes * self.lignes) / 2))] * 2
        shuffle(liste_all_smiley)
        interro = [document["verso"] for _ in range(0, self.lignes * self.lignes)]

        self.liste_recto = [liste_all_smiley[i:i + self.lignes] for i in range(0, len(liste_all_smiley), self.lignes)]
        self.liste_verso = [interro[j:j + self.lignes] for j in range(0, len(interro), self.lignes)]

    def display_game(self):
        lvl = document["niveau"][self.level]
        display = f"{SPACE*2}"
        display = display + f"{SPACE * 2}".join(SPACE * 2 + ascii_uppercase[i] for i in range(0, lvl))
        display = display + "\n\n"

        for i in range(1, lvl + 1):
            display = display + f"\n{str(i)}{SPACE}"
            for j in range(0, lvl):
                display = display + f"{SPACE * 2}{self.liste_verso[i - 1][j]}{SPACE * 2}"
            display = display + "\n\n"
            j = 0


        print(display)

    def position_grille(self, choix_user=""):
        if (len(choix_user) > 2 or len(choix_user) <= 1) or (choix_user[0].isalpha() and choix_user[1].isalpha()) or (
                choix_user[0].isdigit() and choix_user[1].isdigit()):
            print(
                "Mauvaise saisi utilisateur")  # si chaine longueur incorrecte, si deux chiffres ou deux lettres entree
        else:
            chiffres = int(choix_user[0]) - 1 if choix_user[0] in digits else int(choix_user[1]) - 1
            lettres = ascii_uppercase.index(choix_user[1]) if choix_user[0] in digits else ascii_uppercase.index(
                choix_user[0])  # transforme le choix_user en position de grille suivant le sens A1 ou 1A
            choix_user_reverse = f"{choix_user[1]}{choix_user[0]}"
            if (chiffres > document["niveau"][self.level] or lettres > document["niveau"][self.level]):
                print(
                    "Mauvaise saisi utilisateur")  # si superieur a la taille de la grille
            else:
                if not (choix_user or choix_user_reverse) in self.liste_choix_user:
                    if self.paire_en_cours == []:
                        if not self.position_tempo == []:
                            self.liste_verso[self.position_tempo[0][0]][self.position_tempo[0][1]] = "❓"
                            self.liste_verso[self.position_tempo[1][0]][
                                self.position_tempo[1][1]] = "❓"
                            if not self.liste_smiley_trouve == []:
                                for smiley in self.liste_smiley_trouve:
                                    self.liste_verso[smiley[0][0]][smiley[0][1]] = self.liste_recto[smiley[0][0]][
                                        smiley[0][1]]
                                    self.liste_verso[smiley[1][0]][smiley[1][1]] = self.liste_recto[smiley[1][0]][
                                        smiley[1][1]]

                        # del (self.liste_choix_user[-4:-1])
                        self.position_tempo = []
                        self.liste_verso[chiffres][lettres] = self.liste_recto[chiffres][
                            lettres]  # changer la valeur liste_verso
                        self.paire_en_cours.append(
                            self.liste_recto[chiffres][lettres])  # on ajoute le smiley dans la liste paire
                        self.liste_choix_user.append(choix_user)
                        self.liste_choix_user.append(choix_user_reverse)  # le choix_user du moment 1
                        self.position_tempo.append([chiffres, lettres])  # le lieu du choix 1
                    else:
                        if self.liste_recto[chiffres][lettres] in self.paire_en_cours:
                            self.liste_verso[chiffres][lettres] = self.liste_recto[chiffres][
                                lettres]  # changer la valeur liste_verso
                            print('\nPaire trouvé ! Bien joué ! + 2 points\n')
                            self.liste_choix_user.append(
                                choix_user_reverse)
                            self.liste_choix_user.append(choix_user)
                            self.position_tempo.append([chiffres, lettres])
                            self.liste_smiley_trouve.append(self.position_tempo)
                            self.paire_en_cours = []
                            return 2
                        else:
                            self.liste_choix_user = []
                            self.liste_verso[chiffres][lettres] = self.liste_recto[chiffres][
                                lettres]  # changer la valeur liste_verso
                            self.position_tempo.append([chiffres, lettres])
                            self.paire_en_cours = []
                            print('Dommage ! -1 points')
                            return -1


class Joueur:
    def __init__(self, nom):
        self.nom = nom
        self.points = 0

    def creer_joueur(self, nom_joueur):
        if not nom_joueur in LISTE_JOUEURS:
            db.insert({'nom': self.nom, 'niveau': 0, 'liste_recto': [],
                       'liste_verso': [],
                       'liste_smiley_trouve': [],
                       'liste_choix_user': []})

    def sauvegarder_pj(self, niveau, liste_recto, liste_verso, liste_smiley_trouve, liste_choix_user):
        db.update({'niveau': niveau}, user.nom == self.nom)
        db.update({'liste_recto': liste_recto}, user.nom == self.nom)
        db.update({'liste_verso': liste_verso}, user.nom == self.nom)
        db.update({'liste_smiley_trouve': liste_smiley_trouve}, user.nom == self.nom)
        db.update({'liste_choix_user': liste_choix_user}, user.nom == self.nom)

    def charger_pj(self):
        joueur_trouve = db.search(user.nom == self.nom)
        # print(joueur_trouve)
        return [joueur_trouve[0]["niveau"], joueur_trouve[0]["liste_recto"], joueur_trouve[0]["liste_verso"],
                joueur_trouve[0]["liste_smiley_trouve"], joueur_trouve[0]["liste_choix_user"]]


if __name__ == "__main__":

    grid = Grille_de_jeu()
    # Creation
    oui_non = ""
    print()
    print("Bienvenue au Jeu de Paires !\n")
    # nom_joueur = input("Comment tu t'appelles ?\n").lower().title()
    perso = Joueur("nom_joueur")
    print()
    # if db.search(user.nom == perso.nom) != []:
    #     print("\nVoulez_vous charger la partie precedente ?\n")
    #     oui_non = input("O = Oui, N = Non\n").upper()
    #     if oui_non == "O":
    #         liste_recup_joueur = perso.charger_pj()
    #         grid.level = liste_recup_joueur[0]
    #         grid.liste_recto = liste_recup_joueur[1]
    #         grid.liste_verso = liste_recup_joueur[2]
    #         grid.liste_smiley_trouve = liste_recup_joueur[3]
    #         grid.liste_choix_user = liste_recup_joueur[4]
    # else:
    perso.creer_joueur(perso.nom)

    i = 0

    while i < 5:
        if oui_non != "O":
            grid.liste_verso, grid.liste_recto, grid.liste_smiley_trouve, grid.liste_choix_user = [], [], [], []
            grid.new_grille(i + 3)
        print("Niveau ", i, " :")
        while not grid.liste_verso == grid.liste_recto:
            print()
            grid.display_game()
            perso.sauvegarder_pj(grid.level, grid.liste_recto, grid.liste_verso, grid.liste_smiley_trouve,
                                 grid.liste_choix_user)
            quit()
            choix_user = input("Votre choix :\n").upper()
            pts = grid.position_grille(choix_user)
            perso.points += pts if pts != None else 0

        print("Total : ", perso.points, " points\n")
        perso.points = 0
        i += 1

    print("Fin du jeu ! Merci ")
    quit()
