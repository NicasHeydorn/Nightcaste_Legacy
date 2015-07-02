""" Utility Methods used in different contexts and therefore need to be centrally available """
import libtcodpy as libtcod
import gvar
import heapq
import math

def d10(count, label, botchable=True, player=False):
	""" |  rolls x d10s and returns [successes, [die, die, die ...]].
		|  Publishes the roll result to the dice feed, if it was the player's roll.
	"""
	from render import render_dice_rolls

	result = [0, []]
	for i in range(1,count+1):
		dice = libtcod.random_get_int(0, 0, 9)
		if dice >= 7:
			result[0] += 1
		elif dice == 0:
			result[0] += 2
		result[1].append(dice)

	#check for botch
	botch = False
	for d in result[1]:
		if d == 1 and botchable == True:
			botch = True
		elif (d >= 7 or d == 0) and botchable == True:
			botch = False
			break
	if botch == True:
		result[0] = 'botch'
	result.append(label)

	#Only show dice roll messages for rolls of the player
	if player:
		if len(gvar.game.last_die_rolls) > 3:
			del gvar.game.last_die_rolls[0]
		gvar.game.last_die_rolls.append(result)

	return result



def decrease_tick_level():
	""" |  Extracts all actors from the global Tick Counter
		|  and reappends them, decreasing the overall
		|  level, so that the lowest is 0
	"""

	if len(gvar.game.ticks.output()) > 0:
		lowest = gvar.game.ticks.getWithPriority()
		delta = lowest[0]
		buffer = []
		for index in range(len(gvar.game.ticks.output())):
			buffer.append(gvar.game.ticks.getWithPriority())
		for index in range(len(buffer)):
			gvar.game.ticks.put(buffer[index][1], buffer[index][0] - delta)
		gvar.game.ticks.put(lowest[1], lowest[0] - delta)



def is_player(entity):
	""" Returns a boolean, indicating if the given entitiy is the player """
	if entity == gvar.game.player:
		return True
	else:
		return False



def applyBonus(attribute, amount, fighter):
	""" |  Apply a new bonus to fighter,
		|  preserving the existing bonus
	"""
	if attribute in fighter.bonus:
		fighter.bonus[attribute].append(amount)
	else:
		fighter.bonus[attribute] = [amount]



def revertBonus(attribute, amount, fighter):
	""" |  Iterate through bonus array
		|  and remove the given amount, if found
	"""
	if amount in fighter.bonus[attribute]:
		del fighter.bonus[attribute][fighter.bonus[attribute].index(amount)]



def calcBonuses(attribute, fighter):
	""" |  Sum up all Boni that apply from equipment
		|  only for the given attribute
	"""

	equipment = fighter.owner.get_all_equipped()
	bonus = 0
	for item in equipment:
		if len(item.bonus) > 0:
			if attribute in item.bonus: bonus += item.bonus[attribute]
	if attribute in fighter.bonus:
		for b in fighter.bonus[attribute]:
			bonus += b
	return bonus



def rotate90deg(point, origin):
	""" |  rotates point around origin and
		|  returns an array of points rotated 90deg and -90deg
		|  only for orthogonal points
	"""

	diffx = math.fabs(point[0] - origin[0])
	diffy = math.fabs(point[1] - origin[1])
	return [(int(origin[0] - diffy), int(origin[1] - diffx)), (int(origin[0] + diffy), int(origin[1] + diffx))]



def is_double_door(map, point1, point2):
	""" forwarder to check if two points are a double door in both directions """
	return double_door_check(map, point1, point2) or double_door_check(map, point2, point1)



def double_door_check(map, point1, point2):
	""" check if the two points are a double door """
	dx = int(math.fabs(point2[0] - point1[0]))
	dy = int(math.fabs(point2[1] - point1[1]))
	if dy > dx:
		if  ((map.is_blocked(point1[0], point1[1]+2) and map.is_blocked(point1[0], point1[1]-1)) or
			 (map.is_blocked(point1[0], point1[1]+1) and map.is_blocked(point1[0], point1[1]-2))):
					return True
	elif dx > dy:
		if  ((map.is_blocked(point1[0]+2, point1[1]) and map.is_blocked(point1[0]-1, point1[1])) or
			(map.is_blocked(point1[0]+1, point1[1]) and map.is_blocked(point1[0]-2, point1[1]))):
					return True
	return False



