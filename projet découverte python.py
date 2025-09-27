# importation de pygame
import pygame
import time
import random
import os
print(os.listdir())
# Initialisation de pygame
pygame.init()

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
}# Chaque arbre/pierre/or est un tuple (x, y, debut_collecte)
arbres = []
temps_spawn_arbre = time.time()
pierres = []
temps_spawn_pierre = time.time()
ors = []
temps_spawn_or = time.time()

# Variables pour le menu
menu_ouvert = False
rect_inventaire = pygame.Rect(10, HAUTEUR - 60, 50, 50)  # carré en bas à gauche
rect_menu = pygame.Rect(LARGEUR//2 - 200, HAUTEUR//2 - 150, 400, 300)  # menu central
# Drag & drop
ressource_drag = None
drag_offset = (0, 0)
matrice_craft = [[None for _ in range(3)] for _ in range(3)]

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

#test pour verifier si ca marche


