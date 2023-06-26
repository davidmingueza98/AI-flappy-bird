import time
import os
import random

import pygame
import neat


# CONSTANTS DEFINITIONS

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

GEN = 0


class Bird:
	"""
	Represents the bird in the game. Defines basic properties as the image, starting position,
	orientation and velocity. Implements interaction functions as move and jump in the air.
	"""
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROT_VEL = 20
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		"""
		Sets the starting position. Tilt equal to zero means flat.
		"""
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		"""
		Implements the jump. Negative velocity is to go up.
		"""
		self.vel = -10.5
		self.tick_count = 0
		self.height = self.y

	#every single frame
	def move(self):
		"""
		Implements the movement. Executed every single frame.
		Determines how much the bird is moving down or up, sets a terminal velocity
		and defines the conditions when the nose dive start.
		"""
		self.tick_count += 1
		d = self.vel * self.tick_count + 0.5*(3)*self.tick_count**2

		#terminal velocity
		if d >= 16:
			d = d/abs(d) * 16

		if d < 0:
			d -= 2

		self.y += d

		#where moving up or we pass a horizontal limit
		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			#where moving down, nose dive
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self, win):
		"""
		Selects and prints an image in the screen depending on an index
		that loops around the animation base images.
		"""
		self.img_count += 1

		if self.img_count <= self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count <= self.ANIMATION_TIME * 2:
			self.img = self.IMGS[1]
		elif self.img_count <= self.ANIMATION_TIME * 3:
			self.img = self.IMGS[2]
		elif self.img_count <= self.ANIMATION_TIME * 4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME * 4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		#no flap going down
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2

		#rotate the image with a library function and set the center
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)


	def get_mask(self):
		"""
		Generates a mask for to perform collisions
		"""
		return pygame.mask.from_surface(self.img)


class Pipe:
	#how much space between pipes
	GAP = 200
	VEL = 5

	#only x because the size is random
	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0
		self.bottom = 0
		#flip the image to generate the two pipes
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG

		#for collisions
		self.passed = False
		#what is the gap
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	#pixel perfect collision with masks(pixel transparents)
	#not so efficient with squares
	#every time move check if collide
	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		#offset how much away are the corners
		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		#finding point of collision
		#returns None if not collide
		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point:
			return True

		return False


class Base:
	#same velocity as the bird
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		#if one image comes out of bonce, move to front
		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
	#draw in the window
	win.blit(BG_IMG, (0,0))

	#draw pipes
	for pipe in pipes:
		pipe.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

	text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
	win.blit(text, (10, 10))

	base.draw(win)

	for bird in birds:
		bird.draw(win)

	pygame.display.update()

def play(genomes, config):
	global GEN 
	GEN += 1
	nets = []
	ge = []
	birds = []

	#initialize net
	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230, 350))
		g.fitness = 0
		ge.append(g)


	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	#set the ticks
	clock = pygame.time.Clock()

	score = 0

	run = True
	while run:
		#almost 30 ticks per second
		clock.tick(30)
		#iterate over all the events
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				#quit the game
				run = False
				pygame.quit()
				quit()

		pipe_ind = 0
		if len(birds) > 0:
			#get the first bird, if pipe passed look to the next 
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1
		else:
			#quit running the game without birds
			run = False
			break

		for x, bird in enumerate(birds):
			bird.move()
			#if bird is alive increment the fitness
			ge[x].fitness += 0.1

			#pass the parameters to the net, position and distance to the extremes of the pipe
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
			#dont hit the floor
			if output[0] > 0.5:
				bird.jump()


		rem = []
		add_pipe = False
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					#ge[x].fitness -= 1 #penalize
					#eliminate bird
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True

			#pipes passed to remove
			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			pipe.move()

		if add_pipe:
			score += 1
			for g in ge:
				#if score gained, fitness too
				g.fitness += 5
			pipes.append(Pipe(600))

		for r in rem:
			pipes.remove(r)

		#if the bird is out of bounces eliminate
		for x, bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		#its an ideal bird
		if score > 50:
			run = False
			#the model could be saved with pickle
			#pickle.dump(nets[0],open("best.pickle", "wb"))
			break

		base.move()
		draw_window(win, birds, pipes, base, score, GEN)

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
								neat.DefaultSpeciesSet, neat.DefaultStagnation,
								config_path)
	#create a population
	p = neat.Population(config)
	#set the output
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	#call the main fuction 50 times with the parameters
	winner = p.run(play, 50)

	#the best genome now is in winner


if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)


"""
inputs: bird  Y, top pipe and bottom pipe (only one key to move)
outputs: jump?
activation function: Tanh (-1,1)
population size: 100 by default by generation
fitness function: how the birds gonna get better, the rewards (score!!)
max generations: set a max of 30 to cut the program
"""