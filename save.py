""" Methods for serializing game data into lists """

import shelve
import gvar
import pprint

def save_game():
	savegame = shelve.open('nightcaste.sav', 'n')
	player = serialize_object(gvar.game.player)
	pprint.pprint(player)
	savegame['player'] = player
	savegame.close()


def load_game():
	savegame = shelve.open('nightcaste.sav', 'r')

	savegame.close()


def serialize_object(object):
	""" Serializer for Object() Class """
	target = dict()
	#target['currentDungeon'] = object.currentDungeon
	target['currentLevel'] = object.currentLevel
	target['x'] = object.x
	target['y'] = object.y
	target['char'] = object.char
	target['color'] = object.color
	target['name'] = object.name
	target['blocks'] = object.blocks
	target['always_visible'] = object.always_visible
	target['exp'] = object.exp
	target['inventory'] = object.inventory
	target['args'] = object.args
	target['use_function'] = object.use_function
	#target['fighter'] = object.fighter
	#target['ai'] = object.ai
	#target['item'] = object.item
	#target['equipment'] = object.equipment
	return target