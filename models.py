import math
import random

import pyglet
from pyglet.gl import *

from util import Vector3
import renderer
import scene
import fx

WORLD_WIDTH	 = 175	
WORLD_HEIGHT = 175

MAX_SPEED = 1.0 # boat's maximum speed
MAX_CHECKPOINTS = 16


class Racer:
	def __init__(self, model_manager, model):
		# get the 3d model data
		if model == scene.BOAT1:
			self.ri = renderer.RenderInstance(model_manager.getBoat1())
		else: # model == BOAT2:
			self.ri = renderer.RenderInstance(model_manager.getBoat2())
		# rotate so he's always right side up
		self.ri.rotation[:] = -90.0, 0.0, 90.0
		self.ri.scale[:] = 0.5, 0.5, 0.5
		self.ri.position[:] = WORLD_WIDTH / 2.0, 0.0, WORLD_HEIGHT / 2.0
		# update his rotation and direction
		rad = math.radians(self.ri.rotation.y)
		self.dir = Vector3(math.cos(rad), 0.0, math.sin(rad))
		self.nextCPPos = Vector3()
		self.up = True  # used in making the boat bob slight
		self.finished = False  # whether or not we are done with the race
		self.speed = 0 # ship's current speed
		self.nextCheckPoint = 0 # which check point he's aiming for
		self.currLap = 0 # which lap he's on
		self.hasRotated = True # for rotation optimization
		# the water spray that shoots out behind the boat
		self.spray = fx.ParticleSystem(200, 15, self.ri.position, Vector3(0.0, 1.0, 0.0))


	# Keeps the racer inside the seascape
	def boundsCheck(self):
		# check the player against each part fo the world, slow him down if he hit
		pos = self.ri.position.copy()
		if pos.x > WORLD_WIDTH:
			pos.x = WORLD_WIDTH
			self.speed = self.speed * 0.5
		if pos.x < 0:
			pos.x = 0
			self.speed = self.speed * 0.5
		if pos.z > WORLD_HEIGHT:
			pos.z = WORLD_HEIGHT
			self.speed = self.speed * 0.5
		if pos.z < 0:
			pos.z = 0
			self.speed = self.speed * 0.5
		# make the racer bob up and down
		if self.up and self.speed > 0:
			pos.y += 0.02 * self.speed
		elif self.speed > 0:
			pos.y -= 0.02 * self.speed
		if pos.y >= 0.2:
			self.up = False
		if pos.y < -0.05:
			self.up = True
		self.ri.position[:] = pos


	def rotate(self, r):
		self.hasRotated = True
		# this makes sure the rotation doesn't exceed 360 degrees
		if self.ri.rotation.y + r > 360.0 or self.ri.rotation.y + r < -360.0:
			self.ri.rotation.y = 0
		self.ri.rotation.y += r

	def update(self):
		if self.hasRotated:
			# rotate the ship if needed
			rad = math.radians(self.ri.rotation.y)
			self.dir.x = math.cos(rad)
			self.dir.z = math.sin(rad)
			self.hasRotated = False
		# move him in
		self.ri.translate((self.speed * self.dir.x, 0, -self.dir.z * self.speed))
		# Bounds check him against the world
		self.boundsCheck()
		# slow him down
		if self.speed - 0.01474 > 0:
			self.speed -= 0.01474
		elif self.speed - 0.01474 < 0:
			self.speed += 0.03
		# halt him if too slow
		if self.speed <= 0.04 and self.speed >= -0.04:
			self.speed = 0
		# keep the particles with us
		self.updateSpray()


	def updateAI(self, player):
		# we hit an island, this on most cases, corrects the problem
		if self.speed < 0.3:
			self.increaseSpeed(0.025)
			# go around it
			self.dir.x = math.cos(math.radians(90.0))
			self.dir.z = math.sin(math.radians(90.0))
			self.hasRotated = False
			# move him in
			self.ri.translate((self.speed * self.dir.x, 0.0, -self.dir.z * self.speed))
		else:
			self.increaseSpeed(0.025)		
			# build a normalized direction vector
			desiredDir = self.ri.position - self.nextCPPos
			desiredDir.y = 0.0
			mag = math.sqrt(desiredDir.x * desiredDir.x + desiredDir.z * desiredDir.z)
			n = 1.0 / mag
			desiredDir.x *= n
			desiredDir.z *= n
			# slow the AI down a little
			randFac = (8.0 + random.uniform(0.0, 0.00005)) / 10.0
			finalX = -desiredDir.x * self.speed * randFac
			finalZ = -desiredDir.z * self.speed * randFac
			# make the boat "look" forward!!
			if finalZ < 0: k = 90.0
			else: k = -90.0
			self.ri.rotation.y = math.degrees(math.atan(finalX / finalZ)) + k
			# move the boat		
			self.ri.translate((finalX, 0.0, finalZ))
		# keep him in the water
		self.boundsCheck()
		# move the spray trail with him
		self.updateSpray()

	def updateSpray(self):
		# keep it the spray trail right with the boat
		self.spray.move(self.ri.position)
		# also keep it spraying in the right direction
		if self.speed > 0:
			newDir = Vector3(self.dir.x, 0.1, -self.dir.z)
		else:
			newDir = Vector3(0.0, 0.0, 0.0)
		self.spray.redirect(newDir)
		self.spray.update()

	def increaseSpeed(self, s):
		if self.speed < MAX_SPEED:
			self.speed += s
		if self.speed > MAX_SPEED:
			self.speed = MAX_SPEED

	# Renders the ship
	def render(self, renderer):
		# draw the ship
		renderer.render(self.ri)
		# draw the spray trail
		self.spray.render()


