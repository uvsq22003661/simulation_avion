#############################
## IMPORTATION DES MODULES ##
#############################

import tkinter as tk # Interface graphique #
from interne import * # Fichier backend #
from datetime import datetime
import os, webbrowser

################
## CONSTANTES ##
################

# nouveau #
TIMER_EXERCICE = 60 # secondes
# Canvas #
Longueur, Hauteur = 600, 400
couleur_bg = 'black'
couleur_fg = 'white'
bouton_relief = 'flat'
font = ('bold', '20')

# Interface #
COULEUR_FOND = "black"
COULEUR_CONTOUR = "gray35"
COULEURS_TANK = {1: "medium violet red", 2: "dark violet", 3: "medium blue"}
COULEUR_CONTOUR_TANK = {1: "VioletRed4", 2: "DarkOrchid4", 3: "blue4"}
COULEUR_MOTEUR = "gray20"
COULEUR_TEXTE = "white"
TAILLE_BORDURE = 3
fonte = ("Rockwell","20")
WIDTH = 500
HEIGHT = 500
pseudo = ''
mdp = ''
profils = "profils.txt"

########################################
## FONCTIONS POUR DESSINER LE SYSTÈME ##
########################################

def reset_interface():
    """Remet l'interface aux conditions initiales"""
    avion.reset()
    update_interface(root.interface)


def update_interface(interface):
    """Actualise l'interface avec les données correspondantes"""
    for num, reservoir in enumerate(avion.reservoirs, 1):

        # reservoir #
        if reservoir.plein:
            interface.itemconfig(items[f'TT{num}'], fill=COULEURS_TANK[num], outline=COULEUR_CONTOUR_TANK[num])
            interface.itemconfig(items[f'R{num}'], fill=COULEURS_TANK[num])
        else: # reservoir vide
            interface.itemconfig(items[f'TT{num}'], fill='')
            interface.itemconfig(items[f'R{num}'], fill=COULEUR_FOND)

        # pompe #
        if reservoir.pompe_principale.panne:
            interface.itemconfig(items[f'P{num}1'], fill='red')
        else: # pompe principale active
            interface.itemconfig(items[f'P{num}1'], fill='green')

        # pompe_secours #
        if reservoir.pompe_secours.panne:
            interface.itemconfig(items[f'P{num}2'], fill='red')
        elif not reservoir.pompe_secours.active: # pompe secours inactive
            interface.itemconfig(items[f'P{num}2'], fill='black')
        else: # pompe secours active
            interface.itemconfig(items[f'P{num}2'], fill='green')

    for num, moteur in enumerate(avion.moteurs, 1):
        if moteur.fonctionnel:
            interface.itemconfig(items[f'T{num}'],
                    fill=COULEURS_TANK[moteur.source],
                    outline=COULEUR_CONTOUR_TANK[moteur.source]
                    )
            interface.itemconfig(items[f'M{num}'], fill=COULEUR_MOTEUR)
        else: # moteur non fonctionnel
            interface.itemconfig(items[f'T{num}'], fill='')
            interface.itemconfig(items[f'M{num}'], fill='red')
    
    for nom_valve in avion.valves:
        x1, y1, x2, y2 = interface.coords(items[nom_valve][1])
        if x1 == x2 and avion.valves[nom_valve]:
            y = (y1 + y2) / 2
            rayon = y1 - y
            interface.coords(items[nom_valve][1], x1-rayon, y, x1+rayon, y)
        elif y1 == y2 and not avion.valves[nom_valve]:
            x = (x1 + x2) / 2
            rayon = x1 - x
            interface.coords(items[nom_valve][1], x, y1-rayon, x, y1+rayon)


#############################################
## INTÉRACTION UTILISATEUR AVEC LE SYSTÈME ##
#############################################

def switch_valve(nom_valve):
    """Ouvre ou ferme une valve par son bouton"""
    avion.switch_valve(nom_valve)
    update_interface(root.interface)


def switch_pompe_secours(num_reservoir):
    """Active ou désactive une pompe de secours par son bouton"""
    avion.switch_pompe_secours(num_reservoir)
    update_interface(root.interface)


#########################
## GÉNERATION DE PANNE ##
#########################

def vide_reservoir(numero):
    """Vide un réservoir par un clic dessus"""
    avion.vidange_reservoir(numero)
    update_interface(root.interface)


