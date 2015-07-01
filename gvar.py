""" Global Module for global variables:
"""

import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 53
MAP_WIDTH = 80
MAP_HEIGHT = 44

BAR_WIDTH = 20
PANEL_HEIGHT = 10
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1



class Game:
	""" A Game Instance, consisting of all Information, that will go into the savegame

		* player
		* ticks
		* map
		* world (consisting of all Maps)
		* game_msgs
		* last_die_rolls
		* dungeon_level
		* game_state
		* objects
		* rooms
	"""
	def __init__(self):
		global playermaxhl
		from mechanics import player_death
		from components import Object,Fighter
		from utils import PriorityQueue

		self.player = Object(currentDungeon=None, currentLevel=0, x=0, y=0, char=chr(2), color=libtcod.white, name='player', blocks=True, inventory=[])
		compFighter = Fighter(hl=[1,2,2,1], essence=2, strength=1, dexterity=1, stamina=1, death_function=player_death)
		playermaxhl = compFighter.hl
		self.player.fighter = compFighter
		self.player.fighter.owner = self.player

		self.ticks = PriorityQueue()

		self.game_msgs = []
		self.last_die_rolls = []
		self.game_state = 'playing'

	def init_world(self):
		from mapcreation import World, Map, Dungeon
		m = Map()
		self.world = World(Dungeon(id='worldspace'))
		self.world.worldspace.addMap(m)
		m.create_worldspace()



class Admin:
	""" Admin Object for Debugging Purposes

		If the Admin Menu is enabled, you can access it by pressing F11 ingame.

		* *light_all*  -  Toggle FOV
	"""
	#Admin Settings
	def __init__(self):
		self.light_all = False

admin = Admin()