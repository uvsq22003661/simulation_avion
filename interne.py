from random import choice

################
## CONSTANTES ##
################

NOM_VALVES = ("VT12", "VT23", "V12", "V13", "V23")

###################################################
## COMPOSANT ## classe parent des autres classes ##
###################################################

class Composant(object):
    """ Classe parent des classes Pompe, Moteur et Reservoir
    attributs :
    - numero, int:
        numéro identifiant le composant
    """

    def __init__(self, numero: int):
        """
        Initialise les attributs communs aux autres classes
        """
        self.__numero = numero
        self.reset() # utilise leur fonction reset pour initier leurs attributs

    ### GETTER DE 'numero' ###
    @property
    def numero(self) -> int:
        return self.__numero

############
## MOTEUR ##
############

class Moteur(Composant):
    """ Classe simulant le fonctionnement d'un moteur d'un avion
    attributs :
    - numero, int : initié dans la classe Composant
        valeurs possibles = 1, 2 ou 3
    - fonctionnel, int : initié dans la classe Composant
        vérifie s'il existe une source alimentant le moteur
    - source, int :
        numéro du réservoir alimentant le moteur s'il est alimenté
    méthode :
    - reset : remet le moteur à son état fonctionnel
    """

    def reset(self) -> None:
        """
        Réinitialise l'attribut source du moteur à sa valeur initiale :
        - la source est le réservoir correspondant au moteur
        """
        self.__source = self.numero

    ### GETTER DE 'fonctionnel' ###
    @property
    def fonctionnel(self) -> bool:
        return self.source is not None

    ### GETTER, SETTER ET DELETER DE 'source' ###
    @property
    def source(self) -> int:
        return self.__source

    @source.setter
    def source(self, source: int) -> None:
        if isinstance(source, int):
            self.__source = source
        else:
            raise ValueError("'source' est un entier")

    @source.deleter
    def source(self) -> None:
        self.__source = None

###########
## POMPE ##
###########

class Pompe(Composant):
    """ Classe simulant le fonctionnement d'une pompe d'un réservoir
    attributs :
    - numero, int : initié dans la classe Composant
        valeurs possibles = 11, 12, 21, 22, 31 ou 32
        chiffre des dizaines = numéro du réservoir
        chiffre des unités = 1 si c'est la pompe principale
                             2 si c'est la pompe de secours
    - active, bool :
        True = la pompe est active
        False = la pompe est inactive
    - panne, bool :
        True = la pompe est en panne
        False = la pompe n'est pas en panne
    - fonctionnel, bool :
        True si la pompe est active mais pas en panne
        False sinon

    méthode :
    - genere_panne : la pompe tombe en panne
    - reset : remet la pompe à son état fonctionnel
    """

    def reset(self) -> None:
        """
        Réinitialise les attributs de la pompe à leur valeur initiale :
        - la pompe principale est active
        - la pompe de secours est inactive
        - les deux pompes ne sont pas en panne
        """
        if (self.numero % 10) == 1: # pompe principale
            self.__active = True
            self.__panne = False

        elif (self.numero % 10) == 2: # pompe de secours
            self.__active = False
            self.__panne = False

        else: # numero impossible
            raise ValueError(f"{self.numero} n'est pas un numero de pompe correcte.")

    ### GETTER ET SETTER DE 'active' ###
    @property
    def active(self) -> bool:
        return self.__active

    @active.setter
    def active(self, active: bool) -> None:
        if (self.numero % 10) == 1: # pompe principale
            raise AttributeError("L'état de la pompe principale (active/inactive) ne peut pas etre changé")
        elif isinstance(active, bool): # verifie si active est un booléen
            self.__active = active
        else:
            raise ValueError("argument 'active' non booléen")

    ### GETTER ET MÉTHODE DE 'panne' ###
    @property
    def panne(self) -> bool:
        return self.__panne

    def genere_panne(self) -> None:
        self.__panne = True

    ### GETTER DE 'fonctionnel' ###
    @property
    def fonctionnel(self) -> bool:
        return self.active and not self.panne

