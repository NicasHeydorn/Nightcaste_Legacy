""" Main Module, consisting of game managing methods, such as creating a new game, saving and loading games and also the main loop. """

import libtcodpy as libtcod
import math
import pprint

import gvar
import components
import spawn
import input
import mapcreation
import render
import utils
import mechanics
import save


###############################################################
# Initialization & Main Loop
###############################################################

def new_game():
	""" |  Start a new game
		|  Create a map, FOV Map and print Welcome Mesage
	"""
	from charactercreation import create_character
	from spawn import spawn_player

	gvar.game = gvar.Game()
	gvar.game.init_world()
	spawn_player([gvar.game.world.worldspace, 0])

	initialize_fov()
	color = libtcod.color_lerp(libtcod.white, libtcod.red, 0.9)
	render.message('Welcome, Child of the Unconquered Sun.', color)
	ch = create_character()
	if ch == 'exit':
		main_menu()
	play_game()


def next_level():
	""" |  Go deeper into the Dungeon.
		|  Increase the Dungeon Level and create a new map
	"""
	gvar.game.dungeon_level += 1
	mapcreation.make_map()
	initialize_fov()

def prev_level():
	""" |  Go upstairs. Load the previous Map from the Map Storage
	"""
	gvar.game.dungeon_level -= 1


def initialize_fov():
	""" calculate FOV and FOH Maps of the Player """
	libtcod.console_clear(gvar.con)
	gvar.fov_recompute = True
	gvar.fov_map = libtcod.map_new(gvar.MAP_WIDTH, gvar.MAP_HEIGHT)
	gvar.foh_map = libtcod.map_new(gvar.MAP_WIDTH, gvar.MAP_HEIGHT)
	currentMap = gvar.game.player.currentmap().map
	for y in range(gvar.MAP_HEIGHT):
		for x in range(gvar.MAP_WIDTH):
			libtcod.map_set_properties(gvar.fov_map, x, y, not currentMap[x][y].block_sight, not currentMap[x][y].blocked)
			libtcod.map_set_properties(gvar.foh_map, x, y, True, True)



def main_menu():
	""" Display the main menu and wait for input """
	img = libtcod.image_load('menu_background1.png')

	while not libtcod.console_is_window_closed():
		#show the background image, at twice the regular console resolution
		libtcod.image_blit_2x(img, 0, 0, 0)

		choice = render.menu('Nightcaste', ['Play a new game', 'Continue last game', 'Quit'], 24)

		if choice == 0:
			new_game()
		elif choice == 1:
			try:
				save.load_game()
			except:
				render.menu('Couldnt load savegame.', ["ok"], 24)
				continue
			play_game()
		elif choice == 2:
			save.save_game()
			raise SystemExit



def play_game():
	""" Main Loop """
	player_action = None

	#Main Loop
	while not libtcod.console_is_window_closed():
		render.render_all()
		libtcod.console_flush()
		map = gvar.game.player.currentmap()
		for object in  map.objects:
			object.clear()
			if object.fighter is not None and libtcod.map_is_in_fov(gvar.foh_map, object.x, object.y) and not gvar.game.ticks.contains(object):
				object.fighter.join_battle()

		#handle death state
		if gvar.game.game_state == 'dead':
			player_action = input.handle_keys()
			if player_action == 'exit':
				save.save_game()
				break
			else:
				continue

		else:
			actor = gvar.game.ticks.getWithPriority()
			if actor[1] == gvar.game.player:
				#handle keys and exit game if needed
				player_action = input.handle_keys()
				if player_action == 'exit':
					save.save_game()
					break
				gvar.game.ticks.put(actor[1], int(player_action + actor[0]))

			else:
				#let mobs take their turn
				if gvar.game.game_state == 'playing':
					if actor[1].ai:
						speed = actor[1].ai.take_turn()
						gvar.game.ticks.put(actor[1], int(speed + actor[0]))



if __name__ == "__main__":
   libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
   libtcod.console_init_root(gvar.SCREEN_WIDTH, gvar.SCREEN_HEIGHT, 'Nightcaste', False)
   gvar.con = libtcod.console_new(gvar.MAP_WIDTH, gvar.MAP_HEIGHT)
   gvar.overlay = libtcod.console_new(gvar.MAP_WIDTH, gvar.MAP_HEIGHT)
   gvar.panel = libtcod.console_new(gvar.SCREEN_WIDTH, gvar.PANEL_HEIGHT)
   gvar.window = libtcod.console_new(gvar.SCREEN_WIDTH ,gvar.SCREEN_HEIGHT)

   #initialize mob DB
   gvar.mobdb = spawn.load_mob_db()
   gvar.itemdb = spawn.load_item_db()

   main_menu()