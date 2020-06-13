import sys
import random
import base64
import click
import getkey

class Square:
	
	foreground_color = None
	background_color = None
	fill_character = None
	row_offset = None
	column_offset = None
	width = None
	height = None
	interactive = True
	
	def __init__(self, width, height, foreground_color, background_color, fill_character, row_offset=0, column_offset=0):
		self.width = width
		self.height = height
		self.foreground_color = foreground_color
		self.background_color = background_color
		self.fill_character = fill_character
		self.row_offset = row_offset
		self.column_offset = column_offset
	
	def check_position(self, new_row_index, new_column_index, max_row_index, max_column_index, squares):
		row_index_is_valid = new_row_index >= 0 and new_row_index < max_row_index
		column_index_is_valid = new_column_index >= 0 and new_column_index < max_column_index
		both_indices_are_valid = row_index_is_valid and column_index_is_valid
		other_square = squares[new_row_index][new_column_index] if both_indices_are_valid else None
		would_cause_overlap = other_square != None and not other_square.interactive
		return both_indices_are_valid and not would_cause_overlap
	
	def check_base_status(self):
		return self.row_offset == 0 and self.column_offset == 0
	
	def generate_line(self):
		global do_display_colors
		return click.style(self.fill_character * self.width, fg=(self.foreground_color if do_display_colors else "reset"), bg=self.background_color if do_display_colors else "reset")
	
	def generate_lines(self):
		return [self.generate_line() for _ in range(self.height)]

class Tile:
	
	base_square = None
	other_squares = []
	foreground_color = None
	background_color = None
	fill_character = None
	identifier = None
	starting_row_index = None
	starting_column_index = None
	valid_rotation_indices = []
	
	def get_all_squares(self):
		return [self.base_square] + self.other_squares
	
	def check_position(self, new_row_index, new_column_index, max_row_index, max_column_index, squares):
		position_is_valid = True
		for square in self.get_all_squares():
			square_row_index = new_row_index + square.row_offset
			square_column_index = new_column_index + square.column_offset
			if not square.check_position(square_row_index, square_column_index, max_row_index, max_column_index, squares):
				position_is_valid = False
		return position_is_valid

class ITile(Tile):
	
	foreground_color = "black"
	background_color = "cyan"
	fill_character = "I"
	identifier = "I"
	starting_row_index = 0
	starting_column_index = 4
	valid_rotation_indices = [0, 1]
	
	def __init__(self, cell_width, cell_height, rotation_index=0):
		assert rotation_index in self.valid_rotation_indices
		self.base_square = Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character)
		if rotation_index == 0:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=2)]
		elif rotation_index == 1:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=2)]

class OTile(Tile):
	
	foreground_color = "black"
	background_color = "yellow"
	fill_character = "O"
	identifier = "O"
	starting_row_index = 0
	starting_column_index = 4
	valid_rotation_indices = [0]
	
	def __init__(self, cell_width, cell_height, rotation_index=0):
		assert rotation_index in self.valid_rotation_indices
		self.base_square = Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character)
		if rotation_index == 0:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=1)]

class TTile(Tile):
	
	foreground_color = "black"
	background_color = "magenta"
	fill_character = "T"
	identifier = "T"
	starting_row_index = 1
	starting_column_index = 4
	valid_rotation_indices = [0, 1, 2, 3]
	
	def __init__(self, cell_width, cell_height, rotation_index=0):
		assert rotation_index in self.valid_rotation_indices
		self.base_square = Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character)
		if rotation_index == 0:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1)]
		elif rotation_index == 1:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1)]
		elif rotation_index == 2:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1)]
		elif rotation_index == 3:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1)]

class STile(Tile):
	
	foreground_color = "black"
	background_color = "green"
	fill_character = "S"
	identifier = "S"
	starting_row_index = 0
	starting_column_index = 4
	valid_rotation_indices = [0, 1]
	
	def __init__(self, cell_width, cell_height, rotation_index=0):
		assert rotation_index in self.valid_rotation_indices
		self.base_square = Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character)
		if rotation_index == 0:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=-1)]
		elif rotation_index == 1:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1, column_offset=-1)]