def panne_pompe(num_pompe):
    """Génère la panne d'une pompe par un clic dessus"""
    avion.panne_pompe(num_pompe)
    update_interface(root.interface)


###########################################################################
## FONCTIONS POUR CRÉER LES DIFFÉRENTES FORMES DES COMPOSANTS DE L'AVION ##
###########################################################################

def round_rectangle(interface, x1, y1, x2, y2, radius=25, **kwargs):
    """ Création d'un rectangle avec les coins arrondis """
        
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]

    return interface.create_polygon(points, **kwargs, smooth=True)


def create_valve(interface, x, y, rayon, nom):
    """Création des valves"""
    circle = interface.create_oval(
            x-rayon, y-rayon, x+rayon, y+rayon,
            outline='white', fill='black'
            )
    line = interface.create_line(
            x, y-rayon, x, y+rayon,
            fill='white', width=5, capstyle='round'
            )
    interface.create_text(x, y+2*rayon, text=nom, fill=COULEUR_TEXTE)
    return (circle, line)


def create_reservoir(interface, x, y, h, w, numero):
    """Création des réservoirs"""
    r = w / 2 # rayon du cercle d'une pompe

    ### RÉSERVOIR ###
    reservoir = round_rectangle(interface,
            x-w, y-h, x+w, y+h,
            outline=COULEUR_CONTOUR_TANK[numero], fill=COULEURS_TANK[numero],
            tags=f'R{numero}', width=TAILLE_BORDURE
            )
    text_reservoir = interface.create_text(
            x, y, text=f"T{numero}", font=font, tags=f'R{numero}', fill=COULEUR_TEXTE
            )
    
    ### POMPE PRINCIPALE ###
    pompe = interface.create_oval(
            x-(w/2)-r, y+h-2*r, x-(w/2)+r, y+h,
            fill='black', tags=f'P{numero}1', outline=''
            )
    text_pompe = interface.create_text(
            (x-(w/2), y+h-r),
            text=f'P{numero}1', tags=f'P{numero}1', fill=COULEUR_TEXTE
            )

    ### POMPE SECOURS ###
    pompe_secours = interface.create_oval(
            x+(w/2)-r, y+h-2*r, x+(w/2)+r, y+h,
            fill='black', tags=f'P{numero}2', outline=''
            )
    text_pompe_secours = interface.create_text(
            (x+(w/2), y+h-r),
            text=f'P{numero}2', tags=f'P{numero}2', fill=COULEUR_TEXTE
            )
    return reservoir, pompe, pompe_secours


def create_moteur(interface, x, y, h, w, numero):
    """Création des moteurs"""
    moteur = round_rectangle(interface,
            x-w, y-h, x+w, y+h,
            outline=COULEUR_CONTOUR, fill=COULEUR_MOTEUR, radius=15
            )
    interface.create_text(x, y, text=f"M{numero}", font=font, fill=COULEUR_TEXTE)
    return moteur


