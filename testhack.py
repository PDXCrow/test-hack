import tdl
import colors
from random import randint

# Actual size of game window
screen_width = 80
screen_height = 50

# Size of the map
map_width = 80
map_height = 45

# Parameters for dungeon generator
room_max_size = 10
room_min_size = 6
max_rooms = 26
max_room_monsters = 3


FOV_ALGO = 'BASIC'
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

color_dark_wall = (0, 0, 100)
color_light_wall = (130, 110, 50)
color_dark_ground = (50, 50, 150)
color_light_ground = (200, 180, 50)



class Tile:
	# A tile of the map and its properties
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked

		# All tiles start unexplored
		self.explored = False

		# By default, if a tile is blocked, it also blocks sight
		if block_sight is None: 
			block_sight = blocked
		self.block_sight = block_sight




class Rect:
	# A rectangle on the map, used to characterize a room.
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h

	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2
		return (center_x, center_y)

	def intersect (self, other):
		# Returns true if this rectanble intersects with another one.
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)


class GameObject:
	"""
	This is a generic object: the player a monster, an item, the stairs,
	anything represented by a character on screen.
	"""
	def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.blocks = blocks
		self.fighter = fighter
		if self.fighter: # Let the fighter component know who owns it
			self.fighter.owner = self

		self.ai = ai
		if self.ai: # Let the AI component know who owns it
			self.ai.owner = self

	def move(self, dx, dy):
		# Only move if space moving to is not designated as 'blocked'.
		if not is_blocked(self.x + dx, self.y + dy):

			# Move by the given amount
			self.x += dx
			self.y += dy

	def draw(self):
		global visible_tiles

		# Only show if it's visible to the player
		if (self.x, self.y) in visible_tiles:
			# Draw the character that represents this object at its position.
			con.draw_char(self.x, self.y, self.char, self.color, bg=None)

	def clear(self):
		# Erase the character that represents this object
		con.draw_char(self.x, self.y, ' ', self.color, bg=None)


class Fighter:
	# Combat-related properties and methods (monster, player, NPC)
	def __init__(self, hp, defense, power):
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power


class BasicMonster:
	# AI for a basic monster
	def take_turn(self):
		print('The ' + self.owver.name + ' growls!')


def is_blocked(x, y):
	# First test the map tile
	if my_map[x][y].blocked:
		return True

	# Now check for any blocking objects
	for obj in objects:
		if obj.blocks and obj.x == x and obj.y == y:
			return True

	return False


def create_room(room):
    global my_map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False


def place_objects(room):
	# Choose random number of monsters.
	num_monsters = randint(0, max_room_monsters)

	for i in range(num_monsters):
		# Choose random spot for this monster.
		x = randint(room.x1, room.x2)
		y = randint(room.y1, room.y2)

		# Only place if tile is not blocked.
		if not is_blocked(x, y):
			if randint(0, 100) < 80: # 80% chance of getting an orc.

				""" METHOD TO CREATE VARIETY OF MONSTERS:

				#chances: 20% monster A, 40% monster B, 10% monster C, 30% monster D:
				choice = randint(0, 100)
				if choice < 20:
				    #create monster A
				elif choice < 20+40:
				    #create monster B
				elif choice < 20+40+10:
				    #create monster C
				else:
				    #create monster D
				"""

				# Create an orc
				fighter_component = Fighter(hp=10, defense= 0, power=3)
				ai_component = BasicMonster()
				monster = GameObject(x, y, 'o', 'orc', colors.desaturated_green, 
					blocks=True, fighter=fighter_component, ai=ai_component)
			else:
				# Create a dragon.
				fighter_component = Fighter(hp=30, defense= 1, power=4)
				ai_component = BasicMonster()
				monster = GameObject(x, y, 'D', 'dragon', colors.darker_red, 
					blocks=True, fighter=fighter_component, ai=ai_component)

			objects.append(monster)



def create_h_tunnel(x1, x2, y):
	global my_map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		my_map[x][y].blocked = False
		my_map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
	global my_map
	for y in range(min(y1, y2), max(y1, y2) + 1):
		my_map[x][y].blocked = False
		my_map[x][y].block_sight = False


def is_visible_tile(x, y):
	global my_map

	if x >= map_width or x < 0:
		return False
	elif y >= map_height or y < 0:
		return False
	elif my_map[x][y].blocked == True:
		return False
	elif my_map[x][y].block_sight == True:
		return False
	else:
		return True