class RaceCourse:
	# 1. Generates a random race course within the donut described by min and
	#    max radius
	# 2. Adds racers to the race course and sets up the race course
	def __init__(self, center, minRadius, maxRadius, racers, model_manager):
		self.checkPoints = [renderer.RenderInstance(model_manager.getCheckPoint()) for i in xrange(MAX_CHECKPOINTS)]
		# calculate the angle apart each checkpoint has to be
		interval = math.pi * 2.0 / MAX_CHECKPOINTS
		angle = 0.0
		for cp in self.checkPoints:
			x = math.cos(angle) * random.uniform(minRadius, maxRadius) + center.x
			z = math.sin(angle) * random.uniform(minRadius, maxRadius) + center.z
			cp.position[:] = x, 1.0, z
			cp.scale[:] = 1.0, 1.0, 1.0
			cp.rotation[:] = -90.0, 0.0, 0.0
			# advance the angle
			angle -= interval
		# set the racers and the amount of them
		self.racers = racers
		# place all the racers at the first checkpoint, each racer a bit behind
		# the one before him
		for racer in self.racers:
			# set everyone at the starting checkpoint
			racer.nextCheckPoint = 0
			racer.CurrLap = 0
			racer.ri.position[:] = self.checkPoints[0].position
			racer.nextCPPos[:] = self.checkPoints[0].position
		self.racers[0].rotate(90.0)
		# load the textures for the checkpoints
		self.cpOnTex = pyglet.image.load('checkpointon.png').get_texture()
		self.cpOffTex = pyglet.image.load('checkpointoff.png').get_texture()
		self.playerNextCP = 0


	def render(self, ri):
		glPushMatrix()
		self.checkPoints[self.playerNextCP].renderData.texture = self.cpOnTex
		ri.render(self.checkPoints[self.playerNextCP])
		self.checkPoints[self.playerNextCP].renderData.texture = None
		if self.playerNextCP + 1 == MAX_CHECKPOINTS:
			self.checkPoints[0].renderData.texture = self.cpOffTex
			ri.render(self.checkPoints[0])
			self.checkPoints[0].renderData.texture = None
		else:
			self.checkPoints[self.playerNextCP + 1].renderData.texture = self.cpOffTex
			ri.render(self.checkPoints[self.playerNextCP + 1])
			self.checkPoints[self.playerNextCP + 1].renderData.texture = None
		glPopMatrix()


	# Updates the racers, returns 1 if player won, -1 if player lost, and 0
	# if race is still in progress
	def update(self):
		# loop through each racer
		for racer in self.racers:
			# see if he has collided with the next checkpoint
			nextCP = self.checkPoints[racer.nextCheckPoint].position
			pos = racer.ri.position
			dist = (nextCP.x - pos.x) * (nextCP.x - pos.x) + (nextCP.z - pos.z) * (nextCP.z - pos.z)
			radii = 3.0 * 3.0
			if dist < radii:
				# the player has reached the next checkpoint
				# assign him to the next checkpoint
				CP = racer.nextCheckPoint + 1
				# he has reached the last checkpoint
				if CP == MAX_CHECKPOINTS:
					# increment his lap count
					racer.currLap += 1
					if racer.currLap == 3:
						# we have a winner
						racer.finished = True
					CP = 0
				# assign him his new checkpoint
				racer.nextCheckPoint = CP
				racer.nextCPPos[:] = self.checkPoints[CP].position
				if self.racers[0] is racer:
					self.playerNextCP = CP
		return 1