def etat_systeme(root):
    """Création de l'interface principale pour simulateur et exercice"""
    global items
    interface = tk.Canvas(root, width=Longueur, height=Hauteur, bg=COULEUR_FOND)
    items = {}
    
    rayon_valve = 12
    hauteur_reservoir = Hauteur / 8
    largeur_reservoir = Hauteur / 12
    oy_reservoir = Hauteur / 6
    oy_moteur = (5*Hauteur) / 6
    ox_V1 = (1.5*Longueur)/4
    ox_V3 = (2.5*Longueur)/4
    oy_V13 = (5*Hauteur) / 12
    oy_V2 = (7*Hauteur) / 12
    q = Longueur / 4
    tl = 4
    tw = TAILLE_BORDURE
    
    # tuyaux
    items["T2"] = interface.create_polygon(
            (2*q-tl, oy_reservoir), (2*q+tl, oy_reservoir),
            (2*q+tl, oy_V2-tl), (ox_V3, oy_V2-tl), (ox_V3, oy_V2+tl), (2*q+tl, oy_V2+tl),
            (2*q+tl, oy_moteur), (2*q-tl, oy_moteur),
            (2*q-tl, oy_V2+tl), (ox_V1, oy_V2+tl), (ox_V1, oy_V2-tl), (2*q-tl, oy_V2-tl),
            outline='white', fill='yellow', joinstyle='round', width=tw
            )
    items["T1"] = interface.create_polygon(
            (q-tl, oy_reservoir), (q+tl, oy_reservoir),
            (q+tl, oy_V13-tl), (ox_V3, oy_V13-tl), (ox_V3, oy_V13+tl), (q+tl, oy_V13+tl),
            (q+tl, oy_V2-tl), (ox_V1, oy_V2-tl), (ox_V1, oy_V2+tl), (q+tl, oy_V2+tl),
            (q+tl, oy_moteur), (q-tl, oy_moteur),
            outline='black', fill='yellow', joinstyle='round', width=tw
            )
    items["T3"] = interface.create_polygon(
            (3*q-tl, oy_reservoir), (3*q+tl, oy_reservoir),
            (3*q+tl, oy_moteur), (3*q-tl, oy_moteur),
            (3*q-tl, oy_V2+tl), (ox_V3, oy_V2+tl), (ox_V3, oy_V2-tl), (3*q-tl, oy_V2-tl),
            (3*q-tl, oy_V13+tl), (ox_V3, oy_V13+tl), (ox_V3, oy_V13-tl), (3*q-tl, oy_V13-tl),
            outline='black', fill='yellow', joinstyle='round', width=tw
            )
    items['TT1'] = interface.create_rectangle(
            q, oy_reservoir-tl, ox_V1, oy_reservoir+tl,
            outline='black', fill='yellow', width=tw
            )
    items['TT2'] = interface.create_rectangle(
            ox_V1, oy_reservoir-tl, ox_V3, oy_reservoir+tl,
            outline='black', fill='yellow', width=tw
            )
    items['TT3'] = interface.create_rectangle(
            ox_V3, oy_reservoir-tl, 3*q, oy_reservoir+tl,
            outline='black', fill='yellow', width=tw
            )

    # valves #
    items['VT12'] = create_valve(interface, ox_V1, oy_reservoir, rayon_valve, 'VT12')
    items['VT23'] = create_valve(interface, ox_V3, oy_reservoir, rayon_valve, 'VT23')
    items['V12'] = create_valve(interface, ox_V1, oy_V2, rayon_valve, 'V12')
    items['V23'] = create_valve(interface, ox_V3, oy_V2, rayon_valve, 'V23')
    items['V13'] = create_valve(interface, ox_V3, oy_V13, rayon_valve, 'V13')

    # reservoirs #
    for i in range(1, 4):
        ox = q*(i)
        tag_Ri = f'R{i}'
        tag_Pi1 = f'P{i}1'
        tag_Pi2 = f'P{i}2'

        items[tag_Ri], items[tag_Pi1], items[tag_Pi2] = create_reservoir(interface,
                ox, oy_reservoir, hauteur_reservoir, largeur_reservoir, i
                )
        items[f'M{i}'] = create_moteur(interface,
                ox, oy_moteur, hauteur_reservoir, largeur_reservoir/2, i
                )


    ### boutons reset et menu ###
    rayon_bouton = Longueur/20
    interface.create_oval(
            7*Longueur/8-rayon_bouton, oy_moteur-rayon_bouton,
            7*Longueur/8+rayon_bouton, oy_moteur+rayon_bouton,
            tags='menu', outline=COULEUR_TEXTE, fill=COULEUR_FOND
            )
    interface.create_text(
            7*Longueur/8, oy_moteur,
            text="MENU", fill=COULEUR_TEXTE, tags='menu'
            )
    interface.tag_bind('menu', '<Button-1>', lambda e: root.ouvre_menu())
    interface.tag_bind('menu', '<Enter>', lambda e: root.config(cursor="hand1"))
    interface.tag_bind('menu', '<Leave>', lambda e: root.config(cursor=''))

    interface.create_oval(
            Longueur/8-rayon_bouton, oy_moteur-rayon_bouton,
            Longueur/8+rayon_bouton, oy_moteur+rayon_bouton,
            tags='reset', outline=COULEUR_TEXTE, fill=COULEUR_FOND
            )
    items['timer/reset'] = interface.create_text(
            Longueur/8, oy_moteur,
            text="MENU", fill=COULEUR_TEXTE, tags='reset'
            )
    
    return interface

####################
## LOGIN / SIGNIN ##
####################

