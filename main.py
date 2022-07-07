import sys
import pyglet
from pyglet.window import key
import cv2

from RL import BaseEnvironment as Environment
from RL import EvaluationError

class Agent:
	# Agent initialization
	def __init__(self, environment):
		""" Initializes agent """
		# KeyStateHandler handles key states.
		key_handler = key.KeyStateHandler()
		# Let's register our key handler to the environment's key listener.
		environment.unwrapped.window.push_handlers(key_handler)
		self.env = environment
		self.key_handler = key_handler

	def send_commands(self, dt):
		''' Agent control loop '''
		# This function updates the robot behaviour. Parameter dt is the elapsed time, in
		# milliseconds, since the last update call.
		# At each step, the agent produces an action in the form of two reals in [-1,1]:
		#   pwm_left, pwm_right = left motor power, right motor power
		# Play with these values and figure out how to make your own remote control duckiebot!
		vel, angle = 0, 0

		base_speed = 0.8
		base_turn_speed = 10

		if self.key_handler[key.UP] or self.key_handler[key.W]:
			vel = base_speed

		if self.key_handler[key.DOWN] or self.key_handler[key.S]:
			vel = -base_speed

		if self.key_handler[key.LEFT] or self.key_handler[key.A]:
			angle = base_turn_speed

		if self.key_handler[key.RIGHT] or self.key_handler[key.D]:
			angle = -base_turn_speed

		# At each step, the environment may (or may not) change given your actions. Function step takes
		# as parameter the two motor powers as action and returns an observation (what the robot is
		# currently seeing), a reward (mostly used for reinforcement learning), whether the episode is
		# done (also used for reinforcement learning) and some info on the elapsed episode.  Let's ignore
		# return values for now.
		self.env.render()
		return self.env.step(vel, angle)

		

def main():
	# We'll use our version of Duckietown: Duckievillage. This environment will be where we'll run most
	# our tasks.

	env = Environment(
		
		seed = 101,
		map_name = 'loop_empty',
		draw_curve = False,
		draw_bbox = False,
		domain_rand = False,
		distortion = False,
		top_down = False,

		# map_name = 'maps/circuit.yaml',
		# is_external_map = True,

	)

	# Let's reset the environment to get our Duckiebot somewhere random.
	env.reset()
	# This function is used to draw the environment to a graphical user interface using Pyglet.
	env.render()

	# We use this function for on-press key events (not something we use for real-time feedback,
	# though). We'll register ESC as our way out of the Matrix.
	@env.unwrapped.window.event
	def on_key_press(symbol, modifiers):
		if symbol == key.ESCAPE:
			env.close()
			sys.exit(0)
		env.render()

	# Instantiante agent
	agent = Agent(env)
	track_dt = 0

	def loop(dt: float):
		try:
			ret = agent.send_commands(dt)
			print(f"Score : {ret[1]}")
			# print(f"Tile : {env.current_tile()}")

		except EvaluationError as e:
			env.close()
			sys.exit(0)

	# Call send_commands function from periodically (to simulate processing latency)
	pyglet.clock.schedule_interval(loop, 1.0 / env.unwrapped.frame_rate)
	# Now run simulation forever (or until ESC is pressed)
	pyglet.app.run()
	env.close()

if __name__ == '__main__':
	main()