""" Game mechanics, such as Attacks, Death, Spells, Step functions """

import libtcodpy as libtcod
import gvar

def player_move_or_attack(dx, dy):
	""" Move the player to the given direction. If a mob is found there, attack it. """
	x = gvar.game.player.x + dx
	y = gvar.game.player.y + dy

	#try to find an attackable object there
	target = None
	for object in gvar.game.player.currentmap().objects:
		if object.fighter and object.x == x and object.y == y:
			target = object
			break

	#attack if target found, move otherwise
	if target is not None:
		speed = gvar.game.player.fighter.attack(target.fighter)
		return speed
	else:
		gvar.game.player.move(dx, dy)
		gvar.fov_recompute = True
		return gvar.game.player.fighter.movement_speed()



#Use functions

def open_door(x, y):
	""" |  Use function:
		|  Open the door. Set the Character to '/', tile_type to 'door' and do not block or block_sight.
		|  Also, checks direct adjacent (not diagonal) tiles for doors, and opens them too. (As if they were double doors.)
	"""
	from nightcaste import initialize_fov
	map = gvar.game.player.currentmap()
	tile = map.map[x][y]
	if tile is not None and tile.tile_type == 'door':
		tile.blocked = False
		tile.block_sight = False
		tile.char = '/'
		#double doors
		for t in map.adjacent(x, y, diagonal=False):
			next_tile = map.map[t[0]][t[1]]
			if next_tile.tile_type == 'door':
				next_tile.blocked = False
				next_tile.block_sight = False
				next_tile.char = '/'
	initialize_fov()


#Step Functions
#They always have the entity argument,
#indicating who is stepping on the Tile

def fall_into(entity):
	""" |  Step function:
		|  Fall into a hole. Takes an entity (player, mob) as input.
		|  Rolls Wits + Awareness to determine, if they see the hole.
		|  If they do and there is a ledge near (not diagonally), do a reflexive Wits+Awareness roll, to determine if they can hang down the ledge.
		|  Otherwise, kill them.
	"""
	from utils import d10, is_player
	from render import message

	map = entity.currentmap()
	result = d10(entity.fighter.wits + entity.fighter.skills["Awareness"], 'Fall:', botchable=True, player=is_player(entity))
	if result[0] <= 3:
		ledge = False
		for spot in map.adjacent(entity.x, entity.y, diagonal=False):
			if map.map[spot[0]][spot[1]].tile_type == 'floor':
				ledge = True
		if ledge:
			#ledge near, do a reflex roll to catch it
			reflex = d10(entity.fighter.wits + entity.fighter.skills["Awareness"],'Reflex:', botchable=True, player=is_player(entity))
			if reflex[0] >= 2:
				if not is_player:
					message(entity.name + " is hanging down the ledge", libtcod.white)
				else:
					message("You are hanging down the ledge", libtcod.white)
			else:
				if not is_player:
					message(entity.name + " has fallen down the hole", libtcod.red)
				else:
					message("You have fallen down the hole", libtcod.red)
					entity.fighter.death_function(entity)
		else:
			#no ledge near
			if not is_player:
				message(entity.name + " has fallen down the hole", libtcod.red)
			else:
				message("You have fallen down the hole", libtcod.red)
			entity.fighter.death_function(entity)
	else:
		if not is_player:
			message(entity.name + " is hanging down the ledge", libtcod.white)
		else:
			message("You are hanging down the ledge", libtcod.white)



#Death Functions

def player_death(player):
	""" |  Death function for the player.
		|  Set game state to 'dead' and turn the player into a corpse.
	"""
	from render import message
	message('You died!', libtcod.red)
	gvar.game.game_state = 'dead'
	gvar.game.player.char = '%'
	gvar.game.player.color = libtcod.dark_red



def mob_death(mob):
	""" |  Death function for mobs.
		|  Turns the mob into a corpse. It doesn't block, has no AI and Fighter components.
		|  Also, add the mob's EXP value to the player's.
	"""
	from render import message
	message(mob.name.capitalize() + ' is dead!', libtcod.orange)
	mob.char = '%'
	mob.color = libtcod.dark_red
	mob.blocks = False
	mob.fighter = None
	mob.ai = None
	mob.name = 'remains of ' + mob.name
	mob.send_to_back()
	gvar.game.player.exp += mob.exp
	message('Gained ' + str(mob.exp) + ' EXP!')




#Spells and Effects

