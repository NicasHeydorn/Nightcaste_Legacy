""" Module for Map Creation.

Using Binary Space Partitioning for creating randomized Room Layouts.
"""


import libtcodpy as libtcod
import gvar
import roomfeatures

class Tile:
	""" A Tile of the map, to be included in gvar.game.map """
	def __init__(self, blocked = True, char='#', ai_blocked=False, block_sight = None, tile_type='wall', use_function=None, step_function=None, color=libtcod.white, weight=0, args=None):
		self.blocked = blocked 				#: Is the tile passable
		self.ai_blocked = ai_blocked		#: Will the AI pass this tile or go around it
		self.char = char 					#: The Character to be rendered for this tile
		self.color = color 					#: The color in which the character will be rendered
		self.explored = False 				#: Has the player explored it already; False by default
		self.use_function = use_function 	#: A function to be executed when the player uses the tile (e.g. open_door)
		self.step_function = step_function 	#: A function to be executed when the player steps on the tile (e.g. fall_down)
		self.tile_type = tile_type 			#: A string indicating the type (wall, floor, door, hole, etc.)
		self.weight = weight 				#: Weight for Pathfinding. The higher the weight, the more a step through this tile will "cost" leading to mobs going around this tile
		self.args = args 					#: Arguments for passing into the use_function

		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight 		#: By default, if a tile is blocked, it also blocks sight

	def use(self):
		""" Call the use_function, if it is defined. """
		if self.use_function is not None:
			if self.args is not None:
				self.use_function(self.args)
			else:
				self.use_function()



class Rect:
	""" A Rectangle used for creating rooms on the map """
	def __init__(self, map, x, y, w, h):
		self.map = map
		self.x1 = x 			#: Left X-Axis Boundary
		self.y1 = y 			#: Top Y-Axis Boundary
		self.w = w 				#: Width
		self.h = h 				#: Height
		self.x2 = x + w 		#: Right X-Axis Boundary
		self.y2 = y + h 		#: Bottom Y-Axis Boundary



	def get_corners(self, radius=0):
		""" |  Returns an array of the corners of the room.
			|  If radius is set, returns round areas around the corners
			|  only with unblocked tiles
		"""

		corners = [(self.x1, self.y1), (self.x2, self.y1), (self.x1, self.y2), (self.x2, self.y2)]
		reach = []
		if radius > 0:
			for corner in corners:
				a = Circle(corner[0], corner[1], radius, True)
				for c in a.circle:
					if not self.map.is_blocked(c[0], c[1]):
						reach.append((c[0], c[1]))
		return corners + reach



	def get_area(self):
		""" Returns an array containing all Tiles inside the room """
		area = []
		for x in range(self.x1+1, self.x2):
			for y in range(self.y1+1, self.y2):
				area.append((x, y))
		return area


	def random_spot(self):
		""" gets a random tile in a Rect instance """
		return (libtcod.random_get_int(0, self.x1+1, self.x2-1), libtcod.random_get_int(0, self.y1+1, self.y2-1))



	def center(self):
		""" Returns the coordinates of the center of this room, as a tuple """
	   	center_x = (self.x1 + self.x2)/2
	   	center_y = (self.y1 + self.y2)/2
	   	return (center_x, center_y)



	def intersect(self, other):
		""" Returns a boolean value, if this room intersects with another one """
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)



	def get_exits(self):
		""" |  Returns an array of tuples
			|  containing the tiles leading into/out of the room
		"""
		from utils import rotate90deg, is_double_door
		exits = []
		for px in range(self.x1,self.x2+1):
			if not self.map.map[px][self.y1].blocked and self.map.map[px][self.y1].tile_type == 'floor' or self.map.map[px][self.y1].tile_type == 'door':
				exits.append((px, self.y1))
			if not self.map.map[px][self.y2].blocked and self.map.map[px][self.y2].tile_type == 'floor' or self.map.map[px][self.y2].tile_type == 'door':
				exits.append((px, self.y2))
		for py in range(self.y1,self.y2+1):
			if not self.map.map[self.x1][py].blocked and self.map.map[self.x1][py].tile_type == 'floor' or self.map.map[self.x1][py].tile_type == 'door':
				exits.append((self.x1, py))
			if not self.map.map[self.x2][py].blocked and self.map.map[self.x2][py].tile_type == 'floor' or self.map.map[self.x2][py].tile_type == 'door':
				exits.append((self.x2, py))

		#eliminate false positives
		exits_to_remove = []
		for exit in exits:
			#check if there is another exit adjacent
			for adj in self.map.adjacent(exit[0], exit[1], diagonal=False):
				if (adj[0], adj[1]) in exits:
					rotated = rotate90deg(adj, exit)
					left_neighbor_unblocked = not self.map.map[rotated[0][0]][rotated[0][1]].blocked
					right_neightbor_unblocked = not self.map.map[rotated[1][0]][rotated[1][1]].blocked
					#if the exit "lies open" and it's not a double door
					if (((left_neighbor_unblocked and not right_neightbor_unblocked) or (not left_neighbor_unblocked and right_neightbor_unblocked)) and not is_double_door(self.map, exit, adj)):
						#it's a false positive
						exits_to_remove.append(exit)
		for e in exits_to_remove:
			if e in exits:
				exits.remove(e)
		return exits



