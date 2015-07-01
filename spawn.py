""" Methods for spawning Items, Mobs and other Entities """

import libtcodpy as libtcod
import json
import math
import pprint
import gvar



def load_mob_db():
	""" Loads the Mob DB from mobs.json """
	with open('mobs.json') as data_file:
	    return json.load(data_file)



def load_item_db():
	""" Loads the Item DB from items.json """
	with open('items.json') as data_file:
	    return json.load(data_file)


def spawn_stuff(map):
	""" Forwarding function for spawning stairs, mobs and items """
	spawn_mobs(map)
	spawn_items(map)
	spawn_upstairs(map)
	if map.owner.depth > map.level:
		spawn_downstairs(map)


def spawn_player(array_dungeon_level):
	""" |  Spawns the player on an unblocked spot in the given level of the given dungeon, or, if the level has upstairs,
		|  spawns the player at the upstairs' position
		|  Also it invokes the generation of a new random map, if the next level isn't yet defined.
	"""
	from nightcaste import initialize_fov

	dungeon = array_dungeon_level[0]
	level = array_dungeon_level[1]

	if len(dungeon.maps) <= level:
		dungeon.addRandomMap()

	map = dungeon.maps[level]
	map.objects.append(gvar.game.player)

	if map.upstairs is not None:
		player_spawn = (map.upstairs.x, map.upstairs.y)
	else:
		room = map.random_room()
		player_spawn = room.random_spot()
		while map.is_blocked(player_spawn[0], player_spawn[1], ai=True):
			room = map.random_room()
			player_spawn = room.random_spot()

	gvar.game.player.relocate(dungeon=dungeon, level=level, x=player_spawn[0], y=player_spawn[1])
	initialize_fov()



def spawn_entrance(map, x=None, y=None, dungeon=None):
	""" Spawns the entrance to a dungeon. If dungeon is not set, a randomly generated will be used. """
	from components import Object
	if dungeon is None:
		gvar.game.world.random_dungeon()
		dungeon = gvar.game.world.dungeons[len(gvar.game.world.dungeons)-1]
		dungeon.addRandomMap()

	name = 'Entrance to ' + str(dungeon.id)
	if map in dungeon.maps:
		level = dungeon.maps.index(map)
	else:
		level = 0
	map.objects.append(Object(currentDungeon=dungeon, currentLevel=level, x=2 , y=2 , char=chr(31), name=name, color=libtcod.light_turquoise, always_visible=True, use_function=spawn_player, args=[dungeon, 0]))


def spawn_upstairs(map):
	""" Spawns the stairs to the previous level, or to the worldspace, if it's the first level	"""
	from components import Object
	if map.level > 0:
		dest_dungeon = map.owner
		dest_level = map.level - 1
	else:
		dest_dungeon = gvar.game.world.worldspace
		dest_level = 0
	#choose random room
	room = map.random_room()
	(x, y) = room.random_spot()
	#guarantee that player can reach the goal
	while map.is_blocked(x, y, ai=True):
		room = map.random_room()
		(x, y) = room.random_spot()
	map.upstairs = Object(currentDungeon=map.owner, currentLevel=map.level, x=x, y=y, char=chr(30), name='stairs', color=libtcod.light_turquoise, always_visible=True, use_function=spawn_player, args=[dest_dungeon, dest_level])
	map.objects.append(map.upstairs)
	map.upstairs.send_to_back()


def spawn_downstairs(map):
	""" |  Spawns the stairs to the next level
		|  Guarantees that it is rechable from the upstairs position
	"""
	from components import Object

	#choose random room
	room = map.random_room()
	(x, y) = room.random_spot()
	#guarantee that player can reach the goal
	while map.is_blocked(x, y, ai=True) or not map.is_reachable((x, y), (map.upstairs.x, map.upstairs.y)):
		room = map.random_room()
		(x, y) = room.random_spot()
	map.downstairs = Object(currentDungeon=map.owner, currentLevel=map.level, x=x, y=y, char=chr(31), name='stairs', color=libtcod.light_turquoise, always_visible=True, use_function=spawn_player, args=[map.owner, map.level+1])
	map.objects.append(map.downstairs)
	map.downstairs.send_to_back()



def spawn_mobs(map):
	""" |  Spawns randomly distributed mobs. Mobs spawn in packs.
		|  The count and type of mobs is determined by the dungeon level.
	"""

	numberMobs = []
	for moblevel in range(7):
		numberMobs.append(chances(moblevel, map.owner.maps.index(map)+1))
	#Eliminate level 0 Mobs
	numberMobs.pop(0)
	#go through all the mob levels
	for mobcount in numberMobs:
		currentLevelMobs = gvar.mobdb[str(numberMobs.index(mobcount)+1)]
		#Mob Count is +-2 of function value
		mobcount = libtcod.random_get_int(0, mobcount-2, mobcount+2)
		#spawn packs of mobs until the count is depleted
		while mobcount != 0:
			#get random mob of this level
			mobToSpawn = currentLevelMobs[libtcod.random_get_int(0, 0, len(currentLevelMobs)-1)]

			packSize = libtcod.random_get_int(0,mobToSpawn["packsize"][0], mobToSpawn["packsize"][1])
			if packSize > mobcount:
				packSize = mobcount
 			#choose random room
 			room = map.random_room()
			#choose random spot for this pack
			(x, y) = room.random_spot()
			while map.is_blocked(x, y, ai=True):
				(x, y) = room.random_spot()
			place_mob_pack(map, x, y, mobToSpawn, packSize)
			mobcount -= packSize