def make_map():
	global my_map

	# Fill map with "blocked" tiles.
	my_map = [[ Tile(True) # True makes tiles blocked
		for y in range(map_height) ] 
			for x in range(map_width) ]

	rooms = []
	num_rooms = 0

	for r in range(max_rooms):
		# Random width and height
		w = randint(room_min_size, room_max_size)
		h = randint(room_min_size, room_max_size)
		# Random position without going out of the boundaries of the map
		x = randint(0, map_width-w-1)
		y = randint(0, map_height-h-1)

		# 'Rect' class makes rectangles easier to work with.
		new_room = Rect(x, y, w, h)

		# Run through the other rooms and see if they intersect with this one.
		failed = False
		for other_room in rooms:
			if new_room.intersect(other_room):
				failed = True
				break

		if not failed:
			# This means there are no intersections, so this room is valid.

			# 'Paint' it to the map's tiles
			create_room(new_room)

			# Get center coordinates of new room for use later
			(new_x, new_y) = new_room.center()

			if num_rooms == 0:
				# This is our first room, where the player starts at
				player.x = new_x
				player.y = new_y

			else:
				# All rooms after the first.
				# Connect it to the previous room with a tunnel.

				# Center coordinates of previous room
				(prev_x, prev_y) = rooms[num_rooms-1].center()

				# Draw random either 0 or 1
				if randint(0, 1):
					# First move horizontally, then vertically
					create_h_tunnel(prev_x, new_x, prev_y)
					create_v_tunnel(prev_y, new_y, new_x)
				else:
					# First move vertically, then horizontally
					create_v_tunnel(prev_y, new_y, prev_x)
					create_h_tunnel(prev_x, new_x, new_y)

			# Add some contents to the room, such as monsters
			place_objects(new_room)


			# Finally, append the new room to the list
			rooms.append(new_room)
			num_rooms += 1





def render_all():
	global fov_recompute
	global visible_tiles

	if fov_recompute:
		fov_recompute = False
		visible_tiles = tdl.map.quickFOV(player.x, player.y,
										 is_visible_tile, 
										 fov=FOV_ALGO,
										 radius=TORCH_RADIUS,
										 lightWalls=FOV_LIGHT_WALLS)

	# Go through all tiles and set their background color.
	for y in range(map_height):
		for x in range(map_width):
			visible = (x, y) in visible_tiles
			wall = my_map[x][y].block_sight
			if not visible:
				# If it's not visible right now, the player cn only see it if it's explored
				if my_map[x][y].explored:
					if wall:
						con.draw_char(x, y, None, fg=None, bg=color_dark_wall)
					else:
						con.draw_char(x, y, None, fg=None, bg=color_dark_ground)
			else:
				# It's visible
				if wall:
					con.draw_char(x, y, None, fg=None, bg=color_light_wall)
				else:
					con.draw_char(x, y, None, fg=None, bg=color_light_ground)
				# Since it's visible, explore it
				my_map[x][y].explored = True

	# Draw all objects in the list.
	for obj in objects:
		obj.draw()

	"""
	Blit contents of con onto root to display them. 
	Parameters are: top-left corner is 0,0, same size as screen, destination coordinants
	are 0,0 as well.
	"""
	root.blit(con, 0, 0, screen_width, screen_height, 0, 0)


def handle_keys():
	global playerx, playery
	global fov_recompute

	user_input = tdl.event.key_wait()

	if user_input.key == 'ENTER' and user_input.alt:
		#Alt-Enter: toggle fullscreen
		tdl.set_fullscreen(not tdl.get_fullscreen())

	elif user_input.key == 'ESCAPE':
		return 'exit'   # exit game

	if game_state == 'playing':
		# Movement keys
		if user_input.key == 'UP':
			player_move_or_attack(0, -1)
			fov_recompute = True

		elif user_input.key == 'DOWN':
			player_move_or_attack(0, 1)
			fov_recompute = True

		elif user_input.key == 'LEFT':
			player_move_or_attack(-1, 0)
			fov_recompute = True

		elif user_input.key == 'RIGHT':
			player_move_or_attack(1, 0)
			fov_recompute = True
		else:
			return 'didnt_take_turn'

def player_move_or_attack(dx, dy):
	global fov_recompute

	# The coordinates the player is moving to/attacking
	x = player.x + dx
	y = player.y + dy

	# Try to find an attackable object there
	target = None
	for obj in objects:
		if obj.x == x and obj.y == y:
			target = obj
			break

	# Attack if target found, move otherwise
	if target is not None:
		print('The ' + target.name.title() + ' laughs at your puny efforts to attack him')
	else:
		player.move(dx, dy)
		fov_recompute = True


# Initialization and Main Loop

tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

# This is the original root console that is shown directly on screen
root = tdl.init(screen_width, screen_height, title="HansHack", fullscreen=False)

# This is the new console we are drawing off-screen and then applying to root when ready
con = tdl.Console(screen_width, screen_height)

# Create object representing the player
fighter_component = Fighter(hp=30, defense=2, power=5)
player = GameObject(0, 0, '@', 'player', colors.white, blocks=True, fighter=fighter_component)

# The list of objects, starting with the player
objects = [player]

# Generate map (at this point it is not drawn to the screen)
make_map()

fov_recompute = True

game_state = 'playing'
player_action = None



while not tdl.event.is_window_closed():

	#draw all objects in the objects list using the render_all function
	render_all()

	tdl.flush()

	# Erase all objects at their old locations, before they move
	for obj in objects:
		obj.clear()

	# Handle keys and exit game if needed
	player_action = handle_keys()
	if player_action == 'exit':
		break

	# Let monsters take their turn
	if game_state == 'playing' and player_action != 'didnt_take_turn':
		for obj in objects:
			if obj != player:
				# print('The ' + obj.name + ' growls!')
				break