class Circle:
	""" |  A Circle on the map, generated by supplying center coordinates and the radius.
		|  The circle can be filled, with the filled-Flag.
		|  Used e.g. for splash radii
	"""
	def __init__(self, x0, y0, r, filled=True):
		self.x0 = x0	#: Center X-Coordinate
		self.y0 = y0	#: Center Y-Coordinate
		self.r = r 		#: Radius
		#begin midpoint-algorithm
		x = r
		y = 0
		radiusError = 1-x
		self.circle = [] 	#: Array containing the coordinates of all tiles in the circle
		while(x >= y):
			if filled == True:
				for d in range(-x,x+1):
					self.circle.append([d+x0,y+y0])
					self.circle.append([d+x0,-y+y0])
				for d in range (-y, y+1):
					self.circle.append([d+x0,x+y0])
					self.circle.append([d+x0,-x+y0])
			else:
				self.circle += [[x+x0,y+y0]] + [[y+x0, x+y0]] + [[-x+x0,y+y0]] + [[-y+x0,x+y0]] + [[-x+x0,-y+y0]] + [[-y+x0,-x+y0]] + [[x+x0,-y+y0]] + [[y+x0,-x+y0]]
			y += 1
			if radiusError<0:
				radiusError += 2 * y + 1
			else:
				x -= 1
				radiusError += 2 * (y-x) + 1

class World:
	""" |  The World Objects contains all Dungeons (and other Map Collections, like the Worldspace)
		|  It has utilities for generating random Dungeons and Scenarios, as well.
	"""

	def __init__(self, worldspace, dungeons=None):
		self.worldspace = worldspace
		if dungeons is None:
			self.dungeons = list()

	def random_dungeon(self):
		import random, string
		id  = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
		depth = libtcod.random_get_int(0, 1, 25)
		print "Dungeon ", id, " has a depth of ", depth
		dungeon = Dungeon(id=id, depth=depth)
		self.dungeons.append(dungeon)



class Dungeon:
	""" |  A Collection of maps representing a Dungeon with multiple levels.

		|  **id** is a randomly generated string of length 8, if not specified.
		|  **maps** is an array of the maps
		|  **depth** is the maximum depth of the dungeon, to determine if stairs need to be spawned. Defaults to 1.
	"""

	def __init__(self, id, maps=None, depth=1):
		self.id = id
		if maps is None:
			self.maps = list()
		self.depth = depth

	def addMap(self, map):
		map.owner = self
		self.maps.append(map)

	def addRandomMap(self):
		map = Map()
		self.addMap(map)
		map.create_dungeon()


