import random
import renderer
import data


BOAT1, BOAT2 = xrange(2)


class ModelManager:
	def __init__(self):
		self.boat1 = None
		self.boat2 = None
		self.chest = None
		self.island1 = None
		self.island2 = None
		self.checkPoint = None

	# These return RenderData's with the requested model

	def getIsland1(self):
		if not self.island1:
			d = data.loadIsland1()
			self.island1 = renderer.RenderData(d['vertices'], d['indices'], d['uvmap'], d['texture'])
		return self.island1


	def getIsland2(self):
		if not self.island2:
			d = data.loadIsland2()
			self.island2 = renderer.RenderData(d['vertices'], d['indices'], d['uvmap'], d['texture'])
		return self.island2;


	def getBoat2(self):
		if not self.boat2:
			d = data.loadBoat2()
			self.boat2 = renderer.RenderData(d['vertices'], d['indices'], d['uvmap'], d['texture'])
		return self.boat2


	def getBoat1(self):
		if not self.boat1:
			d = data.loadBoat1()
			self.boat1 = renderer.RenderData(d['vertices'], d['indices'], d['uvmap'], d['texture'])
		return self.boat1


	def getRandomSeascapeModel(self):
		return random.choice((self.getIsland1, self.getIsland2))()


	def getCheckPoint(self):
		if not self.checkPoint:
			d = data.loadCheckpoint()
			self.checkPoint = renderer.RenderData(d['vertices'], d['indices'], d['uvmap'], d['texture'])
		return self.checkPoint
