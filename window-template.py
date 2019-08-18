import arcade

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
COORDINATE_X = 0
COORDINATE_Y = 1


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width: int, height: int):
        super().__init__(width, height)

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        # Set up your game here
        self.rate = 10
        self.objects = list()
        self.current_object = 0
        self.objects.append({"name": "pine_tree_1", "coordinates": [50, 250]})
        self.objects.append({"name": "pine_tree_2", "coordinates": [350, 320]})
        self.objects.append({"name": "bird_1", "coordinates": [70, 500]})
        self.objects.append({"name": "bird_2", "coordinates": [470, 550]})

    #        self.pine_tree_1_x = 50
    #        self.pine_tree_1_y = 250

    def get_coordinates(self, name: str) -> tuple:
        for obj in self.objects:
            if obj["name"] == name:
                return obj["coordinates"]

    def get_current_coordinates(self) -> list:
        return self.objects[self.current_object]["coordinates"]

    def draw_background(self):
        """
        This function draws the background. Specifically, the sky and ground.
        """
        # Draw the sky in the top two-thirds
        arcade.draw_lrtb_rectangle_filled(
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_HEIGHT * (1 / 3),
            arcade.color.SKY_BLUE,
        )

        # Draw the ground in the bottom third
        arcade.draw_lrtb_rectangle_filled(
            0, SCREEN_WIDTH, SCREEN_HEIGHT / 3, 0, arcade.color.DARK_SPRING_GREEN
        )

    def draw_bird(self, coordinates: tuple):
        """
        Draw a bird using a couple arcs.
        """
        x, y = coordinates
        arcade.draw_arc_outline(x, y, 20, 20, arcade.color.BLACK, 0, 90)
        arcade.draw_arc_outline(x + 40, y, 20, 20, arcade.color.BLACK, 90, 180)

    def draw_pine_tree(self, coordinates: tuple):
        """
        This function draws a pine tree at the specified location.
        """
        x, y = coordinates
        # Draw the triangle on top of the trunk
        arcade.draw_triangle_filled(
            x + 40, y, x, y - 100, x + 80, y - 100, arcade.color.DARK_GREEN
        )

        # Draw the trunk
        arcade.draw_lrtb_rectangle_filled(
            x + 30, x + 50, y - 100, y - 140, arcade.color.DARK_BROWN
        )

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        # Your drawing code goes here
        self.draw_background()
        self.draw_pine_tree(self.get_coordinates("pine_tree_1"))
        self.draw_pine_tree(self.get_coordinates("pine_tree_2"))
        self.draw_bird(self.get_coordinates("bird_1"))
        self.draw_bird(self.get_coordinates("bird_2"))

    def on_update(self, delta_time: float):
        """ All the logic to move, and the game logic goes here. ~60x/s """
        """delta_time: Time interval since the last time the function was called."""
        # self.pine_tree_1_x += 1
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle events when a key is pressed, such as giving a player a speed."""
        if symbol == arcade.key.RIGHT:
            self.get_current_coordinates()[COORDINATE_X] += self.rate
        elif symbol == arcade.key.LEFT:
            self.get_current_coordinates()[COORDINATE_X] -= self.rate
        elif symbol == arcade.key.UP:
            self.get_current_coordinates()[COORDINATE_Y] += self.rate
        elif symbol == arcade.key.DOWN:
            self.get_current_coordinates()[COORDINATE_Y] -= self.rate
        elif symbol == arcade.key.TAB:
            self.current_object += 1
            if self.current_object >= len(self.objects):
                self.current_object = 0
        elif symbol == arcade.key.ESCAPE:
            arcade.close_window()
        print(self.objects[self.current_object])

#    def on_resize(self, width: float, height: float):
#        """Override this function to add custom code to be called any time the window
#        is resized."""
#        self.on_resize(width, height)


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