class Map:
	""" |  A map object, part of a Dungeon.

		|  **map** is the two-dimensional array of Tiles, the map itself
		|  **rooms** is an array of Rect instances, representing the rooms
		|  **tree** is the BSP tree used to generate the map
		|  **objects** contains all objects (Items, Mobs) in the map
		|  A map also has a **owner** attribute, which is the Dungeon()-Instance containing the map
		|  The **owner** has to be set from outside when initializing the map
		|  **upstairs** and **downstairs** are wuick references to the up- and downstairs objects in the objects array
	"""

	def __init__(self, map=None, rooms=None, tree=None, objects=None, owner=None):
		self.map = map
		if rooms is None:
			self.rooms = list()
		self.tree = tree
		if objects is None:
			self.objects = list()
		self.owner = owner
		self.upstairs = None
		self.downstairs = None

	@property
	def level(self):
		""" Returns the level of this map in the owning dungeon """
		return self.owner.maps.index(self)


	def create_worldspace(self):
		""" | Creates a randomly generated outdoor-scenario
		"""
		from components import Object
		from spawn import spawn_entrance

		self.map = [[ Tile(char=chr(249), tile_type='floor', blocked=False, block_sight=False)
			for y in range(gvar.MAP_HEIGHT) ]
				for x in range(gvar.MAP_WIDTH) ]


		self.rooms = [Rect(self, 0, 0, gvar.MAP_WIDTH, gvar.MAP_HEIGHT)]

		spawn_entrance(self)


	def create_dungeon(self):
		"""	|  Creates a random map

			|  First, fills the map with walls.
			|  Creates a BSP (Binary Space Partitioning) Tree and traverses it, creating a randomly-sized room for every node.
			|  50 % chance to spawn a random room feature, such as holes in the floor or columns.
			|  Spawns the player on a random unblocked spot.
			|  Then, calls *spawn_stuff()* to spawn mobs, items and the stairs
		"""
		from spawn import spawn_stuff
		from components import Object
		from roomfeatures import random_roomfeature

		#fill map with walls
		self.map = [[ Tile(char=chr(219), tile_type='wall', color=libtcod.grey)
			for y in range(gvar.MAP_HEIGHT) ]
				for x in range(gvar.MAP_WIDTH) ]

		#Create BSP Tree and Traverse it
		self.tree = libtcod.bsp_new_with_size(0, 0, gvar.MAP_WIDTH-2, gvar.MAP_HEIGHT-2)
		libtcod.bsp_split_recursive(self.tree, 0, 4, 8, 8, 1.3, 1.3)
		libtcod.bsp_traverse_post_order(self.tree, self.process_node, userData=0)

		#Random Roomfeature
		for room in self.rooms:
			if libtcod.random_get_int(0, 0, 2) == 0:
				random_roomfeature(self, room)

		spawn_stuff(self)


	def unblocked_spot_in(self, radius, x, y):
		""" |  returns an unblocked tile within a given radius
			|  increase the radius if no unblocked spot is found
		"""

		for a in range(radius):
			for b in range(radius):
				if not self.is_blocked(x+a, y+b):
					return (x+a, y+b)
				if not self.is_blocked(x-a, y-b):
					return (x-a, y-b)
		self.unblocked_spot_in(radius+1, x, y)



	def in_boundaries(self, x, y):
		""" Returns a boolean, indicating if the given spot is within the map boundaries """
		if x <= 0 or y <= 0 or x >= gvar.MAP_WIDTH or y >= gvar.MAP_HEIGHT:
			return False
		return True



	def is_blocked(self, x, y, ai=False):
		""" |  check if a map tile is blocked
			|  or if it's blocked for the AI (Holes, Traps, etc.)
		"""
		if not self.in_boundaries(x, y):
			return True
		if self.map[x][y].blocked:
			return True
		if ai:
			if self.map[x][y].ai_blocked:
				return True

		for obj in self.objects:
			if obj.blocks and obj.x == x and obj.y == y:
				return True
		return False


	def adjacent(self, x, y, tile_type=None, diagonal=True):
		""" |  return an array of all adjacent tiles
			|  or an array of all adjacent tiles with given tile_type
			|  If the diagonal Flag is set to False, returns only non-diagonal Tiles
		"""
		if not diagonal:
			adjacent_tiles = [[x, y-1], [x+1, y], [x, y+1], [x-1, y]]
		else:
			adjacent_tiles = [[x, y-1], [x+1, y-1], [x+1, y], [x+1, y+1], [x, y+1], [x-1, y+1], [x-1, y], [x-1, y-1]]
		valid_tiles = []
		for tile in adjacent_tiles:
			if self.in_boundaries(tile[0], tile[1]):
				valid_tiles.append(tile)
		if tile_type is not None:
			for tile in valid_tiles:
				if self.map[tile[0]][tile[1]].tile_type != tile_type:
					valid_tiles.remove(tile)
		return valid_tiles



	def adjacent_ai_unblocked(self, spot, exception=None, ignore_ai_blocks=False, ignore_types=[]):
		""" |  returns an array of all adjacent tiles as tuples
			|  if an exception is set, blocking check wont be executed for the given spot
		"""

		results = []
		(x, y) = spot
		for point in [(x, y-1), (x+1, y-1), (x+1, y), (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y), (x-1, y-1)]:
			if ignore_ai_blocks:
				unblocked = not self.is_blocked(point[0], point[1]) or self.map[point[0]][point[1]].tile_type in ignore_types
			else:
				unblocked = not self.is_blocked(point[0], point[1], ai=True) or self.map[point[0]][point[1]].tile_type in ignore_types
			if unblocked or exception is not None and exception == point:
				results.append(point)
		return results


	def random_room(self):
		""" Returns a random room in this map """
		return self.rooms[libtcod.random_get_int(0, 0, len(self.rooms)-1)]


	def set_door(self, x, y):
		""" Creates a door on the given position. """
		from mechanics import open_door
		self.map[x][y] = Tile(char='+', use_function=open_door, tile_type='door', blocked=True, block_sight=True, color=libtcod.light_sepia)



	def set_floor(self, x, y):
		""" Creates floor on the given position. """
		self.map[x][y] = Tile(char=chr(249), tile_type='floor', blocked=False, block_sight=False, ai_blocked=False, step_function=None)



	def set_wall(self, x, y):
		""" Creates a wall on the given position. """
		self.map[x][y] = Tile(char=chr(219), tile_type='wall', blocked=True, block_sight=True, ai_blocked=True, color=libtcod.grey)



	def set_hole(self, x, y):
		""" Creates a hole on the given position. """
		from mechanics import fall_into
		self.map[x][y] = Tile(char=' ', tile_type='hole', blocked=False, block_sight=False, ai_blocked=True, step_function=fall_into)



	def create_room(self, room):
		""" Iterates over the tiles in the given room and creates floor in it, using set_floor method """
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.set_floor(x, y)


	def corridor(self, node):
		""" |  Builds a corridor between the left and right children of the given node.
			|  The corridor is Z-shaped, only horizontally and vertically.
			|  The order of h / v corridors is randomly set (50/50).
		"""
		left = self.random_spot_in_node(libtcod.bsp_left(node))
		right = self.random_spot_in_node(libtcod.bsp_right(node))
		if libtcod.random_get_int(0, 0, 1) == 1:
			self.create_h_corridor(left[0], right[0], left[1])
			self.create_v_corridor(left[1], right[1], right[0])
		else:
			self.create_v_corridor(left[1], right[1], left[0])
			self.create_h_corridor(left[0], right[0], right[1])




	def create_h_corridor(self, x1, x2, y):
		""" |  Create a horizontal tunnel from **x1** to **x2** on **y**.
			|  Checks for surrounding tiles when entering another room and creates a door with a certain probability.
		"""
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.set_floor(x, y)
			#eliminate doors on crossings and allow double-corridor doors
			if self.map[x][y+1].tile_type == 'door' and self.map[x][y-1].tile_type == 'wall':
				self.set_door(x, y)
			if self.map[x][y-1].tile_type == 'door' and self.map[x][y+1].tile_type == 'wall':
				self.set_door(x, y)
			if self.map[x+1][y].tile_type == 'floor' and libtcod.random_get_int(0, 0, 3) == 3:
				#prevent orphaned doors
				if self.map[x][y+1].tile_type == 'wall' and self.map[x][y-1].tile_type == 'wall':
					self.set_door(x, y)




	def create_v_corridor(self, y1, y2, x):
		""" |  Create a vertical tunnel from **y1** to **y2** on **x**.
			|  Checks for surrounding tiles when entering another room and creates a door with a certain probability.
		"""
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.set_floor(x, y)
			#eliminate doors on crossings and also double-corridor doors
			if self.map[x+1][y] == 'door' and self.map [x-1][y].tile_type == 'wall':
				self.set_door(x, y)
			if self.map[x-1][y] == 'door' and self.map [x+1][y].tile_type == 'wall':
				self.set_door(x, y)
			if self.map[x][y+1].tile_type == 'floor' and libtcod.random_get_int(0, 0, 3) == 3:
				#prevent orphaned doors
				if self.map[x+1][y].tile_type == 'wall' and self.map[x-1][y].tile_type == 'wall':
					self.set_door(x, y)




	def process_node(self, node, userData):
		""" Processes a BSP node.

			|  Creates a room, if the node is a leaf and then smoothes its corners.
			|  If the node is not a leaf, connect the child nodes with a corridor
		"""
		from components import Object
		from render import render_all
		from nightcaste import initialize_fov

		if libtcod.bsp_is_leaf(node):
			#Create Rooms for leafs (level n)
			min_w = node.w - (node.w/2)
			min_h = node.h - (node.h/2)
			width = libtcod.random_get_int(0, min_w, node.w)
			height = libtcod.random_get_int(0, min_h, node.h)
			room = Rect(self, libtcod.random_get_int(0, node.x, (node.x + node.w)-width), libtcod.random_get_int(0, node.y, (node.y + node.h)-height), width, height)
			self.create_room(room)
			self.smooth_room_corners(room)
			self.rooms.append(room)
		elif not libtcod.bsp_is_leaf(node):
			#Connect rooms with corridors for levels n-1
			self.corridor(node)
		return True




	def random_spot_in_node(self, node):
		""" Returns a randomly selected floor inside the given node """
		spot_x = libtcod.random_get_int(0, node.x, node.x + node.w - 1)
		spot_y = libtcod.random_get_int(0, node.y, node.y + node.h - 1)
		if self.map[spot_x][spot_y].tile_type == "floor":
			return (spot_x, spot_y)
		else:
			return self.random_spot_in_node(node)




	def randomize_tiles(self, area, positive_function, negative_function, positive_percentage):
		""" |  Randomizes the tiles inside the given area *(array of positions)*.
			|  If a random value is greater than the given positive_percentage,
			|  calls the positive function with x and y position of the positions
			|  as arguments. If its less, calls negative_function.
		"""
		for spot in area:
			x = spot[0]
			y = spot[1]
			if libtcod.random_get_int(0, 1, 100) < positive_percentage:
				positive_function(x, y)
			else:
				negative_function(x, y)




	def smooth_room_corners(self, room):
		""" |  Randomizes the tiles of the corners of the room and sets them either to wall or to floor.
			|  The Corner radius depends on the size of the room.
			|  Then, calls ca_smooth to smooth out the tiles and create a more natural look.
		"""
		if room.w <= 8:
			coef = 8
		else:
			coef = 4
		self.randomize_tiles(room.get_corners(room.w/coef), self.set_floor, self.set_wall, 50)
		self.ca_smooth(room.get_area(), 'floor', self.set_floor, self.set_wall, (3,6), iterations=4)
		for spot in room.get_corners():
			self.set_wall(spot[0], spot[1])




	def ca_smooth(self, area, positive_type, positive_function, negative_function, ratio, iterations=1):
		""" |  smoothes out the tiles of the room
			|  by applying a cellular automaton
			|  ratio is a tuple for the cellular automaton rule
			|  e.g. (4, 5)
		"""

		for i in range(iterations):
			for spot in area:
				x = spot[0]
				y = spot[1]
				if self.in_boundaries(x, y):
					count = self.adjacent(x, y, positive_type)
					if self.map[x][y].tile_type == positive_type:
						if len(count) >= ratio[0]:
							positive_function(x, y)
						else:
							negative_function(x, y)
					else:
						if len(count) >= ratio[1]:
							positive_function(x, y)



	def restore_accessibility(self, room):
		""" |  Checks, if every exit of the given room is reachable from the other exits.
			|  If one exit is not reachable from the other, builds a bridge between the two.
		"""
		from utils import a_star_search

		for entrance in room.get_exits():
			for exit in room.get_exits():
				if entrance == exit:
					continue
				else:
					if not self.is_reachable(entrance, exit):
						bridge_path = a_star_search(self, entrance, exit, ignore_ai_blocks=True)
						for bridge_tile in bridge_path:
							self.set_floor(bridge_tile[0], bridge_tile[1])



	def is_reachable(self, start, end, crossborder=False):
		""" |  perform an a-star search from start to end
			|  and return Boolean, if end was reached

			|  If the crossborder flag is set, it performs 15 searches from random spots on the map,
			|  which doesn't guarantee reachability, but the probability of non-reachability is sufficiently low
		"""

		from utils import a_star_search
		from render import render_all

		if not crossborder:
			path = a_star_search(self, start, end, ignore_types=['door'])
			if end not in path:
				return False
			return True
		else:
			for i in range(15):
				end = self.random_room().random_spot()
				path = a_star_search(self, start, end, ignore_types=['door'])
				if end not in path:
					return False
			return True