###############
## RESERVOIR ##
###############

class Reservoir(Composant):
    """ Classe simulant le fonctionnement d'un réservoir
    attributs :
    - numero, int : initié dans la classe Composant
        valeurs possibles = 1, 2 ou 3
    - plein, bool :
        True = le réservoir est plein
        False = le réservoir est vide
    - pompe_principale, object : classe Pompe
        simule la pompe principale du réservoir
    - pompe_secours, object : classe Pompe
        simule la pompe de secours du réservoir
    - fonctionnel, bool :
        True si le réservoir est plein et qu'au moins une des deux pompes fonctionne
        False sinon
    méthode :
    - remplissage : remplie le réservoir
    - vidange : vide le réservoir
    - reset : remet le réservoir à son état fonctionnel
    """

    def reset(self) -> None:
        """
        Réinitialise les attributs du réservoir à leur valeur initiale :
        - le réservoir est plein
        - les pompes sont réinitialisées ou initialisées si elles n'existent pas
        """
        self.__plein = True

        if hasattr(self, '__pompe_principale'):
            self.__pompe_principale.reset()
        else: self.__pompe_principale = Pompe( (self.numero*10) + 1 )

        if hasattr(self, '__pompe_secours'):
            self.__pompe_secours.reset()
        else: self.__pompe_secours = Pompe( (self.numero*10) + 2 )

    ### GETTERS DE 'pompe_principale' ET 'pompe_secours' ###
    @property
    def pompe_principale(self) -> object:
        return self.__pompe_principale

    @property
    def pompe_secours(self) -> object:
        return self.__pompe_secours

    ### GETTER ET MÉTHODES DE 'plein' ###
    @property
    def plein(self) -> bool:
        return self.__plein

    def remplissage(self) -> None:
        self.__plein = True

    def vidange(self) -> None:
        self.__plein = False
    
    ### GETTER DE 'fonctionnel' ###
    @property
    def fonctionnel(self) -> bool:
        return self.plein and (self.pompe_principale.fonctionnel or self.pompe_secours.fonctionnel)

###########
## AVION ##
###########

