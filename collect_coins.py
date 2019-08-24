"""
Sprite Collect Coins

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_collect_coins
"""

import random
import arcade
import os

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.2
COIN_COUNT = 10
COIN_MULTIPLES = 10

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Collect Coins Example"

START_RATE = 1

class Coin(arcade.Sprite):
    def __init__(self, filename: str = None, scale: float = 1, rate: int = START_RATE):
        super().__init__(filename, scale)
        self.rate = rate

    def update(self):
        self.center_y -= self.rate

        # See if we went off-screen
        if self.top < 0:
            # Reset the coin to a random spot above the screen
            self.center_y = random.randrange(SCREEN_HEIGHT + 20,
                                            SCREEN_HEIGHT + 100)
            self.center_x = random.randrange(SCREEN_WIDTH)
            self.rate += 1

class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.player_list = None
        self.coin_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0
        self.coin_count = COIN_COUNT
        self.rate = START_RATE

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Score
        self.score = 0

        # Set up the player
        # Character image from kenney.nl
        self.player_sprite = arcade.Sprite(
            "images/character.png", SPRITE_SCALING_PLAYER
        )
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # Create the coins
        for _ in range(self.coin_count):

            # Create the coin instance
            # Coin image from kenney.nl
            coin = Coin("images/coin_01.png", SPRITE_SCALING_COIN, rate=self.rate)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.coin_list.draw()
        self.player_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score} / {self.coin_count}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
        coins_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.coin_list
        )

        # Loop through each colliding sprite, remove it, and add to the score.
        for coin in coins_hit_list:
            coin.kill()
            self.score += 1

        if self.score >= self.coin_count:
            self.coin_count += COIN_MULTIPLES
            self.rate += 1
            self.setup()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.TAB:
            self.setup()
        elif symbol == arcade.key.ESCAPE:
            arcade.close_window()
        elif symbol == arcade.key.KEY_1:
            self.coin_count = 1 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_2:
            self.coin_count = 2 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_3:
            self.coin_count = 3 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_4:
            self.coin_count = 4 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_5:
            self.coin_count = 5 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_6:
            self.coin_count = 6 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_7:
            self.coin_count = 7 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_8:
            self.coin_count = 8 * COIN_MULTIPLES
            self.setup()
        elif symbol == arcade.key.KEY_9:
            self.coin_count = 9 * COIN_MULTIPLES
            self.setup()


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