class ZTile(Tile):
	
	foreground_color = "black"
	background_color = "red"
	fill_character = "Z"
	identifier = "Z"
	starting_row_index = 0
	starting_column_index = 4
	valid_rotation_indices = [0, 1]
	
	def __init__(self, cell_width, cell_height, rotation_index=0):
		assert rotation_index in self.valid_rotation_indices
		self.base_square = Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character)
		if rotation_index == 0:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=1)]
		elif rotation_index == 1:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=-1)]

class JTile(Tile):
	
	foreground_color = "black"
	background_color = "blue"
	fill_character = "J"
	identifier = "J"
	starting_row_index = 1
	starting_column_index = 4
	valid_rotation_indices = [0, 1, 2, 3]
	
	def __init__(self, cell_width, cell_height, rotation_index=0):
		assert rotation_index in self.valid_rotation_indices
		self.base_square = Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character)
		if rotation_index == 0:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1, column_offset=-1)]
		elif rotation_index == 1:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1, column_offset=1)]
		elif rotation_index == 2:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=1)]
		elif rotation_index == 3:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=-1)]

class LTile(Tile):
	
	foreground_color = "black"
	background_color = "white"
	fill_character = "L"
	identifier = "L"
	starting_row_index = 1
	starting_column_index = 4
	valid_rotation_indices = [0, 1, 2, 3]
	
	def __init__(self, cell_width, cell_height, rotation_index=0):
		assert rotation_index in self.valid_rotation_indices
		self.base_square = Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character)
		if rotation_index == 0:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1, column_offset=1)]
		elif rotation_index == 1:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=1)]
		elif rotation_index == 2:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, column_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1, column_offset=-1)]
		elif rotation_index == 3:
			self.other_squares = [Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=1), Square(cell_width, cell_height, self.foreground_color, self.background_color, self.fill_character, row_offset=-1, column_offset=-1)]

