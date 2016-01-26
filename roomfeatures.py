""" Spezialized Map features that are distributed randomly among the map's rooms. """

import libtcodpy as libtcod
import math
import gvar

def random_roomfeature(map, room):
	""" Chooses a random feature from a given list to be spawned in the given room. """

	features = [
				"column_rows",
				"floor_holes"
			]
	method = libtcod.random_get_int(0, 0, len(features)-1)
	globals()[features[method]](map, room)

def column_rows(map, room):
	""" Spawn 2 rows of Columns in the room """
	from mapcreation import Tile
	from utils import interval_on_range
	if (room.w * room.h) <= 60:
		return
	else:
		scale_sm = libtcod.random_get_int(0, 5, 6)
		scale_lg = libtcod.random_get_int(0, 5, 8)
		if room.h >= room.w:
			x = interval_on_range(room.w, scale_sm, 2)
			y = interval_on_range(room.h, scale_lg, 2)
		if room.w > room.h:
			x = interval_on_range(room.w, scale_sm, 2)
			y = interval_on_range(room.h, scale_lg, 2)
		for spot_x in x:
			for spot_y in y:
				map.map[room.x1 + spot_x][room.y1 + spot_y] = Tile(char=chr(9), block_sight=True)

def floor_holes(map, room):
	""" Holes in the floor, maintaining accessibility """
	from mapcreation import Tile, Circle
	from mechanics import fall_into

	if room.w >= 6 and room.h >= 6:
		map.randomize_tiles(room.get_area(), map.set_floor, map.set_hole, 50)
		map.ca_smooth(room.get_area(), 'hole', map.set_hole, map.set_floor, (5, 6))
		map.restore_accessibility(room)