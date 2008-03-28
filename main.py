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

	key_map = {
		key.LEFT:   game.G_LEFT,
		key.UP:     game.G_UP,
		key.RIGHT:  game.G_RIGHT,
		key.DOWN:   game.G_DOWN,
		key.RETURN: game.G_OK,
		key.NUM_1:  game.G_DEVICE1,
		key.NUM_2:  game.G_DEVICE2}

	@win.event
	def on_key_press(symbol, modifiers):
		if key_map.has_key(symbol):
			g.keysDown[key_map[symbol]] = True
			return pyglet.event.EVENT_HANDLED

	@win.event
	def on_key_release(symbol, modifiers):
		if key_map.has_key(symbol):
			g.keysDown[key_map[symbol]] = False
			return pyglet.event.EVENT_HANDLED

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

	pyglet.clock.set_fps_limit(30)
	while not win.has_exit:
		win.dispatch_events()
		frame_time = pyglet.clock.tick()
		#win.clear()
		g.menu()
		win.flip()
