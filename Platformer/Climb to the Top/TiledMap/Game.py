"""
Platformer Template
"""
import arcade

BLUE_KEY = 36
GREEN_KEY = 37
RED_KEY = 38
YELLOW_KEY = 39
BLUE_LOCK = 96
GREEN_LOCK = 97
RED_LOCK = 98
YELLOW_LOCK = 99

KEY_LOCKS = [{"layer": "YellowKeyLock", "key": YELLOW_KEY, "lock": YELLOW_LOCK},
             {"layer": "BlueKeyLock", "key": BLUE_KEY, "lock": BLUE_LOCK},
             {"layer": "GreenKeyLock", "key": GREEN_KEY, "lock": GREEN_LOCK},
             {"layer": "RedKeyLock", "key": RED_KEY, "lock": RED_LOCK}]

# --- Constants
SCREEN_TITLE = "Platformer"

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.36
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 4

GRAVITY = 0.7
PLAYER_JUMP_SPEED = 11
PLAYER_START_X = 85
PLAYER_START_Y = 128
GAME_OVER_TIMER = 100


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT,
                         SCREEN_TITLE, resizable=True)

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera_sprites = None

        # A non-scrolling camera that can be used to draw GUI elements
        self.camera_gui = None

        # Keep track of the score
        self.score = 0
        self.keys = []
        self.locks = []

        # What key is pressed down?
        self.left_key_down = False
        self.right_key_down = False

        self.game_over = 0

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        self.game_over = 0
        # arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        # Set up the Cameras
        self.camera_sprites = arcade.Camera(self.width, self.height)
        self.camera_gui = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = "./level1.tmx"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Keep track of the score
        self.score = 0
        self.keys = []
        self.locks = []

        # Set up the player, specifically placing it at these coordinates.
        src = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(src, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.scene.add_sprite("Player", self.player_sprite)

        # --- Other stuff
        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera_sprites.use()

        # Draw our Scene
        # Note, if you a want pixelated look, add pixelated=True to the parameters
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.camera_gui.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text,
                         start_x=10,
                         start_y=10,
                         color=arcade.csscolor.WHITE,
                         font_size=18)

        if self.game_over:
            arcade.draw_text("OOPS!", 500, 300,
                             arcade.color.YELLOW, 50, align="left", anchor_x="center",
                             anchor_y="center", rotation=8)

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0

        if self.left_key_down and not self.right_key_down:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        # Jump
        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        # Left
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.update_player_speed()

        # Right
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.update_player_speed()

        elif key == arcade.key.ESCAPE:
            self.close()

        elif key == arcade.key.ENTER:
            self.setup()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
            self.update_player_speed()

    def center_camera_to_player(self):
        # Find where player is, then calculate lower left corner from that
        screen_center_x = self.player_sprite.center_x - (self.camera_sprites.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera_sprites.viewport_height / 2)

        # Set some limits on how far we scroll
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        # Here's our center, move to it
        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""

        if self.game_over:
            self.game_over = self.game_over - 1
            if self.game_over <= 0:
                self.setup()
            return

        # Move the player with the physics engine
        self.physics_engine.update()

        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Add one to the score
            self.score += 1

        for key_lock in KEY_LOCKS:
            self.process_keys_and_locks(key_lock)

        if self.player_sprite.center_y + (SPRITE_PIXEL_SIZE / 2) <= 0:
            self.game_over = GAME_OVER_TIMER

        # Position the camera
        self.center_camera_to_player()

    def process_keys_and_locks(self, key_lock):
        # See if we hit a yellow key or lock
        hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[key_lock["layer"]]
        )
        # Loop through each key or lock we hit (if any) and remove it (if appropriate)
        for hit in hit_list:
            if hit.properties["tile_id"] == key_lock["key"]:
                self.keys.append(key_lock["layer"])
                hit.remove_from_sprite_lists()
            elif hit.properties["tile_id"] == key_lock["lock"]:
                if key_lock["layer"] in self.keys:
                    self.locks.append(key_lock["layer"])
                    hit.remove_from_sprite_lists()

    def on_resize(self, width, height):
        new_width = width if width <= SCREEN_WIDTH else SCREEN_WIDTH
        new_height = height if height <= SCREEN_HEIGHT else SCREEN_HEIGHT

        """ Resize window """
        self.camera_sprites.resize(int(new_width), int(new_height))
        self.camera_gui.resize(int(new_width), int(new_height))


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
