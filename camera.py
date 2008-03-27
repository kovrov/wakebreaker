from pyglet.gl import *
from util import Vector3


class Camera:
	def __init__(self):
		self.eye       = Vector3(0, 0,-10)  # position
		self.center    = Vector3(0, 0,  0)  # what the camera is looking at
		self.up        = Vector3(0, 1,  0)  # the up vector
		self.direction = Vector3()  # shoild be normalized vector?

	def translate(self, trans):
		""" moves the camera """
		self.eye += trans

	def lookAt(self, pos, center, up):
		""" fills the eye, center, up vectors for use when the camera updates """
		self.eye[:] = pos
		self.center[:] = center
		self.up[:] = up
	
	def update(self):
		gluLookAt(self.eye.x,    self.eye.y,    self.eye.z,
 		          self.center.x, self.center.y, self.center.z,
		          self.up.x,     self.up.y,     self.up.z)