def cast_heal(min, max, mutableBySkill=True):
	""" |  **Spells and Effects: Heal player**
		|  Heal the player by a random value between *min* and *max* boundaries.
		|  If *mutableBySkill* is true, the player's Medicine skill adds to the boundaries.
	"""
	from render import message

	message('You start to feel better!', libtcod.light_violet)
	modifier = 0
	if mutableBySkill:
		modifier = libtcod.random_get_int(0, 0, gvar.game.player.fighter.skills['Medicine'])
	gvar.game.player.fighter.heal(libtcod.random_get_int(0, min, max) + modifier)



def cast_lightning(min, max):
	""" |  **Spells and Effects: Lightning**
		|  Cast a lightning and deal a random amount of Lethal damage inside the given *min* and *max* boundaries.
		|  The target is the closest mob inside a radius of 5 fields.
	"""
	from utils import closest_mob
	from render import message

	mob = closest_mob(5)
	if mob is None:
		message('No enemy is close enough to strike.', libtcod.red)
		return 'cancelled'
 	damage = libtcod.random_get_int(0, min, max)
	message('A lighting bolt strikes the ' + mob.name + '! The damage is '
		+ str(damage) + ' Lethal HL.', libtcod.light_blue)
	mob.fighter.take_damage(damage)



def cast_confusion(min, max):
	""" |  **Spells and Effects: Confusion**
		|  Apply a 'confusion' status to the closes mob within 5 fields.
		|  A confused enemy moves into a random direction every time it takes a turn.
		|  Also, it doesn't react to ai_blocked tiles, so it can fall down a hole.
	"""
	from utils import closest_mob
	from render import message

	mob = closest_mob(5)
	if mob is None:
		message('No enemy is close enough to target.', libtcod.red)
		return 'cancelled'

	message('A violet smoke appears around the ' + mob.name + '! It\'s confused.', libtcod.violet)
	mob.ai.applyStatus('confusion', libtcod.random_get_int(0,min,max))



def cast_fireball(min, max, explosion_radius=2):
	""" |  **Spells and Effects: Fireball.**
		|  Target a tile within the FOV with and cast a fireball with given explosion *radius* onto the targeted tile.
		|  Deal damage equal to a random value inside the *min* and *max* boundaries.
	"""
	from input import target_tile
	from render import message

	target = target_tile(radius=explosion_radius)
	if target == 'cancelled':
		return'cancelled'
	if target is not None:
		for hit in gvar.game.objects:
			for p in target.splash.circle:
				if hit.fighter is not None:
					if hit.fighter.hl[3] > 0:
						if hit.x == p[0] and hit.y == p[1]:
							dmg = libtcod.random_get_int(0,min,max)
							hit.fighter.take_damage(dmg)
							message('The fireball burns ' + hit.name + ' for ' + dmg + ' damage')




#Skills

def distribute_exp():
	""" Open a menu in which the player can distribute the EXP he acquired."""
	from render import menu, message
	options = ['Strength (500)', 'Dexterity (500)', 'Stamina (500)', '1 -0 Health Level (500)', '1 -1 Health Level (400)', '1 -2 Health Level (300)', '1 -4 Health Level (200)']
	choice = menu('Choose a skill point to distribute points to:', options, 50, alpha=1)
	cost = {0: 500, 1:500, 2:500, 3: 500, 4: 500, 5: 400, 6: 300, 7: 200}
	if choice is not None:
		if choice == 'exit':
			return
		if gvar.game.player.exp >= cost[choice]:
			skill = {0: gain_strength, 1: gain_dexterity, 2: gain_stamina, 3: gain_perception, 4: gain_0hl, 5:gain_1hl, 6:gain_2hl, 7:gain_4hl}
			amount = {0:1, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1}
			skill[choice](amount[choice])
			gvar.game.player.exp -= cost[choice]
			message('You feel stronger!')
		else:
			message('You don\'t have enough experience.')

def gain_strength(amount):
	gvar.game.player.fighter.base_strength += amount

def gain_dexterity(amount):
	gvar.game.player.fighter.base_dexterity += amount

def gain_stamina(amount):
	gvar.game.player.fighter.base_stamina += amount

def gain_perception(amount):
	gvar.game.player.fighter.base_perception += amount

def gain_0hl(amount):
	gvar.game.player.fighter.max_hl[0] += amount

def gain_1hl(amount):
	gvar.game.player.fighter.max_hl[0] += amount

def gain_2hl(amount):
	gvar.game.player.fighter.max_hl[0] += amount

def gain_4hl(amount):
	gvar.game.player.fighter.max_hl[0] += amount