def verifcreer(root):
    """Vérifie les données du pseudo et mot de passe dans Creer
    pour savoir comment agir selon le cas"""
    global pseudo
    res = root.entryPseudo.get()
    resmdp = root.entryMdp.get()
    esp = " "
    compt = 0
    with open(profils, 'r') as f:
        line = f.readline()
        lines = f.readlines()
    if (esp in res) or (esp in resmdp):
        compt = 1
        errorcreer(compt)
    elif res == resmdp:
        compt = 2
        errorcreer(compt)
    elif len(resmdp)==0:
        compt = 3
        errorcreer(compt)
    else :
        if len(line) >= 3:
            for elt in lines:
                pseudo, mdp, score = elt.split(' ')
                if pseudo == res:
                    errorcreer(compt)
                    return
        with open(profils, 'a') as f:
            f.write(res + " " + resmdp + " 0\n")
        pseudo = res
        exo()




def verifconnecter(root):
    """Vérifie les données du pseudo et mot de passe dans Connecter
    pour savoir comment agir selon le cas"""
    global pseudo
    res = root.entryPseudo.get()
    resmdp = root.entryMdp.get()
    esp = " "
    compt = 0
    if (esp in res) or (esp in resmdp):
        compt = 1
        errorconnecter(compt)
        return
    with open(profils, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if len(line) <= 1:
            errorconnecter(compt)
            break
        else :
            for line in lines:
                pseudo, mdp, score = line.split(' ')
                if pseudo == res and mdp != resmdp:
                    compt = 2
                    errorconnecter(compt)
                    break
                elif pseudo == res and mdp == resmdp:
                    exo()
                    break
    errorconnecter(compt)

def errorcreer(compt):
    """Affiche le bon message d'erreur pour Creer"""
    if compt == 1 :
        root.labelErrorCreer.configure(text="Vous ne pouvez pas mettre d'espace.\n Veuillez réessayer.")
    elif compt == 2 :
        root.labelErrorCreer.configure(text="Vous ne pouvez pas avoir le même pseudo et mot de passe.\n"
                                         "Veuillez réessayer.")
    elif compt == 3 :
        root.labelErrorCreer.configure(text="Veuillez entrer un mot de passe.")
    else :
        root.labelErrorCreer.configure(text="Vous avez déjà un compte, ou ce pseudo est déjà pris.\n"
                "Veuillez retourner sur le menu d'identification avec [Echap]\n"
                " afin de vous connecter, ou réessayer.")

def errorconnecter(compt):
    """Affiche le bon message d'erreur pour Connecter"""
    if compt == 1 :
        root.labelErrorConnecter.configure(text="Vous ne pouvez pas mettre d'espace.\n Veuillez réessayer.")
    elif compt == 2 :
        root.labelErrorConnecter.configure(text="Le mot de passe est invalide.\n Veuillez réessayer.")
    else :
        root.labelErrorConnecter.configure(text="Votre profil n'existe pas.\n Veuillez réessayer ou v"
                                           "ous créer un compte en retournant\n sur le menu "
                                           "d'identification avec [Echap].")


#####################
## PARTIE EXERCICE ##
#####################

def timer(t):
    """Minuteur de la partie exercice, complète l'historique également"""
    if t%2:
        resultat = avion.update()
        if resultat == 'x':
            avion.historique.append("x| Système non corrigé à temps")
    if avion.note <= 0 or t == 0:
        root.ouvre_fin()
        return
    elif t > 3:
        #if choice((1, 0, 0, 0)):
        if t%6 == 1:
            avion.panne_aleatoire()
            update_interface(root.interface)
    root.timer = root.after(1000, timer, t-1)
    root.interface.itemconfig(items['timer/reset'], text=str(t-1))


def exo():
    """Appelle les fonctions nécessaires à la partie exercice"""
    reset_interface()
    root.ouvre_exercice()
    timer(TIMER_EXERCICE)

###########################
## CRÉATION DES FENÊTRES ##
###########################

def tableau_de_bord(root):
    """Création du tableau de bord permettant d'activer/désactiver
    les pompes et d'ouvrir/fermer les réservoirs"""
    global dashboard
    dashboard = tk.Toplevel(root)
    dashboard.title("Tableau de Bord")
    dashboard.iconphoto(False, tk.PhotoImage(file='Tableau_icon.png'))
    dashboard.resizable(False, False)
    dashboard.configure(bg=COULEUR_FOND)
    dashboard.bind('<Escape>', lambda e: root.ouvre_menu())
    dashboard.protocol("WM_DELETE_WINDOW", root.ouvre_menu)

    # Valves reservoirs -> reservoirs #
    for i, vt in enumerate(("VT12", "VT23")):
        tk.Button(
            dashboard, command=lambda vt=vt: switch_valve(vt),
            text=vt, bg=couleur_bg, fg=couleur_fg,
            font=font, relief=bouton_relief, highlightthickness=2
        ).grid(row=0, column=i * 3, columnspan=3, padx=10, pady=10)

    # Pompes secours #
    for i, p in enumerate(("P12", "P22", "P32")):
        tk.Button(
            dashboard, command=lambda i=i: switch_pompe_secours(i),
            text=p, bg=couleur_bg, fg=couleur_fg,
            font=font, relief=bouton_relief, highlightthickness=2
        ).grid(row=1, column=i * 2, columnspan=2, padx=10, pady=10)

    # Valves reservoirs -> moteurs #
    for i, v in enumerate(("V12", "V13", "V23")):
        tk.Button(
            dashboard, command=lambda v=v: switch_valve(v),
            text=v, bg=couleur_bg, fg=couleur_fg,
            font=font, relief=bouton_relief, highlightthickness=2
        ).grid(row=2, column=i * 2, columnspan=2, padx=10, pady=10)


def simuler(root):
    """Affiche l'interface à jour pour simuler grâce à un bouton"""
    interface = etat_systeme(root)
    update_interface(interface)
    return interface


def menu(root):
    """Création de l'interface du menu principal"""
    panMenu = tk.Frame(root, bg=COULEUR_FOND)

    tk.Label(
            panMenu, text="Avion Simulateur", bg=COULEUR_FOND,
            fg=COULEUR_TEXTE, font=("system", "30")
            ).pack(pady=10)
    
    tk.Button(
            panMenu, text="Simulateur", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=root.ouvre_simuler
            ).pack(pady=10)

    tk.Button(
            panMenu, text="Exercice", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=root.ouvre_exercer
            ).pack(pady=10)
    
    tk.Button(
            panMenu, text="Scores", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=root.ouvre_score
            ).pack(pady=10)

    tk.Button(
            panMenu, text="Historique", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=lambda: webbrowser.open(os.path.realpath('historique'))
            ).pack(pady=10)
    
    tk.Button(
            panMenu, text="Quitter", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=lambda: root.quit()
            ).pack(pady=10)

    return panMenu


def exercer(root):
    """Création de la première interface Exercice, où l'utilisateur
    choisit entre se connecter ou créer son profil"""
    panIdentification = tk.Frame(root, bg=COULEUR_FOND)

    tk.Button(
            panIdentification, text="Se connecter", font=fonte,
            bg=COULEUR_FOND, fg=COULEUR_TEXTE, command=root.ouvre_authentification
            ).pack(pady=70)
    tk.Button(
            panIdentification, text="Créer son profil", font=fonte,
            bg=COULEUR_FOND, fg=COULEUR_TEXTE, command=root.ouvre_creation
            ).pack(pady=20)

    return panIdentification


def authentification(root):
    """Création de l'interface pour se connecter"""
    global mdp
    panAuthentification = tk.Frame(root, bg=COULEUR_FOND)

    tk.Label(
            panAuthentification, text="Pseudo",
            font=fonte, bg=COULEUR_FOND, fg=COULEUR_TEXTE
            ).pack(pady=5)
    
    root.entryPseudoConnecter = tk.Entry(
            panAuthentification, width=15,
            font=fonte, bg='gray', fg=COULEUR_TEXTE
            )
    root.entryPseudoConnecter.insert(tk.END, pseudo)
    root.entryPseudoConnecter.pack(pady=5)
    
    tk.Label(
            panAuthentification, text="Mot de passe",
            font=fonte, bg=COULEUR_FOND, fg=COULEUR_TEXTE
            ).pack(pady=5)
    
    root.entryMdpConnecter = tk.Entry(
            panAuthentification, textvariable=mdp, show='*',
            width=15, font=fonte, bg='gray', fg=COULEUR_TEXTE
            )
    root.entryMdpConnecter.insert(tk.END, mdp)
    root.entryMdpConnecter.pack(pady=5)

    tk.Button(
            panAuthentification, text="Entrer", font=fonte,
            bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            command=lambda: verifconnecter(root)
            ).pack(pady=10)
    
    root.labelErrorConnecter = tk.Label(
            panAuthentification, text="", font=("Rockwell", "13"),
            bg=COULEUR_FOND, fg="red"
            )
    root.labelErrorConnecter.pack(pady=10)

    return panAuthentification


def creer(root):
    """Création de l'interface pour créer son compte"""
    global mdp
    panCreation = tk.Frame(root, bg=COULEUR_FOND)

    labelPseudo = tk.Label(
            panCreation, text="Pseudo",
            font=fonte, bg=COULEUR_FOND, fg=COULEUR_TEXTE
            ).pack(pady=5)

    root.entryPseudo = tk.Entry(
            panCreation, width=15,
            font=fonte, bg='gray', fg=COULEUR_TEXTE
            )
    root.entryPseudo.insert(tk.END, pseudo)
    root.entryPseudo.pack(pady=5)
    
    tk.Label(
            panCreation, text="Mot de passe",
            font=fonte, bg=COULEUR_FOND, fg=COULEUR_TEXTE
            ).pack(pady=5)

    root.entryMdp = tk.Entry(
            panCreation, textvariable=mdp, show='*',
            width=15, font=fonte, bg='gray', fg=COULEUR_TEXTE
            )
    root.entryMdp.insert(tk.END, mdp)
    root.entryMdp.pack(pady=5)

    tk.Button(
            panCreation, text="Entrer", font=fonte, bg=COULEUR_FOND,
            fg=COULEUR_TEXTE, command=lambda: verifcreer(root)
            ).pack(pady=5)

    root.labelErrorCreer = tk.Label(
            panCreation, text="", font=("Rockwell", "13"),
            bg=COULEUR_FOND, fg="red"
            )
    root.labelErrorCreer.pack(pady=10)

    return panCreation


def score(root):
    """Création de la fenêtre Scores pour le bouton correspondant, là où
    sont affichés les scores"""
    global texte
    panScore = tk.Frame(root, bg=COULEUR_FOND)

    # scrollbar #
    scrollbar = tk.Scrollbar(panScore, orient='vertical')
    scrollbar.pack(side = 'right', fill = 'y')

    # texte #
    root.texte = tk.Text(panScore, font=fonte, bg=COULEUR_FOND, fg=COULEUR_TEXTE, yscrollcommand=scrollbar.set)
    scrollbar.config(command=root.texte.yview)
    root.texte.pack(side='top')
    
    # retour #
    tk.Button(
            panScore, text="Retour", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=root.ouvre_menu
            ).pack(expand=True, fill='y', side='bottom')

    return panScore


def fin_exercice(root):
    """Affiche le score obtenu par l'utilisateur après s'être exercé,
    avec un bouton réessayer ou retour au menu"""
    panFin = tk.Frame(root, bg=COULEUR_FOND)

    root.pseudoFrame = tk.LabelFrame(
            panFin, bg=COULEUR_FOND,
            font=fonte, fg=COULEUR_TEXTE
            )
    root.pseudoFrame.pack(pady=40)
    
    root.noteLabel = tk.Label(
            root.pseudoFrame,
            bg=COULEUR_FOND, fg=COULEUR_TEXTE, font=fonte
            )
    root.noteLabel.pack(pady=10, padx=10)
    
    tk.Button(
            panFin, text="Réessayer", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=lambda: exo()
            ).pack(pady=10)
    
    tk.Button(
            panFin, text="Menu", bg=COULEUR_FOND, fg=COULEUR_TEXTE,
            font=fonte, command=root.ouvre_menu
            ).pack(pady=10)
    
    return panFin


########################
## CHANGEMENT FENÊTRE ##
########################

class Root(tk.Tk):

    def ferme_fenetres(self):
        """Ferme toutes les fenetres"""
        try:
            dashboard.destroy()
        except: None
        for frame in self.frames.values(): frame.forget()


    def ouvre_menu(self):
        """Affiche le menu quand sollicité"""
        self.ferme_fenetres()
        self.title('Menu')
        self.geometry(str(WIDTH)+"x"+str(HEIGHT))
        self.iconphoto(False, tk.PhotoImage(file='Avion_icon.png'))
        self.frames['menu'].pack()
        try:
            self.after_cancel(self.timer)
        except: None


    def ouvre_simuler(self):
        """Affiche la simulation quand sollicitée et permet
        l'activation de différents widgets"""
        global items
        self.ferme_fenetres()
        self.title("Etat du systeme")
        self.geometry(str(Longueur+4) + "x" + str(Hauteur+4))
        self.iconphoto(False, tk.PhotoImage(file='Etat_icon.png'))
        tableau_de_bord(self)
        self.interface.itemconfig(items['timer/reset'], text="RESET")

        # binds bouton reset #
        self.interface.tag_bind('reset', '<Button-1>', lambda e: reset_interface())
        self.interface.tag_bind('reset', '<Enter>', lambda e: self.config(cursor="hand1"))
        self.interface.tag_bind('reset', '<Leave>', lambda e: self.config(cursor=''))

        for i in range(1, 4):
            tag_Ri = f'R{i}'
            tag_Pi1 = f'P{i}1'
            tag_Pi2 = f'P{i}2'

            # binds reservoirs #
            self.interface.tag_bind(tag_Ri, '<Button-1>', lambda e, i=i: vide_reservoir(i))
            self.interface.tag_bind(tag_Ri, '<Enter>', lambda e: self.config(cursor="crosshair"))
            self.interface.tag_bind(tag_Ri, '<Leave>', lambda e: self.config(cursor=''))

            # binds pompes #
            self.interface.tag_bind(tag_Pi1, '<Button-1>', lambda e, i=i: panne_pompe(i*10+1))
            self.interface.tag_bind(tag_Pi1, '<Enter>', lambda e: self.config(cursor="crosshair"))
            self.interface.tag_bind(tag_Pi1, '<Leave>', lambda e: self.config(cursor=''))

            # binds pompes #
            self.interface.tag_bind(tag_Pi2, '<Button-1>', lambda e, i=i: panne_pompe(i*10+2))
            self.interface.tag_bind(tag_Pi2, '<Enter>', lambda e: self.config(cursor="crosshair"))
            self.interface.tag_bind(tag_Pi2, '<Leave>', lambda e: self.config(cursor=''))
        self.interface.pack()


    def ouvre_exercice(self):
        """Affiche l'état du système quand sollicité et permet l'activation
        de différents widgets"""
        global items
        self.ferme_fenetres()
        self.title("Etat du systeme")
        self.geometry(str(Longueur+4) + "x" + str(Hauteur+4))
        self.iconphoto(False, tk.PhotoImage(file='Etat_icon.png'))
        self.interface.itemconfig(items['timer/reset'], text=str(TIMER_EXERCICE))
        
        # unbinds bouton reset #
        self.interface.tag_unbind('reset', '<Button-1>')
        self.interface.tag_unbind('reset', '<Enter>')
        self.interface.tag_unbind('reset', '<Leave>')

        for i in range(1, 4):
            tag_Ri = f'R{i}'
            tag_Pi1 = f'P{i}1'
            tag_Pi2 = f'P{i}2'
            
            # unbinds reservoirs #
            self.interface.tag_unbind(tag_Ri, '<Button-1>')
            self.interface.tag_unbind(tag_Ri, '<Enter>')
            self.interface.tag_unbind(tag_Ri, '<Leave>')

            # unbinds pompes #
            self.interface.tag_unbind(tag_Pi1, '<Button-1>')
            self.interface.tag_unbind(tag_Pi1, '<Enter>')
            self.interface.tag_unbind(tag_Pi1, '<Leave>')

            # unbinds pompes #
            self.interface.tag_unbind(tag_Pi2, '<Button-1>')
            self.interface.tag_unbind(tag_Pi2, '<Enter>')
            self.interface.tag_unbind(tag_Pi2, '<Leave>')
        self.interface.pack()

        tableau_de_bord(self)


    def ouvre_exercer(self):
        """Affiche l'interface permettant de choisir de se connecter ou créer son profil"""
        self.ferme_fenetres()
        self.title("Exercice")
        self.frames['exercer'].pack()


    def ouvre_authentification(self):
        """Affiche l'interface pour se connecter"""
        self.ferme_fenetres()
        self.title("Se connecter")
        self.iconphoto(False, tk.PhotoImage(file='idd_icon.png'))
        self.geometry(str(WIDTH+70) + "x" + str(HEIGHT-45))
        self.labelErrorConnecter.configure(text='')
        self.entryMdpConnecter.delete(0,"end")
        self.entryPseudoConnecter.delete(0,"end")
        self.frames['authentification'].pack()


    def ouvre_creation(self):
        """Affiche l'interface pour créer son compte"""
        self.ferme_fenetres()
        self.title("Créer son profil")
        self.iconphoto(False, tk.PhotoImage(file='idd_icon.png'))
        self.geometry(str(WIDTH+70) + "x" + str(HEIGHT-45))
        self.entryMdp.delete(0,"end")
        self.entryPseudo.delete(0,"end")
        self.frames['creation'].pack()


    def ouvre_score(self):
        """Affiche l'interface des scores"""
        self.ferme_fenetres()
        self.title("Tableau des scores")
        self.iconphoto(False, tk.PhotoImage(file='score_icon.png'))
        self.geometry(str(WIDTH) + "x" + str(HEIGHT))
        update_fenetre_score(self.texte)
        self.frames['score'].pack()


    def ouvre_identification(self):
        """"Affiche l'interface permettant de se connecter ou de créer son profil"""
        self.ferme_fenetres()
        self.title("Identification")
        self.iconphoto(False, tk.PhotoImage(file='idd_icon.png'))
        self.geometry(str(WIDTH+70) + "x" + str(HEIGHT-45))
        self.frames['identification'].pack()


    def ouvre_fin(self):
        """ Affiche le pannel contenant le résultat de l'utilisateur """
        self.ferme_fenetres()
        self.pseudoFrame.configure(text=pseudo)
        note = avion.note if avion.note > 0 else 0
        self.noteLabel.configure(text=f"Note : {note}/10")
        self.frames['fin'].pack()
        update_score(pseudo)
        sauvegarde_historique(pseudo, avion.historique, note)


    def quit(self):
        """Quitte l'application"""
        self.destroy()


def sauvegarde_historique(pseudo, historique, note):
    """Garde une trace de l'historique dans son dossier"""
    date = datetime.now().strftime("%Y_%m_%d_%H_%M")
    with open(f"historique/{pseudo}_{date}.txt", 'x') as file:
        file.write(f"Légende :\no = évènement du système\n"
                "v = bon choix de l'utilisateur\nx = mauvais choix de l'utilisateur\n\n")
        file.write(f"Historique de l'exercice effectué par {pseudo}\n")
        file.write(f"Note : {note}/10\n")
        file.write('\n'.join(historique))


def update_score(pseudo):
    """Mets à jour le score dans le fichier : on choisit le score le plus haut"""
    with open(profils, 'r') as file:
        lignes = file.readlines()
    with open(profils, 'w') as file:
        for ligne in lignes:
            psd, mdp, scr = ligne.split(' ')
            if psd == pseudo and (int(scr) < avion.note):
                file.write(f"{psd} {mdp} {avion.note}\n")
            else: file.write(ligne)


def update_fenetre_score(texte):
    """Affiche le score dans Scores si il y en a un"""
    texte.delete("1.0", "end")
    with open(profils, 'r') as f:
        line = f.readline()
        lines = f.readlines()
        if len(line)<3:
            texte.insert(tk.END, "Aucun score à afficher.")
        else :
            for ligne in lines:
                psd, mdp, scr = ligne.split(' ')
                texte.insert(tk.END, f"{psd} {scr}")


##########
## MAIN ##
##########

def main():
    """Création de l'interface de base"""
    global root, frames
    root = Root()
    root.resizable(False, False)
    root.configure(bg=COULEUR_FOND)

    root.interface = simuler(root)

    root.frames = {
            'menu': menu(root),
            'simuler': root.interface,
            'score': score(root),
            'exercer': exercer(root),
            'creation': creer(root),
            'authentification': authentification(root),
            'fin': fin_exercice(root)
            }

    root.ouvre_menu()
    root.bind('<Escape>', lambda e: root.ouvre_menu())
    root.mainloop()

if __name__ == '__main__':
    avion = Avion()
    main()
