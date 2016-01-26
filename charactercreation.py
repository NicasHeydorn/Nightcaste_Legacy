import gvar
import libtcodpy as libtcod

def create_character():
	""" |  Inits the Stats of the player
		|  and controls menu flow of the character creation process
	"""

	reset_attributes()

	attrs = distribute_attributes()
	if attrs == 'exit':
		return 'exit'
	else:
		skills = distribute_skills()
		if skills == 'exit':
			return 'exit'
		elif skills == 'back':
			create_character()



def reset_attributes():
	""" Resets the attributes of the player Object to 1 """

	gvar.game.player.fighter.strength = 1
	gvar.game.player.fighter.dexterity = 1
	gvar.game.player.fighter.stamina = 1
	gvar.game.player.fighter.perception = 1
	gvar.game.player.fighter.intelligence = 1
	gvar.game.player.fighter.wits = 1



def distribute_attributes():
	""" |  Shows a menu for distributing attribute points
		|  and continue until attribute points are depleted
	"""
	from render import menu, menu_supplement, animate_background

	animate_background("attributes", .6)
	attributes_points = 6
	reset_attributes()
	while attributes_points > 0:
		libtcod.console_clear(gvar.window)

		#Rendered Output
		menu_supplement("Points remaining: " + chr(246)*attributes_points + chr(9)*(6-attributes_points), 5, gvar.SCREEN_HEIGHT - 5)
		i=0
		for attribute in ["STR", "DEX", "STA"]:
			menu_supplement("PHYSICAL", 12, 9)
			menu_supplement(chr(65+i) + " - " + attribute, 9, 12+i)
			attributes = gvar.game.player.fighter.get_attributes('physical')
			attribute_score = attributes[i]
			for o in range(attribute_score):
				menu_supplement(chr(246), 18+o, 12+i)
			for u in range(5-attribute_score):
				menu_supplement(chr(9), 18+attribute_score+u, 12+i)
			i+=1

		menu_supplement("SOCIAL", 36, 9)
		menu_supplement("coming soon", 34, 12)

		i=0
		for attribute in ["PER", "INT", "WIT"]:
			menu_supplement("MENTAL", 59, 9)
			menu_supplement(chr(68+i) + " - " + attribute, 56, 12+i)
			attributes = gvar.game.player.fighter.get_attributes('mental')
			attribute_score = attributes[i]
			for o in range(attribute_score):
				menu_supplement(chr(246), 65+o, 12+i)
			for u in range(5-attribute_score):
				menu_supplement(chr(9), 65+attribute_score+u, 12+i)
			i+=1

		# Dummy Menu
		attributes_choice = menu("",
			["", "", "", "", "", ""],
			gvar.SCREEN_WIDTH,
			alpha=0,
			flush=False,
			hidden=True)

		if attributes_choice == 0 and gvar.game.player.fighter.strength < 5:
			gvar.game.player.fighter.strength += 1
		elif attributes_choice == 1 and gvar.game.player.fighter.dexterity < 5:
			gvar.game.player.fighter.dexterity += 1
		elif attributes_choice == 2 and gvar.game.player.fighter.stamina < 5:
			gvar.game.player.fighter.stamina += 1
		elif attributes_choice == 3 and gvar.game.player.fighter.perception < 5:
			gvar.game.player.fighter.perception += 1
		elif attributes_choice == 4 and gvar.game.player.fighter.intelligence < 5:
			gvar.game.player.fighter.intelligence += 1
		elif attributes_choice == 5 and gvar.game.player.fighter.wits < 5:
			gvar.game.player.fighter.wits += 1
		elif attributes_choice == 'exit':
			return 'exit'
		else:
			continue
		attributes_points -= 1

def distribute_skills():
	""" |  Shows a menu to distribute skill points
		|  until skill points are depleted
		|  resetting skill points to prevent cheating
		|  Not all skills are listed here yet, because not all skills are implemented
	"""
	from render import menu, menu_supplement, animate_background

	animate_background("abilities", .6)

	for skill in gvar.game.player.fighter.skills: 		# Reset Skill points
		gvar.game.player.fighter.skills[skill] = 0
	skill_points = 10			# Points to be distributed
	skill_limit = 3				# Maximum skill level
	skills = ['Martial-Arts',	# Available Skills
			 'Melee',
			 'Archery',
			 'Athletics',
			 'Awareness',
			 'Dodge',
			 'Resistance',
			 'Medicine']
	descriptions = []
	for skill in skills:
		descriptions.append(0)
	while skill_points > 0:

		#Rendered Output
		menu_supplement("Points remaining: " + chr(246)*skill_points + chr(9)*(10-skill_points), 5, gvar.SCREEN_HEIGHT - 5)

		i=0
		for skill in skills:
			menu_supplement(chr(65+i) + " - " + skill, 20, 12+i)
			skill_score = gvar.game.player.fighter.skills[skill]
			for o in range(skill_score):
				menu_supplement(chr(246), 39+o, 12+i)
			for u in range(5-skill_score):
				menu_supplement(chr(9), 39+skill_score+u, 12+i)
			i+=1


		# Dummy Menu
		skill_choice = menu("",
			["", "", "", "", "", "", "", ""],
			gvar.SCREEN_WIDTH,
			alpha=0,
			flush=False,
			hidden=True)

		if skill_choice == 'exit':
			skill_points = 0
			return 'exit'
			break
		elif skill_choice >= 0 and skill_choice < len(skills):
			if gvar.game.player.fighter.skills[skills[skill_choice]] < 3:
				gvar.game.player.fighter.skills[skills[skill_choice]] += 1
			else:
				continue
		else:
			continue
		skill_points -= 1