class Avion(object):
    """ Classe simulant le fonctionnement d'un avion
    attributs :
    - reservoirs, list : liste des instances des trois réservoirs de la classe Reservoir
    - moteurs, list : liste des instances des trois moteurs de la classe Moteur
    - valves, dict : dictionnaire contenant les valves de l'avion
        clé = nom de la valve dont les valeurs possibles sont dans la constante NOM_VALVES
        valeur = état de la valve :
            True = valve ouverte, le flux passe
            False = valve fermée, le flux ne passe pas
    - nbr_erreurs, int : positif
        variable contenant le nombre d'erreurs dans le système
        calculé lors de la mise à jour de ce dernier
    - note, int : 0 à 10 inclus
        note attribuée à la session actuelle de l'avion
    - historique, list :
        garde en mémoire les différentes actions effectuées pendant la session (simulation ou
        exercice)
    """

    def __init__(self):
        self.__reservoirs = [Reservoir(num) for num in range(1, 4)] # Création des 3 réservoirs
        self.__moteurs = [Moteur(num) for num in range(1, 4)] # Création des 3 moteurs
        self.__valves = {nom: False for nom in NOM_VALVES}
        self.__nbr_erreurs = 0
        self.__note = 10
        self.__historique = []

    ### GETTERS ###
    @property
    def reservoirs(self):
        return self.__reservoirs

    @property
    def moteurs(self):
        return self.__moteurs

    @property
    def valves(self):
        return self.__valves

    @property
    def note(self):
        return self.__note

    @property
    def historique(self):
        return self.__historique

    ### MÉTHODES NON ACCESSIBLES EN DEHORS DE LA CLASSE ### 
    def __reequilibrage_reservoirs(self) -> int:
        """
        Réequilibre les réservoirs si la valve entre deux réservoirs est ouverte
        et vérifie l'utilité de l'ouverture des valves :
            pour les deux valves VT :
            - si l'un des deux réservoirs adjacents à la valve est vide et l'autre est plein,
            celui qui est vide se remplit 
            - sinon augmente le nombre d'erreur
        """
        nbr_erreurs = 0
        if self.valves['VT12']:
            if self.reservoirs[0].plein and self.reservoirs[1].plein:
                nbr_erreurs += 1
            elif self.reservoirs[0].plein or self.reservoirs[1].plein:
                self.reservoirs[0].remplissage()
                self.reservoirs[1].remplissage()
            else:
                nbr_erreurs += 1

        if self.valves['VT23']:
            if self.reservoirs[1].plein and self.reservoirs[2].plein:
                nbr_erreurs += 1
            elif self.reservoirs[1].plein or self.reservoirs[2].plein:
                self.reservoirs[1].remplissage()
                self.reservoirs[2].remplissage()
            else:
                nbr_erreurs += 1

        return nbr_erreurs

    def __verification_moteurs(self) -> int:
        """
        Vérifie si les moteurs sont bien alimentés
        et compte le nombre de réservoirs les alimentant
        ainsi que le nombre d'erreur :
        - pour chaque moteur, regarde pour chacun des réservoirs
            si celui-ci peut alimenter le moteur
        - vérifie si aucune pompe de secours n'est activée pour rien
            augmente le nombre d'erreur sinon
        - vérifie si au moins un moteur fonctionne
            met la note à 0 sinon
        """
        nbr_erreurs = 0
        for i, moteur in enumerate(self.moteurs):
            
            liste_flux = []
            for j in range(3): # boucle commencant par le reservoir correspondant au moteur

                reservoir = self.reservoirs[(i+j)%3]
                if reservoir.fonctionnel and self.__flux_ouvert(reservoir, moteur):
                    # le réservoir alimente le moteur
                    liste_flux.append(reservoir.numero)

            if liste_flux: # si il existe au moins un flux
                moteur.source = liste_flux.pop(0)
                # autant d'erreur a ajouter que de flux inutiles
                nbr_erreurs += len(liste_flux)
            else: # le moteur n'est pas alimenté
                del moteur.source
                nbr_erreurs += 1

        for reservoir in self.reservoirs:
            if reservoir.pompe_secours.fonctionnel and not reservoir.pompe_principale.panne:
                # la pompe de secours est activée pour rien
                nbr_erreurs += 1

        # si plus aucun moteur ne marche, la note tombe à 0
        if not any([moteur.fonctionnel for moteur in self.moteurs]):
            self.__note = 0

        return nbr_erreurs

    def __flux_ouvert(self, composant_1: object, composant_2: object) -> bool:
        """
        Vérifie si le flux peut passer entre les deux composants
        """
        if nom := nom_valve(composant_1, composant_2): # si il existe une valve entre les deux composants
            return self.valves[nom] # retourne si la valve est ouverte ou non
        else: return True # sinon le flux est ouvert (car il n'y a pas de valve)

    ### MÉTHODES ACCESSIBLES EN DEHORS DE LA CLASSE ###
    def reset(self) -> None:
        """
        Réinitialise les attributs de l'avion à leur valeur initiale :
        - les moteurs sont réinitialisés
        - les réservoirs sont réinitialisés
        - les valves sont fermées, le flux ne passe pas
        - il n'y a plus d'erreur
        - retour à la note maximale
        - l'historique est vide
        """
        for moteur in self.moteurs: moteur.reset()
        for reservoir in self.reservoirs: reservoir.reset()
        for nom_valve in self.valves: self.valves[nom_valve] = False
        self.__nbr_erreurs = 0
        self.__note = 10
        self.__historique = []

    def update(self, compte=True) -> str:
        """ Mise à jour de l'avion
        vérifie si les réservoirs ont besoin d'être rééquilibrés
        et si les moteurs sont toujours alimentés
        
        argument :
        - compte, bool : indique si la note doit être changée
        retourne :
        - 'x', str : si il y a au moins autant d'erreur qu'avant la mise à jour
        - 'v', str : si il y a moins d'erreur qu'avant la mise à jour
        """
        nbr_erreurs = self.__nbr_erreurs # garde en mémoire le nombre d'erreurs avant mise à jour

        # mise à jour #
        self.__nbr_erreurs = self.__reequilibrage_reservoirs()
        self.__nbr_erreurs += self.__verification_moteurs()

        # vérifie si le système a des erreurs ou si il y en a moins #
        if (0 < nbr_erreurs <= self.__nbr_erreurs) and compte:
            self.__note -= 1
            return 'x'
        return 'v'
        # print(f"Note: {self.note}/10")

    ## INTÉRACTION UTILISATEUR AVEC LE SYSTÈME ##
    def switch_valve(self, nom_valve: str) -> None:
        """
        Passe la valve 'nom_valve' de l'état ouvert à fermé ou inversement
        argument :
        - nom_valve, str : nom identifiant la valve à ouvrir/fermer
        """
        self.__valves[nom_valve] = not self.__valves[nom_valve] # ouvre/ferme la valve v

        # mise à jour de l'historique #
        etat = "ouverture" if self.valves[nom_valve] else "fermeture"
        choix = self.update()
        self.historique.append(f"{choix}| {etat} de la valve {nom_valve}")

    def switch_pompe_secours(self, num_reservoir: int) -> None:
        """
        Passe la pompe de secours du réservoir numéro 'num_reservoir'
        de l'état active à inactive ou inversement
        argument :
        - num_reservoir, int : numéro identifiant le réservoir dont la pompe de secours
            doit être activée ou désactivée
        """
        reservoir = self.reservoirs[num_reservoir]
        reservoir.pompe_secours.active = not reservoir.pompe_secours.active

        # mise à jour de l'historique #
        etat = "activation" if reservoir.pompe_secours.active else "désactivation"
        choix = self.update()
        self.historique.append(f"{choix}| {etat} de la pompe P{num_reservoir+1}2")

    ## GÉNERATION DE PANNE ##
    def vidange_reservoir(self, numero: int) -> None:
        """
        Vide le réservoir numéro 'numero'
        argument :
        - numero, int : numéro identifiant le réservoir à vider
        """
        self.reservoirs[numero-1].vidange() # vide le reservoir numero 'numero'

        # mise à jour de l'historique #
        self.historique.append(f"o| Réservoir {numero} n'a plus de carburant")
        self.update(compte=False)

    def panne_pompe(self, num_pompe: int) -> None:
        """
        Génère une panne pour la pompe numéro 'num_pompe'
        argument :
        - num_pompe, int : numéro identifiant la pompe à faire tomber en panne
        """
        # récupère le numéro du réservoir à partir du numéro de la pompe
        num_reservoir = (num_pompe // 10)
        if (num_pompe % 2) == 1:
            self.reservoirs[num_reservoir-1].pompe_principale.genere_panne()
        else:
            self.reservoirs[num_reservoir-1].pompe_secours.genere_panne()

        # mise à jour de l'historique #
        log = f"o| P{num_pompe} tombe en panne"
        if log in self.historique:
            self.historique.append(log)

        self.update(compte=False)

    def panne_aleatoire(self) -> None:
        """
        Génère une panne aléatoirement :
        - 50% de chance de vider un réservoir
        - 50% de chance de mettre en panne une des pompes
        ainsi chaque réservoir et chaque pompe ont équitablement
        une chance d'être impacté.
        """
        if choice((True, False)): # vide un reservoir
            self.vidange_reservoir(choice((1, 2, 3)))
        else: # met en panne une pompe
            self.panne_pompe(choice((11, 12, 21, 22, 31, 32)))


def nom_valve(c1: object, c2: object) -> str or None: # composant_1, composant_2
    """
    Retourne le nom de la valve entre le composant c1 et le composant c2
    """
    if c1.numero == c2.numero:
        return None # pas de valve entre les deux composants

    n, N = sorted([c1.numero, c2.numero])
    if type(c1) == type(c2): # deux réservoirs
        return "VT" + str(n) + str(N)
    else: # un réservoir et un moteur
        return "V" + str(n) + str(N)


if __name__ == '__main__':
    print("Veuillez executer le fichier main.py.")

