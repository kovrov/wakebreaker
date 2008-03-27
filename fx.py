import ctypes
import random
from pyglet.gl import *
from util import Vector3


class Particle(ctypes.Structure):
	_fields_ = [('pos', Vector3), ('velocity', Vector3), ('life', GLfloat)]


class ParticleSystem:
	def __init__(self, numParticles, maxLife, pos, dir):
		# assign in the particle system properties
		self.__emitPoint = Vector3(pos)
		self.__dir = Vector3(dir)
		self.__maxLife = maxLife
		# build the new array of particles
		self.__particles = (Particle*numParticles)()
		self.__particles_ptr = ctypes.pointer(self.__particles[0].pos)
		# initialize all the particles
		for p in self.__particles:
			self.resetParticle(p)

	# moves the emission point
	def move(self, newEmitPoint):
		self.__emitPoint[:] = newEmitPoint

	def redirect(self, dir):
		""" Changes the particle system's direction """
		self.__dir[:] = dir
	
	def resetParticle(self, particle):
		# set the position
		particle.pos[:] = self.__emitPoint
		# reset the life
		particle.life = self.__maxLife + random.uniform(-5.0, 5.0)
		# Add some variety to the velocities
		# Assign them in, alter the direction by the factor
		particle.velocity.x = random.uniform(0.0, 0.33) * self.__dir.x
		particle.velocity.y = random.uniform(0.0, 0.25) * self.__dir.y
		particle.velocity.z = random.uniform(0.0, 0.33) * self.__dir.z

	def render(self):
		glPushMatrix()
		# Turn of texturing, it would be too expensive
		glDisable(GL_TEXTURE_2D)
		# Attenuate the particle size based on distance
		glPointSize(8.0)
		glPointParameterfv(GL_POINT_DISTANCE_ATTENUATION, (GLfloat*3)(0.0, 0.05, 0.005))
		glVertexPointer(3, GL_FLOAT, ctypes.sizeof(Particle), self.__particles_ptr)
		glDrawArrays(GL_POINTS, 0, len(self.__particles))
		glEnable(GL_TEXTURE_2D)
		glPopMatrix()	
	
	def update(self):
		"""
		Updates particle position and life,  resets them if they need to be
		"""
		for p in self.__particles:
			p.life -= 1
			if p.life < 0:
				self.resetParticle(p)
			p.pos += p.velocity
