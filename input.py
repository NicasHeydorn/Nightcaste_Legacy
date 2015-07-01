import libtcodpy as libtcod
import gvar

def handle_keys():
	""" |  The player's main input method
		|  Returns a speed value as an integer
	"""
	from mechanics import distribute_exp, player_move_or_attack
	from render import inventory_menu, stat_menu, menu, admin_menu
	from nightcaste import next_level
	from utils import sort_inventory

	speed = 0

	key = libtcod.console_wait_for_keypress(True)

 	# Fullscreen
	if key.vk == libtcod.KEY_F10:
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

 	# Exit
	elif key.vk == libtcod.KEY_ESCAPE:
		return 'exit'

 	# Movement
	if gvar.game.game_state == 'playing':
		if libtcod.console_is_key_pressed(libtcod.KEY_UP) or libtcod.console_is_key_pressed(libtcod.KEY_KP8):
			speed = player_move_or_attack(0, -1)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) or libtcod.console_is_key_pressed(libtcod.KEY_KP2):
			speed = player_move_or_attack(0, 1)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) or libtcod.console_is_key_pressed(libtcod.KEY_KP4):
			speed = player_move_or_attack(-1, 0)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) or libtcod.console_is_key_pressed(libtcod.KEY_KP6):
			speed = player_move_or_attack(1, 0)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_KP7):
			speed = player_move_or_attack(-1, -1)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_KP9):
			speed = player_move_or_attack(1, -1)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_KP3):
			speed = player_move_or_attack(1, 1)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_KP1):
			speed = player_move_or_attack(-1, 1)
			gvar.fov_recompute = True
		elif libtcod.console_is_key_pressed(libtcod.KEY_KP5):
			speed = 1
		elif libtcod.console_is_key_pressed(libtcod.KEY_F11):
			admin_menu()
		else:
			key_char = chr(key.c)

			if key_char == 'y':		# Pick up an item
				for object in gvar.game.player.currentmap().objects:
					if object.x == gvar.game.player.x and object.y == gvar.game.player.y and object.item:
						object.item.pick_up()
						break

			if key_char == 'i':		# Show the inventory; if an item is selected, use it
				sort_inventory()
				chosen_item = inventory_menu('Inventory\nPress the key next to an item to use it, or any other to cancel.\n')
				if chosen_item is not None:
					chosen_item.use()

			if key_char == 'd':		# Show character information
				chosen_item = inventory_menu('Press the key next to an item to drop it.\n')
				if chosen_item is not None:
					chosen_item.drop()

			if key_char == 'c':		# Show character information
				choice = stat_menu()
				if choice == 0:
					distribute_exp()

			if key_char == 'e':		# Use a map tile (doors, stairs, etc.)
				x, y = target_adjacent()
				if gvar.game.player.currentmap().map[x][y].use_function is not None:
					gvar.game.player.currentmap().map[x][y].use_function(x, y)
				for object in gvar.game.player.currentmap().objects:
					if object.x == x and object.y == y:
						object.use()

			if key_char == 's':		# Ranged Attack
				speed = gvar.game.player.fighter.ranged_attack()

			if key_char == ' ':		# Jump
				direction = target_adjacent(True)
				speed = gvar.game.player.jump(direction)
				gvar.fov_recompute = True

		if speed == 'cancelled':
			return 'didnt-take-turn'
		else:
			return speed



def target_tile(max_range=None, radius=0):
	"""	|  Target a distant tile
		|  For Ranged Attacks, like Archery, Thrown
		|  Also Fireballs or similar projectiles with Radius
	"""
	from components import Object
	from mapcreation import Circle
	from render import render_all

	# Spawn a Target Object that can be moved with arrow Keys
	(x, y) = (gvar.game.player.x, gvar.game.player.y)
	target = Object(x, y, 'X', color=libtcod.red, name='target', blocks=False)
	gvar.game.objects.append(target)

	while True:
		target.send_to_front()
		render_all()

		#Render Splash
		libtcod.console_clear(gvar.overlay)
		if radius > 0:
			target.splash = Circle(target.x, target.y, radius)
			for point in target.splash.circle:
				libtcod.console_set_char_background(gvar.overlay, point[0], point[1], libtcod.yellow)
		libtcod.console_blit(gvar.overlay, 0, 0, gvar.SCREEN_WIDTH, gvar.SCREEN_HEIGHT, 0, 0, 0, 1.0, 0.5)
		libtcod.console_flush()

		#Move the Target around
		key = libtcod.console_wait_for_keypress(True)

		if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x, target.y-1):
				target.y -= 1
		elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x, target.y+1):
				target.y += 1
		elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x-1, target.y):
				target.x -= 1
		elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x+1, target.y):
				target.x += 1
		elif key.vk == libtcod.KEY_KP7:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x-1, target.y-1):
				target.x -= 1
				target.y -= 1
		elif key.vk == libtcod.KEY_KP9:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x+1, target.y-1):
				target.x += 1
				target.y -= 1
		elif key.vk == libtcod.KEY_KP3:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x+1, target.y+1):
				target.x += 1
				target.y += 1
		elif key.vk == libtcod.KEY_KP1:
			if libtcod.map_is_in_fov(gvar.fov_map, target.x-1, target.y+1):
				target.x -= 1
				target.y += 1
		elif key.vk == libtcod.KEY_ENTER:
			gvar.game.objects.remove(target)
			return target
			break
		elif key.vk == libtcod.KEY_ESCAPE:
			gvar.game.objects.remove(target)
			return 'cancelled'
			break
		elif chr(key.c) == 's':
			# Returns String 'closest' for further evaluation by the calling function, e.g. for targeting the closest mob
			gvar.game.objects.remove(target)
			return 'closest'
			break



def target_adjacent(relative=False):
	""" |  Target an adjacent tile,
		|  e.g. for using doors
		|  Returns absolute coordinates
		|  or the relative direction, if relative flag is set
	"""

	x = 0
	y = 0
	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_KP4 or key.vk == libtcod.KEY_LEFT:
		x -= 1
	elif key.vk == libtcod.KEY_KP8 or key.vk == libtcod.KEY_UP:
		y -= 1
	elif key.vk == libtcod.KEY_KP6 or key.vk == libtcod.KEY_RIGHT:
		x += 1
	elif key.vk == libtcod.KEY_KP2 or key.vk == libtcod.KEY_DOWN:
		y += 1
	elif key.vk == libtcod.KEY_KP7:
		x -= 1
		y -= 1
	elif key.vk == libtcod.KEY_KP9:
		x += 1
		y -= 1
	elif key.vk == libtcod.KEY_KP3:
		x += 1
		y += 1
	elif key.vk == libtcod.KEY_KP1:
		x -= 1
		y += 1
	elif key.vk == libtcod.KEY_KP5:
		pass

	if relative:
		return (x, y)
	else:
		return (gvar.game.player.x + x, gvar.game.player.y + y)