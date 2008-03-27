"""
Original author Peter Angstadt (http://pete.nextraztus.com/)
see license.txt
"""

if __name__ == '__main__':
	import pyglet
	from pyglet.window import key
	from pyglet.gl import *
	import game

	win = pyglet.window.Window(320, 240, caption="Wake Breaker", resizable=True)

	@win.event
	def on_key_press(symbol, modifiers):
		if symbol == key.LEFT:   g.keyDown(game.G_LEFT)
		if symbol == key.UP:     g.keyDown(game.G_UP)
		if symbol == key.RIGHT:  g.keyDown(game.G_RIGHT)
		if symbol == key.DOWN:   g.keyDown(game.G_DOWN)
		if symbol == key.RETURN: g.keyDown(game.G_OK)
		if symbol == key.NUM_1:  g.keyDown(game.G_DEVICE1)
		if symbol == key.NUM_2:  g.keyDown(game.G_DEVICE2)

	@win.event
	def on_key_release(symbol, modifiers):
		if symbol == key.LEFT:   g.keyUp(game.G_LEFT)
		if symbol == key.UP:     g.keyUp(game.G_UP)
		if symbol == key.RIGHT:  g.keyUp(game.G_RIGHT)
		if symbol == key.DOWN:   g.keyUp(game.G_DOWN)
		if symbol == key.RETURN: g.keyUp(game.G_OK)
		if symbol == key.NUM_1:  g.keyUp(game.G_DEVICE1)
		if symbol == key.NUM_2:  g.keyUp(game.G_DEVICE2)

	@win.event
	def on_resize(width, height):
		fov = 45.0
		near = 1.0
		far = 256.0
		ratio = float(width) / float(height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(fov, ratio, near, far)
		glMatrixMode(GL_MODELVIEW)
		glViewport(0, 0, width, height)
		return pyglet.event.EVENT_HANDLED

	g = game.Game()
	g.create()

	pyglet.clock.set_fps_limit(30)
	while not win.has_exit:
		win.dispatch_events()
		frame_time = pyglet.clock.tick()
		#win.clear()
		g.menu()
		win.flip()
