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

# Position et rayon de la boule
arbres = []
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
    'epee_or': 0
}
couleurs_ressources = {
    'bois': (139, 69, 19),
    'pierre': (128, 128, 128),
    'or': (255, 215, 0),
    'stick': (160, 82, 45),
    'pioche_bois': (205, 133, 63),
    'pioche_pierre': (100, 100, 100),
    'stick_pierre': (80, 80, 80),
    'epee_pierre': (120, 120, 120),
    'epee_or': (255, 223, 0)
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
drag_offset = (0, 0)
matrice_craft = [[None for _ in range(3)] for _ in range(3)]

def degats_joueur():
    if inventaire['epee_or'] > 0:
        return 10
    elif inventaire['epee_pierre'] > 0:
        return 5
    elif inventaire['stick_pierre'] > 0:
        return 2
    elif inventaire['stick'] > 0:
        return 1
    else:
        return 0

# Boucle principale
en_cours = True
while en_cours:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			en_cours = False
		# Gestion du clic sur le carré inventaire
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			mx, my = event.pos
			if rect_inventaire.collidepoint(mx, my):
				menu_ouvert = not menu_ouvert
			# Drag depuis inventaire (menu ouvert)
			if menu_ouvert:
				font = pygame.font.Font(None, 28)
				y_inv = rect_menu.y + 30
				for res in inventaire:
					rect_res = pygame.Rect(rect_menu.x + 20, y_inv, 28, 28)
					if rect_res.collidepoint(mx, my) and inventaire[res] > 0:
						ressource_drag = res
						drag_offset = (mx - rect_res.x, my - rect_res.y)
					y_inv += 35
				# Drag depuis matrice de craft
				case_size = 40
				mat_x = rect_menu.x + 220
				mat_y = rect_menu.y + 40
				for row in range(3):
					for col in range(3):
						rect_case = pygame.Rect(mat_x + col*case_size, mat_y + row*case_size, case_size, case_size)
						if rect_case.collidepoint(mx, my) and matrice_craft[row][col]:
							ressource_drag = matrice_craft[row][col]
							drag_offset = (mx - rect_case.x, my - rect_case.y)
							# Réajoute la ressource à l'inventaire immédiatement
							inventaire[ressource_drag] += 1
							matrice_craft[row][col] = None
							break
		# Drop sur matrice ou inventaire
		if event.type == pygame.MOUSEBUTTONUP and ressource_drag:
			mx, my = pygame.mouse.get_pos()
			case_size = 40
			mat_x = rect_menu.x + 220
			mat_y = rect_menu.y + 40
			dropped = False
			# Drop sur matrice
			for row in range(3):
				for col in range(3):
					rect_case = pygame.Rect(mat_x + col*case_size, mat_y + row*case_size, case_size, case_size)
					if rect_case.collidepoint(mx, my):
						if matrice_craft[row][col] is None and inventaire[ressource_drag] > 0:
							matrice_craft[row][col] = ressource_drag
							inventaire[ressource_drag] -= 1
						dropped = True
						break
			# Drop sur inventaire
			font = pygame.font.Font(None, 28)
			y_inv = rect_menu.y + 30
			for res in inventaire:
				rect_res = pygame.Rect(rect_menu.x + 20, y_inv, 28, 28)
				if rect_res.collidepoint(mx, my):
					inventaire[ressource_drag] += 1
					dropped = True
					break
				y_inv += 35
			ressource_drag = None
		# Drag en cours (affichage visuel)

	# Gestion des touches
	touches = pygame.key.get_pressed()
	if touches[pygame.K_LEFT]:
		x -= vitesse
		direction = 'left'
	elif touches[pygame.K_RIGHT]:
		x += vitesse
		direction = 'right'
	elif touches[pygame.K_UP]:
		y -= vitesse
		direction = 'up'
	elif touches[pygame.K_DOWN]:
		y += vitesse


		direction = 'down'
	# gestion du portail (changement de monde)
	if (x - porte_x)**2 + (y - porte_y)**2 < (rayon + 30)**2:
		if monde == MONDE_INITIAL:
			monde = MONDE_ANIMALE
		else:
			monde = MONDE_INITIAL
		x, y = LARGEUR // 2, HAUTEUR // 2
		reset_map(monde)
		time.sleep(0.2)  # évite de repasser instantanément le portail


    # gestion spawn arbres
	# Spawn arbres
	if (time.time() - temps_spawn_arbre > 5) and (len(arbres) < 10):
		temps_spawn_arbre = time.time()
		arbres.append([random.randint(0, LARGEUR), random.randint(0, HAUTEUR), None])

	# Spawn pierres
	if (time.time() - temps_spawn_pierre > 7) and (len(pierres) < 5):
		temps_spawn_pierre = time.time()
		pierres.append([random.randint(0, LARGEUR), random.randint(0, HAUTEUR), None])

	# Spawn or
	if (time.time() - temps_spawn_or > 30) and (len(ors) < 1):
		temps_spawn_or = time.time()
		ors.append([random.randint(0, LARGEUR), random.randint(0, HAUTEUR), None])

	# Gestion des monstres uniquement dans le monde animal 
	if monde == MONDE_ANIMALE:
        # Spawn loups
		if (time.time() - temps_spawn_loup > 20) and (len(loups) < 3):
			temps_spawn_loup = time.time()
			dir_x, dir_y = random_direction()
			loups.append([random.randint(0, LARGEUR), random.randint(0, HAUTEUR), dir_x, dir_y, time.time(), 30, 0])

        # Spawn araignées
		# Araignées : [x, y, dir_x, dir_y, last_dir_change, pv, dernier_degats]
		if (time.time() - temps_spawn_araignee > 20) and (len(araignees) < 3):
			temps_spawn_araignee = time.time()
			dir_x, dir_y = random_direction()
			araignees.append([random.randint(0, LARGEUR), random.randint(0, HAUTEUR), dir_x, dir_y, time.time(), 20, 0])

        # Déplacement aléatoire des loups
		for loup in loups[:]:
			dist = ((x - loup[0])**2 + (y - loup[1])**2)**0.5
			# Dégâts au joueur
			if dist < rayon + 20:
				if time.time() - loup[6] > 1:
					pv_joueur -= 3
					loup[6] = time.time()
			# Dégâts au loup si contact et joueur a une arme
			if dist < rayon + 20 and degats_joueur() > 0:
				if time.time() - dernier_degats_loup > 1:
					loup[5] -= degats_joueur()
					dernier_degats_loup = time.time()
			# Mort du loup
			if loup[5] <= 0:
				loups.remove(loup)
				continue
			# Déplacement
			if dist < 100:
				dx = x - loup[0]
				dy = y - loup[1]
				norm = max(1, (dx**2 + dy**2)**0.5)
				loup[0] += int(3 * dx / norm)
				loup[1] += int(3 * dy / norm)
			else:
				if time.time() - loup[4] > 5:
					loup[2], loup[3] = random_direction()
					loup[4] = time.time()
				loup[0] += loup[2] * 0.07
				loup[1] += loup[3] * 0.07
			loup[0] = max(0, min(LARGEUR, loup[0]))
			loup[1] = max(0, min(HAUTEUR, loup[1]))


        # --- Combat et dégâts des araignées ---
		for araignee in araignees[:]:
			dist = ((x - araignee[0])**2 + (y - araignee[1])**2)**0.5
			# Dégâts au joueur
			if dist < rayon + 20:
				if time.time() - araignee[6] > 1:
					pv_joueur -= 1
					araignee[6] = time.time()
			# Dégâts à l'araignée si contact et joueur a une arme
			if dist < rayon + 20 and degats_joueur() > 0:
				if time.time() - dernier_degats_araignee > 1:
					araignee[5] -= degats_joueur()
					dernier_degats_araignee = time.time()
			# Mort de l'araignée
			if araignee[5] <= 0:
				araignees.remove(araignee)
				continue
			# Déplacement
			if dist < 100:
				dx = x - araignee[0]
				dy = y - araignee[1]
				norm = max(1, (dx**2 + dy**2)**0.5)
				araignee[0] += int(3 * dx / norm)
				araignee[1] += int(3* dy / norm)
			else:
				if time.time() - araignee[4] > 5:
					araignee[2], araignee[3] = random_direction()
					araignee[4] = time.time()
				araignee[0] += araignee[2] * 0.07
				araignee[1] += araignee[3] * 0.07
			araignee[0] = max(0, min(LARGEUR, araignee[0]))
			araignee[1] = max(0, min(HAUTEUR, araignee[1]))
		
	# Gestion bucheronnage
	indices_a_supprimer = []
	for i in range(len(arbres)):
		xa, ya, debut_buch = arbres[i]
		if (x - xa)**2 + (y - ya)**2 < (rayon + 10)**2:
			if debut_buch is None:
				arbres[i][2] = time.time()
			elif time.time() - debut_buch > 3:
				inventaire['bois'] += 1
				indices_a_supprimer.append(i)
		else:
			arbres[i][2] = None
	for index in sorted(indices_a_supprimer, reverse=True):
		arbres.pop(index)

	# Gestion minage pierre
	indices_pierre_supprimer = []
	for i in range(len(pierres)):
		xp, yp, debut_mine = pierres[i]
		if (x - xp)**2 + (y - yp)**2 < (rayon + 10)**2:
			if inventaire['pioche_bois'] > 0 or inventaire['pioche_pierre'] > 0:
				if debut_mine is None:
					pierres[i][2] = time.time()
				elif time.time() - debut_mine > 3:
					inventaire['pierre'] += 1
					indices_pierre_supprimer.append(i)
			else:
				font = pygame.font.Font(None, 28)
				txt = font.render("Besoin d'une pioche en bois!", True, (255, 0, 0))
				fenetre.blit(txt, (LARGEUR//2 - 100, HAUTEUR//2 + 120))
		else:
			pierres[i][2] = None
	for index in sorted(indices_pierre_supprimer, reverse=True):
		pierres.pop(index)
    # Gestion minage or
	indices_or_supprimer = []
	for i in range(len(ors)):
		xo, yo, debut_or = ors[i]
		if (x - xo)**2 + (y - yo)**2 < (rayon + 10)**2:
			if inventaire['pioche_pierre'] > 0:
				if debut_or is None:
					ors[i][2] = time.time()
				elif time.time() - debut_or > 3:
					inventaire['or'] += 1
					indices_or_supprimer.append(i)
			else:
				font = pygame.font.Font(None, 28)
				txt = font.render("Besoin d'une pioche en pierre!", True, (255, 0, 0))
				fenetre.blit(txt, (LARGEUR//2 - 100, HAUTEUR//2 + 120))
		else:
			ors[i][2] = None

	for index in sorted(indices_or_supprimer, reverse=True):
		ors.pop(index)
    # Dessin
	fenetre.fill(BLANC)
	arbre_img = pygame.image.load('arbre.png')
	pierre_img = pygame.image.load('pierre.png')
	or_img = pygame.image.load('or.png')
	# Dessin arbres
	for arbre in arbres:
		xa, ya, _ = arbre
		fenetre.blit(arbre_img, (xa - arbre_img.get_width()//2, ya - arbre_img.get_height()//2))
	# Dessin pierres
	for pierre_ in pierres:
		xp, yp, _ = pierre_
		fenetre.blit(pierre_img, (xp - pierre_img.get_width()//2, yp - pierre_img.get_height()//2))
	# Dessin or
	for oritem in ors:
		xo, yo, _ = oritem
		fenetre.blit(or_img, (xo - or_img.get_width()//2, yo - or_img.get_height()//2))
	
	# Dessin du portail
	fenetre.blit(porte_img, (porte_x - porte_img.get_width()//2, porte_y - porte_img.get_height()//2))

    # Dessin des monstres si monde animal
	if monde == MONDE_ANIMALE:
		for loup in loups:
			fenetre.blit(loup_img, (loup[0] - loup_img.get_width()//2, loup[1] - loup_img.get_height()//2))
		for araignee in araignees:
			fenetre.blit(araignee_img, (araignee[0] - araignee_img.get_width()//2, araignee[1] - araignee_img.get_height()//2))

	# Animation du personnage
	frame_timer += 1
	if frame_timer >= 10:
		frame_index = (frame_index + 1) % len(frames)
		frame_timer = 0
	fenetre.blit(frames[direction][frame_index], (x - rayon, y - rayon))

	# Affichage du carré inventaire en bas à gauche
	pygame.draw.rect(fenetre, (200, 200, 200), rect_inventaire)
	font = pygame.font.Font(None, 24)
	texte_inv = font.render("Inv.", True, (0, 0, 0))
	fenetre.blit(texte_inv, (rect_inventaire.x + 5, rect_inventaire.y + 15))

	# --- Affichage de la barre de PV du joueur ---
	bar_x = rect_inventaire.x + rect_inventaire.width + 20
	bar_y = rect_inventaire.y + 10
	bar_largeur = 100
	bar_hauteur = 20
	pygame.draw.rect(fenetre, (180, 0, 0), (bar_x, bar_y, bar_largeur, bar_hauteur))  # fond rouge
	pv_largeur = int(bar_largeur * pv_joueur / 100)
	pygame.draw.rect(fenetre, (0, 200, 0), (bar_x, bar_y, pv_largeur, bar_hauteur))   # barre verte
	font_pv = pygame.font.Font(None, 22)
	txt_pv = font_pv.render(f"{pv_joueur}/100 PV", True, (0, 0, 0))
	fenetre.blit(txt_pv, (bar_x + 10, bar_y + 2))

	# Affichage du menu central si ouvert
	if menu_ouvert:
		pygame.draw.rect(fenetre, (220, 220, 220), rect_menu)
		pygame.draw.rect(fenetre, (0, 0, 0), rect_menu, 2)
		# Inventaire à gauche avec carré coloré
		font = pygame.font.Font(None, 28)
		y_inv = rect_menu.y + 30
		ressources_affichees = list(inventaire.keys())
		# Flèches haut/bas
		rect_up = pygame.Rect(rect_menu.x + 20, y_inv - 25, 28, 20)
		rect_down = pygame.Rect(rect_menu.x + 20, y_inv + nb_affichees*35, 28, 20)
		pygame.draw.rect(fenetre, (180,180,180), rect_up)
		pygame.draw.rect(fenetre, (180,180,180), rect_down)
		font_scroll = pygame.font.Font(None, 20)
		fenetre.blit(font_scroll.render('▲', True, (0,0,0)), (rect_up.x+7, rect_up.y))
		fenetre.blit(font_scroll.render('▼', True, (0,0,0)), (rect_down.x+7, rect_down.y))
		# Affichage ressources scrollées
		for idx, res in enumerate(ressources_affichees[scroll_offset:scroll_offset+nb_affichees]):
			rect_res = pygame.Rect(rect_menu.x + 20, y_inv + idx*35, 28, 28)
			pygame.draw.rect(fenetre, couleurs_ressources.get(res, (100, 100, 100)), rect_res)
			txt = font.render(f"{res} : {inventaire[res]}", True, (0, 0, 0))
			fenetre.blit(txt, (rect_menu.x + 55, y_inv + idx*35))
		# Matrice 3x3 à droite
		case_size = 40
		mat_x = rect_menu.x + 220
		mat_y = rect_menu.y + 40
		for row in range(3):
			for col in range(3):
				rect_case = pygame.Rect(mat_x + col*case_size, mat_y + row*case_size, case_size, case_size)
				pygame.draw.rect(fenetre, (180, 180, 180), rect_case)
				pygame.draw.rect(fenetre, (0, 0, 0), rect_case, 2)
				# Affiche la ressource déposée (remplit toute la case)
				res_case = matrice_craft[row][col]
				if res_case:
					pygame.draw.rect(fenetre, couleurs_ressources.get(res_case, (100, 100, 100)), rect_case)
		# Bouton "Créer"
		bouton_rect = pygame.Rect(mat_x, mat_y + 3*case_size + 20, case_size*3, 35)
		pygame.draw.rect(fenetre, (100, 200, 100), bouton_rect)
		txt_bouton = font.render("Créer", True, (0, 0, 0))
		fenetre.blit(txt_bouton, (bouton_rect.x + 30, bouton_rect.y + 5))

		
		if rect_up.collidepoint(mx, my) and scroll_offset > 0:
			scroll_offset -= 1
		if rect_down.collidepoint(mx, my) and scroll_offset < len(ressources_affichees) - nb_affichees:
			scroll_offset += 1

		# Drag visuel
		if ressource_drag:
			mx, my = pygame.mouse.get_pos()
			pygame.draw.rect(fenetre, couleurs_ressources.get(ressource_drag, (100, 100, 100)), (mx - drag_offset[0], my - drag_offset[1], 28, 28))

		# Gestion du craft stick
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			if bouton_rect.collidepoint(mx, my):
				recette_stick = [[None, 'bois', None], [None, 'bois', None], [None, 'bois', None]]
				recette_pioche_bois = [['bois', 'bois', 'bois'], [None, 'stick', None], [None, 'stick', None]]
				recette_pioche_pierre = [['pierre', 'pierre', 'pierre'], [None, 'stick', None], [None, 'stick', None]]
				recette_stick_pierre = [[None, 'pierre', None], [None, 'pierre', None], [None, 'pierre', None]]
				recette_epee_pierre = [[None, 'pierre', None], [None, 'pierre', None], [None, 'stick', None]]
				recette_epee_or = [[None, 'or', None], [None, 'or', None], [None, 'stick_pierre', None]]

				if matrice_craft == recette_stick:
					inventaire['stick'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_pioche_bois:
					inventaire['pioche_bois'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_pioche_pierre:
					inventaire['pioche_pierre'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_stick_pierre:
					inventaire['stick_pierre'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_epee_pierre:
					inventaire['epee_pierre'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_epee_or:
					inventaire['epee_or'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
	pygame.display.flip()

pygame.quit()







