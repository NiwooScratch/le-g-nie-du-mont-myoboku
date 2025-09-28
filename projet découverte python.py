# importation de pygame
import pygame
import time
import random
import os

print(os.listdir())
# Initialisation de pygame
pygame.init()

# Ajout des images pour le portail, loups et araignées
porte_img = pygame.image.load('porte_animale.png')
loup_img = pygame.image.load('loup.png')
araignee_img = pygame.image.load('arraigné.png')

# Définition des mondes
MONDE_INITIAL = "monde_initial"
MONDE_ANIMALE = "monde_animale"
monde = MONDE_INITIAL

# propriétés de chaque monde ---
def reset_map(monde):
    global arbres, pierres, ors, temps_spawn_arbre, temps_spawn_pierre, temps_spawn_or, loups, araignees, temps_spawn_loup, temps_spawn_araignee
    arbres = []
    pierres = []
    ors = []
    temps_spawn_arbre = time.time()
    temps_spawn_pierre = time.time()
    temps_spawn_or = time.time()
    if monde == MONDE_ANIMALE:
        loups = []
        araignees = []
        temps_spawn_loup = time.time()
        temps_spawn_araignee = time.time()
    else:
        loups = []
        araignees = []

DIRECTIONS = [
    (0, -1),   # haut
    (0, 1),    # bas
    (-1, 0),   # gauche
    (1, 0)     # droite
]

def random_direction():
    return random.choice(DIRECTIONS)

scroll_offset = 0
nb_affichees = 6  # nombre de ressources visibles dans le menu

# Dimensions de la fenêtre
LARGEUR, HAUTEUR = 800, 600
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Jeu de la boule 2D")

# Couleurs
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)

arme_distance = None  # 'arc' si sélectionné, sinon None
trait_visee = False
pos_visee = (0, 0)

# Position et rayon de la boule
import os
x, y = LARGEUR // 2, HAUTEUR // 2
rayon = 10

# Chargement des frames du personnage animé
# frames[direction][frame_index]
frames = {
    'up': [pygame.image.load(f'uppersoframe{i+1}.png') for i in range(8)],      # frames pour le haut
    'down': [pygame.image.load(f'downpersoframe{i+1}.png') for i in range(8)],    # frames pour le bas
    'left': [pygame.image.load(f'leftpersoframe{i+1}.png') for i in range(8)],    # frames pour la gauche
    'right': [pygame.image.load(f'rightpersoframe{i+1}.png') for i in range(8)]    # frames pour la droite
}
direction = 'up'  # direction par défaut

frame_index = 0
frame_timer = 0
vitesse = 1 

# Inventaire sous forme de dictionnaire
inventaire = {
    'bois': 0,
    'pierre': 0,
    'or': 0,
    'stick': 0,
    'pioche_bois': 0,
    'pioche_pierre': 0,
    'stick_pierre': 0,
    'epee_pierre': 0,
    'epee_or': 0,
    'viande': 0,
    'fil': 0,
    'arc': 0,
    'fleche_pierre': 0,
    'fleche_or': 0
}

# Couleurs des ressources — j'ai conservé et fusionné les deux versions
couleurs_ressources = {
    'bois': (139, 69, 19),
    'pierre': (128, 128, 128),
    'or': (255, 215, 0),
    'stick': (160, 82, 45),
    'pioche_bois': (205, 133, 63),
    'pioche_pierre': (100, 100, 100),
    'stick_pierre': (80, 80, 80),
    'epee_pierre': (120, 120, 120),
    'epee_or': (255, 223, 0),
    'viande': (200, 100, 80),
    'fil': (220, 220, 220),
    'arc': (120, 80, 40),
    'fleche_pierre': (100, 100, 100),
    'fleche_or': (255, 215, 0)
}

# variables de combat
pv_joueur = 100
dernier_degats_loup = 0
dernier_degats_araignee = 0

# Chaque arbre/pierre/or est un tuple (x, y, debut_collecte)
arbres = []
temps_spawn_arbre = time.time()
pierres = []
temps_spawn_pierre = time.time()
ors = []
temps_spawn_or = time.time()

#  variables pour les monstres ---
loups = []
araignees = []
temps_spawn_loup = time.time()
temps_spawn_araignee = time.time()

# Position du portail
porte_x, porte_y =  60, HAUTEUR//2 

# Variables pour le menu
menu_ouvert = False
rect_inventaire = pygame.Rect(10, HAUTEUR - 60, 50, 50)  # carré en bas à gauche
rect_menu = pygame.Rect(LARGEUR//2 - 200, HAUTEUR//2 - 150, 400, 300)  # menu central
# Drag & drop
ressource_drag = None
drag_offset =_