class Seascape:
	def __init__(self, mm):
		# used in water animation
		self.texTranslate = 0
		self.waterMoved = True
		self.models = [renderer.RenderInstance(mm.getRandomSeascapeModel()) for i in xrange(15)]
		for model in self.models:
			# generate a random x and z
			model.position[:] = random.uniform(0.0, WORLD_WIDTH), 0.0, random.uniform(0.0, WORLD_HEIGHT)
			# generate a random rotation
			model.rotation[:] = -90.0, random.uniform(0.0, 360.0), 0.0
		# set up the renderInstance
		# Set up the sea floor
		vertices = (
			(-2,						0.0,	-2.0),
			(-2,						0.0,	WORLD_HEIGHT / 2.0 + 2.0),
			(WORLD_WIDTH / 2.0 + 2.0,	0.0,	-2.0),
			(WORLD_WIDTH / 2.0 + 2.0,	0.0,	WORLD_HEIGHT / 2.0 + 2.0))
		indices = (0, 1, 2, 2, 1, 3)
		uvmap = ((0.0, 0.0), (15.0, 0.0), (0.0, 15.0), (15.0, 15.0))
		texture = pyglet.image.load('watertex.png').get_texture()
		self.sea = renderer.RenderInstance(renderer.RenderData(vertices, indices, uvmap, texture))
		self.sea.position[:] = 0.0, 0.0, 0.0

	# checks if anything collided with the islands
	def collided(self, pos, radius):
		for model in self.models:
			# if the distance between the two points is more than the two radii,
			# no collision calculate the distance squared
			dist = (model.position.x - pos.x) * (model.position.x - pos.x) + (model.position.z - pos.z) * (model.position.z - pos.z)
			radii = (radius + 1.5) * (radius + 1.5)
			if dist < radii:
				return True
		return False

	# renders the seascape
	def render(self, renderer):
		# render all the models first
		for model in self.models:
			renderer.render(model)
			# draw reflection
			model.scale[:] = 2.0, -2.0, 2.0
			renderer.render(model)
			model.scale[:] = 2.0,  2.0, 2.0
		# make sure the m_texTranslate never goes out of bounds
		if self.waterMoved:
			self.texTranslate -= 0.005
		else:
			self.texTranslate += 0.005
		if self.texTranslate > 15.0:
			self.waterMoved = True
		if self.texTranslate < -15.0:
			self.waterMoved = False
		# Now render the water plane
		# We render it 4 times, so that it forms a giant block
		glPushMatrix()
		# set up blending
		glEnable(GL_BLEND)
		glColor4f(1.0, 1.0, 1.0, 0.6)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		self.renderWater(renderer)
		glTranslatef(0.0, 0.0, WORLD_HEIGHT / 2 + 4)
		self.renderWater(renderer)
		glTranslatef(WORLD_HEIGHT / 2.0 + 4.0, 0.0, 0.0)
		self.renderWater(renderer)
		glTranslatef(0.0, 0.0, -(WORLD_HEIGHT / 2.0 + 4.0))
		self.renderWater(renderer)
		# turn of blending and restore the original color
		glDisable(GL_BLEND)
		glColor4f(1.0, 1.0, 1.0, 1.0)
		glPopMatrix()

	# Renders the water
	def renderWater(self, renderer):
		glMatrixMode(GL_TEXTURE)
		# shift the texture coords to simulate motion
		glTranslatef(self.texTranslate, self.texTranslate, 0.0)
		glRotatef(35.0, 0.0, 0.0, 1.0)
		glColor4f(1.0, 1.0, 1.0, 0.6)
		# render the first sea quad
		renderer.render(self.sea)
		# reset the texture matrix
		glLoadIdentity()
		# now scale and move the tex coords
		glScalef(0.7, 0.7, 0.7)
		glTranslatef(-self.texTranslate, 0.0, 0.0)
		# change the transparency
		glColor4f(1.0, 1.0, 1.0, 0.35)
		# render another water quad just slightly above the previous one
		glMatrixMode(GL_MODELVIEW)
		self.sea.translate((0.0, 0.1, 0.0))
		renderer.render(self.sea)
		self.sea.translate((0.0 ,-0.1, 0.0))
		glMatrixMode(GL_TEXTURE)
		# reset the texture matrix again
		glLoadIdentity()
		# change back to modelview
		glMatrixMode(GL_MODELVIEW)
