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
tir_en_cours = False
tir_rouge_timer = 0
dernier_tir_ennemi = None
degats_fleche = 0
tir_touche = False
game_over = False
game_over_timer = 0
bouclier_actif = False
bouclier_leve = False

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
	'epee_or': 0,
	'viande': 0,
	'fil': 0 ,
	'arc': 0,
	'fleche_pierre': 0,
    'fleche_or': 0 ,
	'bouclier_bois': 0
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
	'epee_or': (255, 223, 0),
	'viande': (200, 100, 80),
	'fil': (220, 220, 220),
	'arc': (120, 80, 40),
    'fleche_pierre': (100, 100, 100),
    'fleche_or': (255, 215, 0),
	'bouclier_bois': (150, 120, 60)
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
	
scroll_last_pressed = False

# Boucle principale
en_cours = True
while en_cours:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			en_cours = False

		# Gestion de la visée à l'arc (affichage du trait)
		if arme_distance == 'arc' and inventaire['arc'] > 0:
			if event.type == pygame.MOUSEMOTION:
				# Limite la visée à 300 pixels
				mx, my = event.pos
				dx, dy = mx - x, my - y
				dist = (dx**2 + dy**2)**0.5
				if dist > 300:
					ratio = 300 / dist
					mx = int(x + dx * ratio)
					my = int(y + dy * ratio)
				pos_visee = (mx, my)
				trait_visee = True
			if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				trait_visee = False
			# Tir à l'arc sur ESPACE
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not tir_en_cours:
				# On ne tire que si on a des flèches
				if inventaire['fleche_or'] > 0 or inventaire['fleche_pierre'] > 0:
					dx, dy = pos_visee[0] - x, pos_visee[1] - y
					dist = (dx**2 + dy**2)**0.5
					if dist > 0:
						vx, vy = dx / dist, dy / dist
						# Cherche le premier ennemi sur la ligne de visée (tolérance 10px)
						cible = None
						cible_type = None
						cible_idx = None
						min_dist = 9999
						# Loups
						for idx, loup in enumerate(loups):
							lx, ly = loup[0], loup[1]
							proj = ((lx - x) * vx + (ly - y) * vy)
							if 0 < proj < 300:
								px, py = x + proj * vx, y + proj * vy
								d = ((lx - px)**2 + (ly - py)**2)**0.5
								if d < 15 and proj < min_dist:
									cible = loup
									cible_type = 'loup'
									cible_idx = idx
									min_dist = proj
						# Araignées
						for idx, araignee in enumerate(araignees):
							ax, ay = araignee[0], araignee[1]
							proj = ((ax - x) * vx + (ay - y) * vy)
							if 0 < proj < 300:
								px, py = x + proj * vx, y + proj * vy
								d = ((ax - px)**2 + (ay - py)**2)**0.5
								if d < 15 and proj < min_dist:
									cible = araignee
									cible_type = 'araignee'
									cible_idx = idx
									min_dist = proj
						# Si cible trouvée, prépare le tir (ligne rouge)
						if cible is not None:
							tir_en_cours = True
							tir_rouge_timer = time.time()
							tir_touche = True
							dernier_tir_ennemi = (cible_type, cible_idx)
							if inventaire['fleche_or'] > 0:
								degats_fleche = 10
								inventaire['fleche_or'] -= 1
							elif inventaire['fleche_pierre'] > 0:
								degats_fleche = 5
								inventaire['fleche_pierre'] -= 1
						else:
							# Tire sans toucher (ligne reste noire)
							if inventaire['fleche_or'] > 0:
								inventaire['fleche_or'] -= 1
							elif inventaire['fleche_pierre'] > 0:
								inventaire['fleche_pierre'] -= 1
							tir_en_cours = True
							tir_rouge_timer = time.time()
							tir_touche = False
							dernier_tir_ennemi = None
		# Gestion du clic sur le carré inventaire
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			mx, my = event.pos
			if rect_inventaire.collidepoint(mx, my):
				menu_ouvert = not menu_ouvert
			# Drag depuis inventaire (menu ouvert, version scrollable)
			if menu_ouvert:
				font = pygame.font.Font(None, 28)
				y_inv = rect_menu.y + 30
				ressources_affichees = list(inventaire.keys())
				visible_ressources = ressources_affichees[scroll_offset:scroll_offset+nb_affichees]
				for idx, res in enumerate(visible_ressources):
					rect_res = pygame.Rect(rect_menu.x + 20, y_inv + idx*35, 28, 28)
					if rect_res.collidepoint(mx, my) and inventaire[res] > 0:
						ressource_drag = res
						drag_offset = (mx - rect_res.x, my - rect_res.y)
						break
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

	# Collision avec les bords de la map
	x = max(rayon, min(LARGEUR - rayon, x))
	y = max(rayon, min(HAUTEUR - rayon, y))
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
					degat = 3
					if bouclier_actif and bouclier_leve:
						degat = degat // 2
					pv_joueur -= degat
					loup[6] = time.time()
			# Dégâts au loup si contact et joueur a une arme
			if dist < rayon + 20 and degats_joueur() > 0:
				if time.time() - dernier_degats_loup > 1:
					loup[5] -= degats_joueur()
					dernier_degats_loup = time.time()
			# Mort du loup
			if loup[5] <= 0:
				loups.remove(loup)
				inventaire['viande'] += 1  # loot viande
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
					degat = 1
					if bouclier_actif and bouclier_leve:
						degat = degat // 2
					pv_joueur -= degat
					araignee[6] = time.time()
			# Dégâts à l'araignée si contact et joueur a une arme
			if dist < rayon + 20 and degats_joueur() > 0:
				if time.time() - dernier_degats_araignee > 1:
					araignee[5] -= degats_joueur()
					dernier_degats_araignee = time.time()
			# Mort de l'araignée
			if araignee[5] <= 0:
				araignees.remove(araignee)
				inventaire['fil'] += 1  # loot fil
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

	# --- Affichage des items consommables (viande) ---
	# Affiche la viande si présente dans l'inventaire (consommable uniquement)
	if inventaire['viande'] > 0:
		viande_rect = pygame.Rect(rect_inventaire.x + 10, rect_inventaire.y - 40, 40, 40)
		pygame.draw.rect(fenetre, couleurs_ressources['viande'], viande_rect)
		font_viande = pygame.font.Font(None, 22)
		txt_viande = font_viande.render(f"Viande x{inventaire['viande']}", True, (0, 0, 0))
		fenetre.blit(txt_viande, (viande_rect.x + 2, viande_rect.y + 10))

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

	# case bouclier
	bouclier_case = pygame.Rect(bar_x + bar_largeur + 70, bar_y, 40, 40)
	pygame.draw.rect(fenetre, (220, 220, 220), bouclier_case)
	if inventaire['bouclier_bois'] > 0:
		pygame.draw.rect(fenetre, couleurs_ressources['bouclier_bois'], bouclier_case)
		font_bouclier = pygame.font.Font(None, 18)
		fenetre.blit(font_bouclier.render('Bouclier', True, (0,0,0)), (bouclier_case.x+2, bouclier_case.y+10))
		if bouclier_actif:
			pygame.draw.rect(fenetre, (0,200,255), (bouclier_case.x, bouclier_case.y, 40, 5))
	else:
		font_bouclier = pygame.font.Font(None, 18)
		fenetre.blit(font_bouclier.render('Bouclier', True, (100,100,100)), (bouclier_case.x+2, bouclier_case.y+10))

	# gstion arc
	arc_case = pygame.Rect(bar_x + bar_largeur + 20, bar_y, 40, 40)
	pygame.draw.rect(fenetre, (220, 220, 220), arc_case)
	if arme_distance == 'arc' and inventaire['arc'] > 0:
		pygame.draw.rect(fenetre, couleurs_ressources['arc'], arc_case)
		font_arc = pygame.font.Font(None, 18)
		fenetre.blit(font_arc.render('Arc', True, (0,0,0)), (arc_case.x+5, arc_case.y+10))
	else:
		font_arc = pygame.font.Font(None, 18)
		fenetre.blit(font_arc.render('Arc', True, (100,100,100)), (arc_case.x+5, arc_case.y+10))

	if arme_distance == 'arc' and inventaire['arc'] > 0:
		if event.type == pygame.MOUSEMOTION:
			trait_visee = True
			pos_visee = event.pos
		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			trait_visee = False
		if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
			dx, dy = pos_visee[0] - x, pos_visee[1] - y
			norm = max(1, (dx**2 + dy**2)**0.5)
			direction_fleche = (dx/norm, dy/norm)
			if inventaire['fleche_or'] > 0:
				inventaire['fleche_or'] -= 1
				# Ajoute ici la logique de déplacement de la flèche et collision si tu veux
			elif inventaire['fleche_pierre'] > 0:
				inventaire['fleche_pierre'] -= 1
                # Idem pour la flèche en pierre

		
	
	# Affiche le trait de visée (noir ou rouge si tir et touche)
	couleur_trait = (0,0,0)
	if tir_en_cours and tir_touche and time.time() - tir_rouge_timer < 1:
		couleur_trait = (255,0,0)
	if arme_distance == 'arc' and trait_visee:
		# Limite la portée à 300px
		dx, dy = pos_visee[0] - x, pos_visee[1] - y
		dist = (dx**2 + dy**2)**0.5
		if dist > 300:
			ratio = 300 / dist
			px = int(x + dx * ratio)
			py = int(y + dy * ratio)
			pygame.draw.line(fenetre, couleur_trait, (x, y), (px, py), 2)
		else:
			pygame.draw.line(fenetre, couleur_trait, (x, y), pos_visee, 2)
	# Affiche le nombre de flèches
	font_fleche = pygame.font.Font(None, 16)
	fenetre.blit(font_fleche.render(f"P:{inventaire['fleche_pierre']}", True, (80,80,80)), (arc_case.x, arc_case.y+35))
	fenetre.blit(font_fleche.render(f"O:{inventaire['fleche_or']}", True, (200,180,0)), (arc_case.x+20, arc_case.y+35))

	# Applique les dégâts à l'ennemi touché après 1s
	if tir_en_cours and time.time() - tir_rouge_timer >= 1:
		if tir_touche and dernier_tir_ennemi is not None:
			cible_type, cible_idx = dernier_tir_ennemi
			if cible_type == 'loup' and 0 <= cible_idx < len(loups):
				loups[cible_idx][5] -= degats_fleche
			elif cible_type == 'araignee' and 0 <= cible_idx < len(araignees):
				araignees[cible_idx][5] -= degats_fleche
		tir_en_cours = False
		dernier_tir_ennemi = None
		degats_fleche = 0
		tir_touche = False

	# Gestion Game Over
	if not game_over and pv_joueur <= 0:
		game_over = True
		game_over_timer = time.time()

	if game_over:
		# Affiche Game Over
		font_go = pygame.font.Font(None, 80)
		txt_go = font_go.render("GAME OVER", True, (200,0,0))
		fenetre.blit(txt_go, (LARGEUR//2 - txt_go.get_width()//2, HAUTEUR//2 - txt_go.get_height()//2))
		pygame.display.flip()
		if time.time() - game_over_timer > 5:
			# Reset complet
			pv_joueur = 100
			x, y = LARGEUR // 2, HAUTEUR // 2
			for k in inventaire:
				inventaire[k] = 0
			matrice_craft = [[None for _ in range(3)] for _ in range(3)]
			loups.clear()
			araignees.clear()
			arbres.clear()
			pierres.clear()
			ors.clear()
			reset_map(MONDE_INITIAL)
			monde = MONDE_INITIAL
			menu_ouvert = False
			ressource_drag = None
			trait_visee = False
			tir_en_cours = False
			tir_touche = False
			dernier_tir_ennemi = None
			degats_fleche = 0
			game_over = False
		continue

	mouse_pressed = pygame.mouse.get_pressed()
	# Affichage du menu central si ouvert
	if menu_ouvert:
		pygame.draw.rect(fenetre, (220, 220, 220), rect_menu)
		pygame.draw.rect(fenetre, (0, 0, 0), rect_menu, 2)
		# Inventaire à gauche avec carré coloré
		font = pygame.font.Font(None, 28)
		y_inv = rect_menu.y + 30
		ressources_affichees = list(inventaire.keys())
		# Slider graphique pour le scroll
		slider_x = rect_menu.x + 10 + 28 + 10
		slider_y = y_inv - 5
		slider_height = nb_affichees * 35
		slider_width = 10
		pygame.draw.rect(fenetre, (200,200,200), (slider_x, slider_y, slider_width, slider_height))
		# Taille du curseur
		total_items = len(ressources_affichees)
		if total_items > nb_affichees:
			curseur_height = max(30, int(slider_height * nb_affichees / total_items))
			max_offset = total_items - nb_affichees
			curseur_y = slider_y + int(slider_height * scroll_offset / total_items)
			curseur_rect = pygame.Rect(slider_x, curseur_y, slider_width, curseur_height)
			pygame.draw.rect(fenetre, (100,100,100), curseur_rect)
		else:
			curseur_height = slider_height
			curseur_rect = pygame.Rect(slider_x, slider_y, slider_width, curseur_height)
			pygame.draw.rect(fenetre, (100,100,100), curseur_rect)

		# Affichage ressources scrollées
		for idx, res in enumerate(ressources_affichees[scroll_offset:scroll_offset+nb_affichees]):
			rect_res = pygame.Rect(rect_menu.x + 20, y_inv + idx*35, 28, 28)
			pygame.draw.rect(fenetre, couleurs_ressources.get(res, (100, 100, 100)), rect_res)
			txt = font.render(f"{res} : {inventaire[res]}", True, (0, 0, 0))
			fenetre.blit(txt, (rect_menu.x + 55, y_inv + idx*35))

		# Gestion du slider (drag & click)
		mouse_pressed = pygame.mouse.get_pressed()
		mouse_pos = pygame.mouse.get_pos()
		if 'slider_drag' not in globals():
			slider_drag = False
			slider_drag_offset = 0
		if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[0]:
			if curseur_rect.collidepoint(mouse_pos):
				slider_drag = True
				slider_drag_offset = mouse_pos[1] - curseur_rect.y
			elif (slider_x <= mouse_pos[0] <= slider_x+slider_width) and (slider_y <= mouse_pos[1] <= slider_y+slider_height):
				# Clique sur la barre, saute à la position
				rel_y = mouse_pos[1] - slider_y
				percent = rel_y / slider_height
				scroll_offset = int(percent * (total_items - nb_affichees))
				scroll_offset = max(0, min(scroll_offset, total_items - nb_affichees))
		if event.type == pygame.MOUSEBUTTONUP:
			slider_drag = False
		if slider_drag and mouse_pressed[0]:
			rel_y = mouse_pos[1] - slider_y - slider_drag_offset + curseur_height//2
			percent = rel_y / slider_height
			scroll_offset = int(percent * (total_items - nb_affichees))
			scroll_offset = max(0, min(scroll_offset, total_items - nb_affichees))

		# Drag visuel (corrigé pour ne pas buguer avec le scroll)
		if ressource_drag:
			mx, my = pygame.mouse.get_pos()
			pygame.draw.rect(fenetre, couleurs_ressources.get(ressource_drag, (100, 100, 100)), (mx - drag_offset[0], my - drag_offset[1], 28, 28))
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
				recette_arc = [[None, 'stick', 'stick'], [None, 'fil', 'stick'], [None, 'stick', 'stick']]
				recette_fleche_pierre = [[None, 'pierre', None], [None, 'stick', None], [None, 'stick', None]]
				recette_fleche_or = [[None, 'or', None], [None, 'stick', None], [None, 'stick', None]]
				recette_bouclier_bois = [['pierre','bois','pierre'],['bois','pierre','bois'],['pierre','bois','pierre']]

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
				elif matrice_craft == recette_arc:
					inventaire['arc'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_fleche_pierre:
					inventaire['fleche_pierre'] += 4
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_fleche_or:
					inventaire['fleche_or'] += 4
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
				elif matrice_craft == recette_bouclier_bois:
					inventaire['bouclier_bois'] += 1
					matrice_craft = [[None for _ in range(3)] for _ in range(3)]
	pygame.display.flip()

	# --- Gestion de la consommation de la viande (clic sur la viande dans l'inventaire) ---
	mouse_pressed = pygame.mouse.get_pressed()
	mouse_pos = pygame.mouse.get_pos()
	if inventaire['viande'] > 0:
		viande_rect = pygame.Rect(rect_inventaire.x + 10, rect_inventaire.y - 40, 40, 40)
		if mouse_pressed[0] and viande_rect.collidepoint(mouse_pos):
			if pv_joueur < 100:
				inventaire['viande'] -= 1
				pv_joueur = min(100, pv_joueur + 10)
	
	if inventaire['arc'] > 0:
		arc_case = pygame.Rect(bar_x + bar_largeur + 20, bar_y, 40, 40)
		if mouse_pressed[0] and arc_case.collidepoint(mouse_pos):
			arme_distance = 'arc'
		
	if inventaire['bouclier_bois'] > 0:
		bouclier_case = pygame.Rect(bar_x + bar_largeur + 70, bar_y, 40, 40)
	if mouse_pressed[0] and bouclier_case.collidepoint(mouse_pos):
		bouclier_actif = True

pygame.quit()