class Board:
	
	width = 10
	height = 20
	cell_width = 3
	cell_height = 2
	horizontal_character = "-"
	vertical_character = "|"
	intersection_character = "+"
	squares = []
	current_tile_identifier = None
	is_game_over = False
	current_rotation_index = 0
	
	def __init__(self):
		self.squares = [[None] * self.width for _ in range(self.height)]
	
	def add_tile(self, tile, row_index, column_index):
		if tile.check_position(row_index, column_index, self.height, self.width, self.squares):
			for square in tile.get_all_squares():
				self.squares[row_index + square.row_offset][column_index + square.column_offset] = square
			self.current_tile_identifier = tile.identifier
		else:
			self.is_game_over = True
	
	def move_interactive_squares(self, row_delta, column_delta):
		do_move_squares = self.check_position(row_delta, column_delta)
		if do_move_squares:
			base_row_index, base_column_index = self.find_base_indices()
			self.remove_interactive_squares()
			new_tile = None
			if self.current_tile_identifier == "I":
				new_tile = ITile(self.cell_width, self.cell_height, rotation_index=self.current_rotation_index)
			elif self.current_tile_identifier == "O":
				new_tile = OTile(self.cell_width, self.cell_height, rotation_index=self.current_rotation_index)
			elif self.current_tile_identifier == "T":
				new_tile = TTile(self.cell_width, self.cell_height, rotation_index=self.current_rotation_index)
			elif self.current_tile_identifier == "S":
				new_tile = STile(self.cell_width, self.cell_height, rotation_index=self.current_rotation_index)
			elif self.current_tile_identifier == "Z":
				new_tile = ZTile(self.cell_width, self.cell_height, rotation_index=self.current_rotation_index)
			elif self.current_tile_identifier == "J":
				new_tile = JTile(self.cell_width, self.cell_height, rotation_index=self.current_rotation_index)
			elif self.current_tile_identifier == "L":
				new_tile = LTile(self.cell_width, self.cell_height, rotation_index=self.current_rotation_index)
			self.add_tile(new_tile, base_row_index + row_delta, base_column_index + column_delta)
	
	def move_interactive_squares_to_bottom(self):
		is_valid = True
		row_delta = 1
		while is_valid:
			is_valid = self.check_position(row_delta, 0)
			row_delta += 1
		self.move_interactive_squares(row_delta - 2, 0)
	
	def rotate_interactive_squares(self):
		base_row_index, base_column_index = self.find_base_indices()
		new_rotation_index = self.current_rotation_index + 1
		if self.current_tile_identifier == "I":
			new_rotation_index %= 2
			new_tile = ITile(self.cell_width, self.cell_height, rotation_index=new_rotation_index)
			if new_tile.check_position(base_row_index, base_column_index, self.height, self.width, self.squares):
				self.remove_interactive_squares()
				self.add_tile(new_tile, base_row_index, base_column_index)
				self.current_rotation_index = new_rotation_index
		elif self.current_tile_identifier == "O":
			new_rotation_index %= 1
			new_tile = OTile(self.cell_width, self.cell_height, rotation_index=new_rotation_index)
			if new_tile.check_position(base_row_index, base_column_index, self.height, self.width, self.squares):
				self.remove_interactive_squares()
				self.add_tile(new_tile, base_row_index, base_column_index)
				self.current_rotation_index = new_rotation_index
		elif self.current_tile_identifier == "T":
			new_rotation_index %= 4
			new_tile = TTile(self.cell_width, self.cell_height, rotation_index=new_rotation_index)
			if new_tile.check_position(base_row_index, base_column_index, self.height, self.width, self.squares):
				self.remove_interactive_squares()
				self.add_tile(new_tile, base_row_index, base_column_index)
				self.current_rotation_index = new_rotation_index
		elif self.current_tile_identifier == "S":
			new_rotation_index %= 2
			new_tile = STile(self.cell_width, self.cell_height, rotation_index=new_rotation_index)
			if new_tile.check_position(base_row_index, base_column_index, self.height, self.width, self.squares):
				self.remove_interactive_squares()
				self.add_tile(new_tile, base_row_index, base_column_index)
				self.current_rotation_index = new_rotation_index
		elif self.current_tile_identifier == "Z":
			new_rotation_index %= 2
			new_tile = ZTile(self.cell_width, self.cell_height, rotation_index=new_rotation_index)
			if new_tile.check_position(base_row_index, base_column_index, self.height, self.width, self.squares):
				self.remove_interactive_squares()
				self.add_tile(new_tile, base_row_index, base_column_index)
				self.current_rotation_index = new_rotation_index
		elif self.current_tile_identifier == "J":
			new_rotation_index %= 4
			new_tile = JTile(self.cell_width, self.cell_height, rotation_index=new_rotation_index)
			if new_tile.check_position(base_row_index, base_column_index, self.height, self.width, self.squares):
				self.remove_interactive_squares()
				self.add_tile(new_tile, base_row_index, base_column_index)
				self.current_rotation_index = new_rotation_index
		elif self.current_tile_identifier == "L":
			new_rotation_index %= 4
			new_tile = LTile(self.cell_width, self.cell_height, rotation_index=new_rotation_index)
			if new_tile.check_position(base_row_index, base_column_index, self.height, self.width, self.squares):
				self.remove_interactive_squares()
				self.add_tile(new_tile, base_row_index, base_column_index)
				self.current_rotation_index = new_rotation_index
	
	def remove_interactive_squares(self):
		for row_index, row in enumerate(self.squares):
			for column_index, square in enumerate(row):
				if square != None and square.interactive:
					self.squares[row_index][column_index] = None
	
	def find_base_indices(self):
		for row_index, row in enumerate(self.squares):
			for column_index, square in enumerate(row):
				if square != None and square.interactive:
					if square.check_base_status():
						return row_index, column_index
	
	def check_position(self, row_delta, column_delta):
		is_valid = True
		for row_index, row in enumerate(self.squares):
			new_row_index = row_index + row_delta
			for column_index, square in enumerate(row):
				new_column_index = column_index + column_delta
				if square != None and square.interactive and not square.check_position(new_row_index, new_column_index, self.height, self.width, self.squares):
					is_valid = False
		return is_valid
	
	def clean(self):
		do_lock = False
		for row_index, row in enumerate(self.squares):
			for column_index, square in enumerate(row):
				if row_index < self.height - 1:
					adjacent_square = self.squares[row_index + 1][column_index]
				do_lock_based_on_adjacent_square = row_index + 1 == self.height or (adjacent_square != None and not adjacent_square.interactive)
				if square != None and square.interactive and do_lock_based_on_adjacent_square:
					do_lock = True
		if do_lock:
			for row in self.squares:
				for square in row:
					if square != None and square.interactive:
						square.interactive = False
		did_remove_some_row = False
		for row_index, row in enumerate(self.squares):
			do_remove_row = True
			for square in row:
				if square == None:
					do_remove_row = False
			if do_remove_row:
				self.squares[row_index] = [None] * self.width
				for inversed_other_row_index, other_row in enumerate(reversed(self.squares[:row_index])):
					self.squares[row_index - inversed_other_row_index] = other_row
					self.squares[row_index - inversed_other_row_index - 1] = [None] * self.width
				did_remove_some_row = True
		if self.squares[0] != [None] * self.width:
			self.is_game_over = True
			return
		if do_lock or did_remove_some_row:
			self.current_rotation_index = 0
			new_tiles = [ITile(self.cell_width, self.cell_height), OTile(self.cell_width, self.cell_height), TTile(self.cell_width, self.cell_height), STile(self.cell_width, self.cell_height), ZTile(self.cell_width, self.cell_height), JTile(self.cell_width, self.cell_height), LTile(self.cell_width, self.cell_height)]
			new_tile = random.choice(new_tiles)
			self.add_tile(new_tile, new_tile.starting_row_index, new_tile.starting_column_index)
	
	def generate_border_line(self):
		global do_blink
		line_str = self.intersection_character
		for _ in range(self.width):
			line_str += self.horizontal_character * self.cell_width
			line_str += self.intersection_character
		return click.style(line_str, blink=do_blink)
	
	def generate_lines(self):
		global do_blink
		lines = [self.generate_border_line()]
		for row_index, row in enumerate(self.squares):
			for cell_line_index in range(self.cell_height):
				line = click.style(self.vertical_character, blink=do_blink)
				for column_index, square in enumerate(row):
					line += click.style(" " * self.cell_width) if square == None else square.generate_line()
					line += click.style(self.vertical_character, blink=do_blink)
				lines.append(line)
			lines.append(self.generate_border_line())
		return lines

