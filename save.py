""" Methods for savegame management """

import shelve
import gvar

def save_game():
	""" Just saves the gvar.game instance in a shelve named nightcaste.sav """
	savegame = shelve.open('nightcaste.sav', 'n')
	savegame["game"] = gvar.game
	savegame.close()

def save_game_custom():
	""" |  Custom Save Game method, serializing all instances.
		|  Not needed at the moment, but you never know.
	"""

	savegame = shelve.open('nightcaste.sav', 'n')
	savegame["dungeons"] = list()
	savegame["dungeon-maps"] = dict()
	savegame["maps"] = list()
	savegame["map-rooms"] = dict()
	savegame["map-objects"] = dict()
	savegame["rooms"] = list()
	savegame["objects"] = list()

	for dungeon in gvar.game.world.dungeons + [gvar.game.world.worldspace]:
		savegame["dungeon-maps"][dungeon.id] = [map.id for map in dungeon.maps]
		for map in dungeon.maps:
			map.owner = dungeon.id
			for room in map.rooms:
				room.map = map.id
				savegame["rooms"] += [room]
			savegame["map-rooms"][map.id] = [room.id for room in map.rooms]
			map.rooms = None

			for object in map.objects:
				object.currentDungeon = dungeon.id
				if object.use_function == "spawn_player":
					object.args[0] = object.args[0].id
				savegame["objects"] += [object]

			savegame["map-objects"][map.id] = [object.id for object in map.objects]
			map.objects = None

			serialize_object(map)
			savegame["maps"] += [map]
		dungeon.maps = None
		savegame["dungeons"] += [dungeon]

	savegame['world-dungeons'] = [dungeon.id for dungeon in gvar.game.world.dungeons]
	savegame['world-worldspace'] = [dungeon.id for dungeon in gvar.game.world.worldspace]
	gvar.game.world.worldspace = None
	gvar.game.world.dungeon = None
	savegame['world'] = gvar.game.world
	gvar.game.world = None
	savegame['game'] = gvar.game
	savegame.close()



def load_game():
	""" Just loads the gvar.game instance from a shelve named nightcaste.sav """
	savegame = shelve.open('nightcaste.sav', 'r')
	gvar.game = savegame['game']
	gvar.fov_recompute = True
	savegame.close()