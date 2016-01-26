""" Rendering and User Input Functions, such as menus and GUI """

import libtcodpy as libtcod
import textwrap
import gvar

def render_all():
	""" |  Main rendering method.
		|  Recomputes the FOV.
		|  Renders the map and all objects.
		|  Then blits all to the main console.
		|  Also Renders the GUI to gvar.panel
	"""

	from utils import get_distance, fov_distance_coef, is_visible
	from mapcreation import Circle

	#Recompute FOV if needed
	if gvar.fov_recompute:
			gvar.fov_recompute = False
			libtcod.map_compute_fov(gvar.fov_map, gvar.game.player.x, gvar.game.player.y, gvar.game.player.fighter.fov(), True, libtcod.FOV_PERMISSIVE(5))
			libtcod.map_compute_fov(gvar.foh_map, gvar.game.player.x, gvar.game.player.y, gvar.game.player.fighter.foh(), True, libtcod.FOV_PERMISSIVE(5))
			player_fov_distance = max(int(gvar.game.player.fighter.skills["Awareness"] + gvar.game.player.fighter.perception)-1, 3)
			gvar.fovmap_override = Circle(gvar.game.player.x, gvar.game.player.y, player_fov_distance)

	#Render the Map
	mapObject = gvar.game.player.currentmap()
	map = mapObject.map

	apply_screen_impact()

	for y in range(gvar.MAP_HEIGHT):
		for x in range(gvar.MAP_WIDTH):
			visible = is_visible((x, y))
			if not visible or gvar.admin.light_all:
				if map[x][y].explored or gvar.admin.light_all:
					libtcod.console_put_char_ex(gvar.con, x, y, map[x][y].char, map[x][y].color * 0.2, libtcod.BKGND_NONE)
			else:
				libtcod.console_put_char_ex(gvar.con, x, y, map[x][y].char, map[x][y].color * fov_distance_coef((x, y)), libtcod.BKGND_NONE)
				if fov_distance_coef((x, y)) > 0.2:
					map[x][y].explored = True

	#Render all objects, after that rerender the player
	for object in gvar.game.player.currentmap().objects:
		object.draw()
	gvar.game.player.draw()

	#Apply to main Console
	libtcod.console_blit(gvar.con, 0, 0, gvar.SCREEN_WIDTH, gvar.SCREEN_HEIGHT, 0, 0, 0)

	#Render GUI
	libtcod.console_set_default_background(gvar.panel, libtcod.black)
	libtcod.console_clear(gvar.panel)
	render_messages()



	#Player's Stats
	render_health_levels()
	#Dungeon Level
 	libtcod.console_print_ex(gvar.panel, 1, 2, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon Level: ' + str(gvar.game.player.currentLevel))
	#Experience Points
	libtcod.console_print_ex(gvar.panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Experience: ')
	libtcod.console_set_default_foreground(gvar.panel, libtcod.desaturated_yellow)
	libtcod.console_print_ex(gvar.panel, 15, 3, libtcod.BKGND_NONE, libtcod.LEFT, str(gvar.game.player.exp))

	libtcod.console_blit(gvar.panel, 0, 0, gvar.SCREEN_WIDTH, gvar.PANEL_HEIGHT, 0, 0, gvar.PANEL_Y)


def apply_screen_impact():
	""" |  Render the whole screen in the color set in gvar.screen_impact
		|  and fade out.
	"""
	if gvar.screen_impact is not None:
		color = libtcod.color_lerp(libtcod.black, gvar.screen_impact[0], float(gvar.screen_impact[1]))
		libtcod.console_set_default_background(gvar.con, color)
		libtcod.console_rect(gvar.con, 1, 1, gvar.SCREEN_WIDTH, gvar.SCREEN_HEIGHT, False, libtcod.BKGND_SET)
		gvar.screen_impact[1] -= 0.25
		if gvar.screen_impact[1] < 0:
			gvar.screen_impact = None




def message(new_msg, color = libtcod.white):
	""" |  Show a message in the message log
		|  split the message if necessary, among multiple lines
	"""

	new_msg_lines = textwrap.wrap(new_msg, gvar.MSG_WIDTH)
	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(gvar.game.game_msgs) == gvar.MSG_HEIGHT:
			del gvar.game.game_msgs[0]
		gvar.game.game_msgs.append( (line, color) )



def render_messages():
	""" Render Game messages, with fading color """
	y = 1
	coef = 1
	for (line, color) in reversed(gvar.game.game_msgs):
		libtcod.console_set_default_foreground(gvar.panel, color*coef)
		libtcod.console_print_ex(gvar.panel, gvar.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
		coef -= 0.2
		y += 1

	y = gvar.PANEL_HEIGHT - 3
	coef = 1
	for roll in reversed(gvar.game.last_die_rolls):
		render_dice_rolls(y, roll)
		coef -= 0.2
		y += 1



def render_health_levels():
	""" Renders the player's health levels at a fixed position """
	libtcod.console_set_default_foreground(gvar.panel, libtcod.white)
	libtcod.console_print_ex(gvar.panel, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Health: ')
	libtcod.console_set_default_foreground(gvar.panel, libtcod.white)
	libtcod.console_print_ex(gvar.panel, 9, 1, libtcod.BKGND_SET, libtcod.LEFT, "-"+str(gvar.game.player.fighter.health_penalty())+":")
	pos = 13
	for level in [0, 1, 2, 3]:
		if gvar.game.player.fighter.hl[level] <= 0:
			libtcod.console_set_default_foreground(gvar.panel, libtcod.darker_red)
		else:
			libtcod.console_set_default_foreground(gvar.panel, libtcod.white)
		libtcod.console_print_ex(gvar.panel, pos, 1, libtcod.BKGND_SET, libtcod.LEFT, str(gvar.game.player.fighter.hl[level]))
		pos += 1



def render_dice_rolls(y, roll):
	""" Renders the last Die rolls the player has made. """
	x = 1
	#Print Roll Label
	libtcod.console_set_default_foreground(gvar.panel, libtcod.white)
	while len(roll[2]) < 6:
		roll[2] += ' '
	libtcod.console_print_ex(gvar.panel, x, y, libtcod.BKGND_SET, libtcod.LEFT, str(roll[2]) + ' - ')
	x += len(roll[2]) + 3

	#Print Successes
	libtcod.console_set_default_foreground(gvar.panel, libtcod.yellow)
	libtcod.console_print_ex(gvar.panel, x, y, libtcod.BKGND_SET, libtcod.LEFT, str(roll[0]) + ': ')
	x += len(str(roll[0])) + 2

	#Print Individual Dice
	libtcod.console_set_default_foreground(gvar.panel, libtcod.white)
	for die in roll[1]:
		libtcod.console_print_ex(gvar.panel, x, y, libtcod.BKGND_SET, libtcod.LEFT, str(die))
		x += 2



def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
	""" |  Renders a bar (HP, experience, etc)
		|  Not currently used, but could be used in the future again
	"""
	bar_width = int(float(value) / maximum * total_width)
	libtcod.console_set_default_background(gvar.panel, back_color)
	libtcod.console_rect(gvar.panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
	libtcod.console_set_default_background(gvar.panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(gvar.panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
	libtcod.console_set_default_foreground(gvar.panel, libtcod.white)
	libtcod.console_print_ex(gvar.panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))



def menu_supplement(text, x, y):
	""" Adds a text at the given position to the menu, not overwriting anything. """
 	height = gvar.SCREEN_HEIGHT
 	libtcod.console_set_default_foreground(gvar.window, libtcod.white)
 	libtcod.console_print_ex(gvar.window, x, y, libtcod.BKGND_NONE, libtcod.LEFT, text)



def menu(header, options, width, color=None, text_color=libtcod.white, alpha=1, center=False, additional_line=0, option_descriptions=None, flush=True, hidden=False, xOffset=0, yOffset=0):
	""" |  Render a Full-Screen menu, overwriting the console.
		|  @TODO Add multi-page support
	"""

	if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

	header_height = libtcod.console_get_height_rect(gvar.con, 0, 0, width, gvar.SCREEN_HEIGHT, header)+1
 	height = gvar.SCREEN_HEIGHT

 	if flush == True:
 		gvar.window = libtcod.console_new(gvar.SCREEN_WIDTH, gvar.SCREEN_HEIGHT)

	if not hidden:

		#print the background
		libtcod.console_set_default_foreground(gvar.window, text_color)
		if color is not None:
			libtcod.console_set_default_background(gvar.window, color)
			libtcod.console_rect(gvar.window, 1, 1, gvar.SCREEN_WIDTH-2, height-2, False, libtcod.BKGND_SET)
		#print the header with separating line
		if header != '':
			libtcod.console_print_rect_ex(gvar.window, 2, 2, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
			libtcod.console_hline(gvar.window,1,header_height+1,gvar.SCREEN_WIDTH-2,libtcod.BKGND_NONE)

		#print options
		y = header_height+2
		letter_index = ord('a')
		for option_text in options:
			index = options.index(option_text)
			if index == additional_line and additional_line != 0:
				libtcod.console_hline(gvar.window,1,y,gvar.SCREEN_WIDTH-2,libtcod.BKGND_NONE)
				y+= 1
			text = chr(letter_index).upper() + ' - ' + option_text
			libtcod.console_print_ex(gvar.window, 2, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
			if option_descriptions is not None:
				libtcod.console_print_ex(gvar.window, 25, y, libtcod.BKGND_NONE, libtcod.LEFT, option_descriptions[index])
			y += 1
			letter_index += 1

	#blit the contents of "window" to the root console
	if center == True:
		x = (gvar.SCREEN_WIDTH/2 - width/2)-2
		y = (gvar.SCREEN_HEIGHT/2 - height/2)-2
	else:
		x=0
		y=0

	libtcod.console_blit(gvar.window, 0, 0, width, height, 0, xOffset+x, yOffset+y, 1.0, alpha)

	#present the root console to the player and wait for a key-press
	libtcod.console_flush()
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	key_pressed = libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS,key,mouse,True)
	if not key_pressed:
		return None

	if key.vk == libtcod.KEY_F10:
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	if key.vk == libtcod.KEY_ESCAPE:
		return 'exit'

	#convert the ASCII code to an index; if it corresponds to an option, return it
	index = key.c - ord('a')
	if index >= 0 and index < len(options): return index
	return None



def inventory_menu(header):
	""" |  Show a menu with each item of the inventory as an option,
		|  separating equipped items from others.
		|  Derives from menu()
	"""

	line_pos = 0
	equipcount = 0
	if len(gvar.game.player.inventory) == 0:
		options = ['Inventory is empty.']
	else:
		options = []
		for item in gvar.game.player.inventory:
			text = item.name
			if item.item.count > 1:
				text = text + ' (' + str(item.item.count) + ')'
			if item.equipment and item.equipment.is_equipped:
				text = text + ' (equipped on ' + item.equipment.slot
				for key in item.equipment.bonus.keys():
   					text = text + ' ' + key + ':' + str(item.equipment.bonus[key])
   				text = text + ')'
				equipcount += 1
			else:
				if line_pos == 0 and equipcount > 0:
					line_pos = gvar.game.player.inventory.index(item)
			options.append(text)

	index = menu(header, options, gvar.SCREEN_WIDTH, color=libtcod.darker_grey, additional_line=line_pos, alpha=0.7)
	if index == 'exit':
		return

	#if an item was chosen, return it
	if index is None or len(gvar.game.player.inventory) == 0: return None
	return gvar.game.player.inventory[index].item



def stat_menu():
	""" |  Shows a menu displaying the Player's Stats and a possibility to distribute EXP Points.
		|  Derives from menu()
	"""

	libtcod.console_clear(gvar.window)
	text = 'Skills:\n\n'
	text2 = ''
	for skill in sorted(gvar.game.player.fighter.skills):
		text += ' ' + skill + '\n'
		text2 += str(gvar.game.player.fighter.skills[skill]) + '\n'
	menu_supplement(text, gvar.SCREEN_WIDTH/2, 2)
	menu_supplement(text2, gvar.SCREEN_WIDTH/2 + 15, 4)
	return menu('Character Sheet\n\nExperience: ' + str(gvar.game.player.exp) +
		'\n\nHealth Levels:' +
		'\n-0: ' + str(gvar.game.player.fighter.max_hl[0]) +
		'\n-1: ' + str(gvar.game.player.fighter.max_hl[1]) +
		'\n-2: ' + str(gvar.game.player.fighter.max_hl[2]) +
		'\n-4: ' + str(gvar.game.player.fighter.max_hl[3]) +
		'\n\nStrength:  ' + str(gvar.game.player.fighter.strength) +
		'\nDexterity: ' + str(gvar.game.player.fighter.dexterity) +
		'\nStamina:   ' + str(gvar.game.player.fighter.stamina) +
		'\n\nSoak (B/L): ' + str(gvar.game.player.fighter.bashing_soak()) + '/' + str(gvar.game.player.fighter.lethal_soak()) +
		'\nDodge DV: ' + str(gvar.game.player.fighter.dodgeDV()) +
		'\n\n\n\n\n\n\n\n\n\n\n\n', ['Distribute experience points'], gvar.SCREEN_WIDTH, libtcod.darker_grey, flush=False)



def admin_menu():
	""" Shows an admin menu fpr debugging purposes """
	libtcod.console_clear(gvar.window)
	menu_supplement("Current Dungeon: " + str(gvar.game.player.currentmap().owner.id), 2, gvar.SCREEN_HEIGHT-2)
	choice = menu('Admin Menu', ['Toggle FOV'], gvar.SCREEN_WIDTH, libtcod.desaturated_red, flush=False)
	if choice == 0:
		gvar.admin.light_all = False if gvar.admin.light_all else True

def animate_background(animation_name, duration, reverse=False):
	""" |  Blits images with names on a range from *animation_name*_0 to *animation_name*_x onto the screen
		|  with given *duration*. x is the amount of files in the assets/images/<animation_name>/ directory.
		|  The *reverse*-Flag reverses the animation
	"""
	import os, os.path
	from time import sleep

	end = len([name for name in os.listdir('./assets/images/' + animation_name + '/')])
	for i in range(0, end):
		if reverse:
			i = end - i -1
		libtcod.image_blit_2x(libtcod.image_load("assets/images/" + animation_name + '/' + animation_name + '_' + str(i) + '.png'),gvar.window, 0, 0)
		libtcod.console_blit(gvar.window, 0, 0, gvar.SCREEN_WIDTH, gvar.SCREEN_HEIGHT, 0, 0, 0, 1.0, 1)
		libtcod.console_flush()
		sleep(float(duration) / float(end))