click.clear()
click.secho("Welcome to Textris!", bold=True)
click.secho("Press any key to continue.", blink=True)
click.pause(info="")
board = Board()
new_tiles = [ITile(board.cell_width, board.cell_height), OTile(board.cell_width, board.cell_height), TTile(board.cell_width, board.cell_height), STile(board.cell_width, board.cell_height), ZTile(board.cell_width, board.cell_height), JTile(board.cell_width, board.cell_height), LTile(board.cell_width, board.cell_height)]
new_tile = random.choice(new_tiles)
board.add_tile(new_tile, new_tile.starting_row_index, new_tile.starting_column_index)
input_character = None
characters_typed = ""
printable_characters = "abcdefghijklmnopqrstuvwxyz1234567890 .,<>;:/?'\"[]{}\\|-_=+!@#$%^&()`~"
global do_blink
global do_display_colors
do_blink = False
do_display_colors = False
banned_words = [b"ZnVjaw==", b"c2hpdA==", b"Y3VudA==", b"ZGljaw==", b"YXNz"]
while input_character != "q":
	click.clear()
	for line in board.generate_lines():
		click.echo(line)
	click.echo(characters_typed)
	if "blink" in characters_typed:
		do_blink = True
	if "color" in characters_typed:
		do_display_colors = True
		characters_typed = characters_typed.replace("*", click.style("*", fg="red"))
	input_character = getkey.getkey().lower()
	characters_typed += input_character if input_character in printable_characters else ""
	for banned_word in banned_words:
		actual_banned_word = base64.b64decode(banned_word).decode("utf-8")
		if actual_banned_word in characters_typed:
			characters_typed = characters_typed.replace(actual_banned_word, click.style("*", fg=("red" if do_display_colors else "reset")) * len(actual_banned_word))
#			click.clear()
#			click.secho("No bad words allowed!", fg="red", bold=True)
#			click.secho("Press any key to continue.", blink=True)
#			click.pause(info="")
	if input_character == getkey.keys.W:
		board.rotate_interactive_squares()
		continue
	elif input_character == getkey.keys.S:
		board.move_interactive_squares(1, 0)
	elif input_character == getkey.keys.A:
		board.move_interactive_squares(0, -1)
		continue
	elif input_character == getkey.keys.D:
		board.move_interactive_squares(0, 1)
		continue
	elif input_character == getkey.keys.SPACE:
		board.move_interactive_squares_to_bottom()
	else:
		continue
	board.clean()
	if board.is_game_over:
		click.clear()
		click.secho("You lost!", fg="red", bold=True)
		click.secho("Press any key to continue.", blink=True)
		click.pause(info="")
		break
click.clear()