def spawn_items(map):
	""" |  Spawns randomly selected Items from Item DB.
		|  The count and type of the items is determined by the dungeon level.
	"""

	numberItems = []
	for rarity in range(4):
		numberItems.append(chances(rarity, map.owner.maps.index(map)+1))
	numberItems.pop(0)

	for itemcount in numberItems:
		currentLevelItems = gvar.itemdb[str(numberItems.index(itemcount))]
		itemcount = libtcod.random_get_int(0, itemcount, itemcount+2)
		while itemcount > 0:
			itemToSpawn = currentLevelItems[libtcod.random_get_int(0, 0, len(currentLevelItems)-1)]
			room = map.random_room()
			(x, y) = room.random_spot()
			while map.is_blocked(x, y, ai=True):
				(x, y) = room.random_spot()
			if len(itemToSpawn["equipment"]) > 0:
				place_equipment(map, x, y, itemToSpawn)
			else:
				place_item(map, x, y, itemToSpawn)
			itemcount -= 1



def place_mob_pack(map, x, y, mobToSpawn, packsize):
	""" Places a pack of mobs at the given position. """
	from components import Object,Fighter,MobAI
	from mechanics import mob_death

	for mob in range(1, packsize+1):
		if map.is_blocked(x, y, ai=True):
			(x, y) = map.unblocked_spot_in(4, x, y)
		compAI = MobAI()
		mob = Object(map.owner, map.owner.maps.index(map), x, y, str(mobToSpawn["character"]), color=libtcod.Color(mobToSpawn["color"][0],mobToSpawn["color"][1],mobToSpawn["color"][2]), name=mobToSpawn["name"], blocks=True, exp=mobToSpawn["exp"], ai=compAI)
		compFighter = Fighter(
								hl=mobToSpawn["hl"],
								essence=mobToSpawn["essence"],
								strength=mobToSpawn["strength"],
								dexterity=mobToSpawn["dexterity"],
								skills=mobToSpawn["skills"],
								death_function=mob_death
							)
		mob.fighter = compFighter
		mob.fighter.owner = mob

		map.objects.append(mob)
		mob.send_to_front()



def place_item(map, x, y, itemToSpawn):
	""" Places a usable item at the given position """
	from components import Object, Item, Equipment
	import mechanics

	compItem = Item(use_function=getattr(mechanics, str(itemToSpawn["use_function"])), args=itemToSpawn["args"], count=libtcod.random_get_int(0, itemToSpawn["amount"][0], itemToSpawn["amount"][1]))
	item = Object(map.owner, map.owner.maps.index(map), x, y, str(itemToSpawn["character"]), color=libtcod.Color(itemToSpawn["color"][0], itemToSpawn["color"][1], itemToSpawn["color"][2]), name=itemToSpawn["name"], item=compItem)

	map.objects.append(item)
	item.send_to_back()



def place_equipment(map, x, y, itemToSpawn):
	""" Places a piece of equipment, that can be picked up, at the given position """
	from components import Object, Item, Equipment, Weapon, Armor, Ranged
	import mechanics

	compEquip = Equipment(
							slot=str(itemToSpawn["equipment"]["slot"])
	 					)

	if itemToSpawn["equipment"].has_key("armor"):
		armor= itemToSpawn["equipment"]["armor"]
		compEquip.armor = Armor(bashing_soak=armor["bashing_soak"],
								lethal_soak=armor["lethal_soak"],
								fatigue=armor["fatigue"],
								penalty=armor["penalty"],
								hardness=armor["hardness"])

	if itemToSpawn["equipment"].has_key("weapon"):
		weapon= itemToSpawn["equipment"]["weapon"]
		compEquip.weapon = Weapon(accuracy=weapon["accuracy"],
								damage=weapon["damage"],
								skill=weapon["skill"],
								speed=weapon["speed"])
		if "ranged" in weapon and weapon["ranged"] == True:
			compEquip.ranged = Ranged(accuracy=weapon["ranged_accuracy"],
								damage=weapon["ranged_damage"],
								skill=weapon["ranged_skill"],
								speed=weapon["ranged_speed"])

	item = Object(map.owner, map.owner.maps.index(map), x, y, str(itemToSpawn["character"]), color=libtcod.Color(itemToSpawn["color"][0], itemToSpawn["color"][1], itemToSpawn["color"][2]), name=itemToSpawn["name"], equipment=compEquip)
	map.objects.append(item)
	item.send_to_back()



def chances(level, x):
	"""	|  Returns an integer representing the count of mobs/items that will be spawned,
		|  by applying different functions, depending on dungeon_level and mob level.
		|  http://fooplot.com/plot/1nydnisrci
		|  x = dungeon level
		|  level = mob/item level
	"""

	func1 = 0.85*x + 8
	func2 = 0.6*x + 3.5
	func3 = 0.5*x
	func4 = 0.33*x
	func5 = 0.2*x

	if level == 1:
		return int(func1) if func1 > 0 else 0
	elif level == 2:
		return int(func2) if func2 > 0 else 0
	elif level == 3:
		return int(func3) if func3 > 0 else 0
	elif level == 4:
		return int(func4) if func4 > 0 else 0
	elif level == 5:
		return int(func5) if func5 > 0 else 0
	elif level >= 6:
		chance = int((0.1*x)-(level-6))
		return chance if chance > 0 else 0