def sort_inventory():
	""" |  Sort the inventory, putting all equipped items on top
		|  and grouping items together
	"""
	gvar.game.player.inventory = sorted(gvar.game.player.inventory, key=lambda item: item.name)
	for item in gvar.game.player.inventory:
		if item.equipment is not None:
			if item.equipment.is_equipped == True:
				gvar.game.player.inventory.remove(item)
				gvar.game.player.inventory.insert(0, item)



def interval_on_range(stretch, delta, pad):
	""" |  returns an array of spots along a stretch, evenly distributed
		|  with interval of delta and a left/right padding
	"""
	spots = []
	a = 1+pad
	delta = max(delta, 1)
	while a <= stretch - pad:
		spots.append(a)
		a += delta
	if len(spots) > 0 and (stretch-pad) != spots[-1]:
		for spot in range(0, len(spots)):
			spots[spot] += ((stretch-pad)-spots[-1])/2
	return spots



def get_distance(start, destination):
	""" calculates the euclidean distance between two points """
	dx = destination[0] - start[0]
	dy = destination[1] - start[1]
	return math.sqrt(dx ** 2 + dy ** 2)



def fov_distance_coef(spot):
	""" |  returns a value between 0.3 and 1
		|  depending on the distance between spot and the player's position
	"""
	distance = get_distance((spot[0], spot[1]), (gvar.game.player.x, gvar.game.player.y))
	player_fov_distance = int(gvar.game.player.fighter.skills["Awareness"] + gvar.game.player.fighter.perception)
	coef = player_fov_distance/max(distance, 1)/5
	if spot == (gvar.game.player.x, gvar.game.player.y):
		return 1
	return max(coef, 0.1)

def is_visible((x, y)):
	""" | returns a boolean value, if the given spot is inside the circular fov field of the player """
	return (libtcod.map_is_in_fov(gvar.fov_map, x, y) and [x, y] in gvar.fovmap_override.circle) or (gvar.game.player.x == x and gvar.game.player.y == y)


class PriorityQueue:
	""" |  Priority Queue using Heaps
		|  for A*-Search
	"""
	def __init__(self):
		self.elements = []
	def output(self):
		return self.elements
	def empty(self):
		return len(self.elements) == 0
	def put(self, item, priority):
		heapq.heappush(self.elements, (priority, item))
	def get(self):
		return heapq.heappop(self.elements)[1]
	def getWithPriority(self):
		return heapq.heappop(self.elements)
	def contains(self, item):
		for element in self.elements:
			if element[1] == item:
				return True
		return False



def heuristic(a, b):
	""" Manhattan Heuristic for A*-Search """
	(x1, y1) = a
	(x2, y2) = b
	return abs(x1 - x2) + abs(y1 - y2)



def a_star_search(map, start, goal, ignore_ai_blocks=False, ignore_types=[]):
	""" |  A* Search algorithm
		|  Thanks to Redblobgames, based off:
		|  http://www.redblobgames.com/pathfinding/a-star/implementation.html
	"""
	frontier = PriorityQueue()
	frontier.put(start, 0)
	came_from = {}
	cost_so_far = {}
	came_from[start] = None
	cost_so_far[start] = 0

	while not frontier.empty():
		current = frontier.get()

		if current == goal:
			break

		for next in map.adjacent_ai_unblocked(current, goal, ignore_ai_blocks=ignore_ai_blocks, ignore_types=ignore_types):
			new_cost = cost_so_far[current] + map.map[next[0]][next[1]].weight
			if next not in cost_so_far or new_cost < cost_so_far[next]:
				cost_so_far[next] = new_cost
				priority = new_cost + heuristic(goal, next)
				frontier.put(next, priority)
				came_from[next] = current

	#exception for completely blocked paths
	#mob just stays on its position
	if goal not in came_from:
		return [start, start]

	current = goal
	path = [current]
	while current != start:
		current = came_from[current]
		path.append(current)
	return path