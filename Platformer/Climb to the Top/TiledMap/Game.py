"""
Platformer Template
"""
from typing import Optional

import arcade
from arcade import SpriteList

SPRITE_NAME_PLAYER = "Player"

LAYER_NAME_BUTTONS = "Buttons"
LAYER_NAME_SPRINGS = "Springs"
LAYER_NAME_LOCKED_DOORS = "LockedDoors"
LAYER_NAME_EXITS = "Exits"
LAYER_NAME_SHORT_GREEN_WORMS = "ShortGreenWorms"
LAYER_NAME_TALL_GREEN_WORMS = "TallGreenWorms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_PLATFORMS = "Platforms"

CHEATS = {'startLevel': 1,
          'restart': 'level',
          'keyLocks': False,
          'startX': None,
          'startY': None,
          }

UNLOCK_DISTANCE = 41

BLUE_KEY = 36
GREEN_KEY = 37
RED_KEY = 38
YELLOW_KEY = 39
BLUE_LOCK = 96
GREEN_LOCK = 97
RED_LOCK = 98
YELLOW_LOCK = 99

KEY_LOCK_COLOURS = ["Yellow", "Blue", "Green", "Red"]

# --- Constants
SCREEN_TITLE = "Climb to the Top"

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.36
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 9
SPRING_RATIO = [1.7, 2.2]
PLAYER_START_X = [85, 50]
PLAYER_START_Y = [128, 58]
GAME_OVER_TIMER = 70
LEVEL_WON_TIMER = 50


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
        self.scene: Optional[arcade.Scene] = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A non-scrolling camera that can be used to draw GUI elements
        self.camera_gui = None

        # Keep track of the score
        self.score = 0
        self.keys = []
        self.locks = []

        # What key is pressed down?
        self.left_key_down = False
        self.right_key_down = False

        self.game_over_countdown = 0
        self.level_won_countdown = 0

        self.level = 0

    def set_game_over(self):
        self.game_over_countdown = GAME_OVER_TIMER

    def is_game_over(self):
        return self.game_over_countdown > 0

    def set_level_won(self):
        self.level_won_countdown = LEVEL_WON_TIMER

    def is_level_won(self):
        return self.level_won_countdown > 0

    def setup(self, level=1):
        """Set up the game here. Call this function to restart the game."""

        self.level = level if level else 1
        self.game_over_countdown = 0
        self.level_won_countdown = 0

        # Set up the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.camera_gui = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = f"./level{level:02d}.tmx"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
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

        if CHEATS.get('keyLocks'):
            self.keys = [key_lock for key_lock in KEY_LOCK_COLOURS]
            self.locks = [key_lock for key_lock in KEY_LOCK_COLOURS]

        # Set up the player, specifically placing it at these coordinates.
        src = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(src, CHARACTER_SCALING)
        self.player_sprite.center_x = CHEATS.get('startX') if CHEATS.get('startX') else PLAYER_START_X[level - 1]
        self.player_sprite.center_y = CHEATS.get('startY') if CHEATS.get('startY') else PLAYER_START_Y[level - 1]
        self.scene.add_sprite(SPRITE_NAME_PLAYER, self.player_sprite)

        # --- Other stuff
        # Create the 'physics engine'
        barrier_sprites: SpriteList = self.get_layer(LAYER_NAME_PLATFORMS)
        locked_doors = self.get_layer(LAYER_NAME_LOCKED_DOORS)
        if locked_doors:
            barrier_sprites.extend(locked_doors)
        tall_green_worms = self.get_layer(LAYER_NAME_TALL_GREEN_WORMS)
        if tall_green_worms:
            barrier_sprites.extend(tall_green_worms)
        short_green_worms = self.get_layer(LAYER_NAME_SHORT_GREEN_WORMS)
        if short_green_worms:
            barrier_sprites.extend(short_green_worms)
        for colour in KEY_LOCK_COLOURS:
            barrier_sprites.extend(self.get_layer(f"{colour}Lock"))
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=barrier_sprites
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate the game camera
        self.camera.use()

        # Draw our Scene
        # Note, if you want a pixelated look, add pixelated=True to the parameters
        self.scene.draw()

        # Activate the GUI camera before drawing GUI elements
        self.camera_gui.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Level: {self.level} Score: {self.score}"
        arcade.draw_text(score_text,
                         start_x=10,
                         start_y=10,
                         color=arcade.csscolor.WHITE,
                         font_size=18)

        if self.is_game_over():
            arcade.draw_text("OOPS!", 500, 300,
                             arcade.color.YELLOW, 50, align="left", anchor_x="center",
                             anchor_y="center", rotation=8)

        if self.is_level_won():
            arcade.draw_text("WHOOHOO!", 500, 300,
                             arcade.color.YELLOW, 50, align="left", anchor_x="center",
                             anchor_y="center", rotation=8)

    def get_layer(self, layer_name):
        try:
            return self.scene[layer_name]
        except KeyError:
            pass

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0

        if self.left_key_down and not self.right_key_down:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        match key:
            case arcade.key.UP | arcade.key.W | arcade.key.SPACE:
                if self.physics_engine.can_jump():
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
            case arcade.key.LEFT | arcade.key.A:
                self.left_key_down = True
                self.update_player_speed()
            case arcade.key.RIGHT | arcade.key.D:
                self.right_key_down = True
                self.update_player_speed()
            case arcade.key.ESCAPE:
                self.close()
            case arcade.key.ENTER:
                self.setup(self.level if CHEATS.get('restart') == 'level' else 1)
            case arcade.key.DOWN:
                # See if we're at an exit
                exits_layer = self.get_layer(LAYER_NAME_EXITS)
                if exits_layer:
                    hit_list = arcade.check_for_collision_with_list(
                        self.player_sprite, exits_layer
                    )
                    if len(hit_list) > 0:
                        self.set_level_won()

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
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Set some limits on how far we scroll
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        # Here's our center, move to it
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""

        if self.is_game_over():
            self.game_over_countdown = self.game_over_countdown - 1
            if self.game_over_countdown <= 0:
                self.setup(self.level if CHEATS.get('restart') == 'level' else 1)
            return

        if self.is_level_won():
            self.level_won_countdown = self.level_won_countdown - 1
            if self.level_won_countdown <= 0:
                self.level = self.level + 1
                self.setup(self.level)
            return

        # Move the player with the physics engine
        self.physics_engine.update()

        self.process_coins()

        for key_lock in KEY_LOCK_COLOURS:
            self.process_keys_and_locks(key_lock)

        self.process_springs()

        self.process_buttons()

        if self.player_sprite.center_y + (SPRITE_PIXEL_SIZE / 2) <= 0:
            self.set_game_over()

        # Position the camera
        self.center_camera_to_player()

    def process_coins(self):
        # See if we hit any coins
        coins_layer = self.get_layer(LAYER_NAME_COINS)
        if not coins_layer:
            return
        hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, coins_layer
        )
        # Loop through each coin we hit (if any) and remove it
        for hit in hit_list:
            # Remove the coin
            hit.remove_from_sprite_lists()
            # Add to the score
            match hit.properties['tile_id']:
                case 16:  # bronze
                    self.score += 1
                case 18:  # silver
                    self.score += 2
                case 17:  # gold
                    self.score += 3

    def process_keys_and_locks(self, colour):
        # See if we hit the key
        key_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.get_layer(f"{colour}Key")
        )
        # Loop through each key or lock we hit (if any)
        for key in key_hit_list:
            # Pick up the key
            self.keys.append(colour)
            key.remove_from_sprite_lists()

        # See if we hit the lock
        closest_lock = arcade.get_closest_sprite(
            self.player_sprite, self.get_layer(f"{colour}Lock")
        )
        if not closest_lock:
            return

        lock, distance = closest_lock
        # If we're next to the lock, and we already have the corresponding key...
        if distance <= UNLOCK_DISTANCE and colour in self.keys:
            # ...unlock it
            self.locks.append(colour)
            lock.remove_from_sprite_lists()
            # If we've unlocked all the locks...
            if len(self.locks) >= len(KEY_LOCK_COLOURS):
                # ... unlock all the doors
                door_sprite_list: SpriteList = self.get_layer(LAYER_NAME_LOCKED_DOORS)
                doors = [door for door in door_sprite_list.sprite_list]
                for door in doors:
                    # Assume the Tiled map has an open door hidden in a layer behind each locked door.
                    # So all we need to do is remove the locked door to reveal the unlocked one.
                    door.remove_from_sprite_lists()

    def process_springs(self):
        # See if we hit any springs
        hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.get_layer(LAYER_NAME_SPRINGS)
        )
        # Loop through each spring we hit (if any)
        for _ in hit_list:
            # Spring the player
            self.player_sprite.change_y = PLAYER_JUMP_SPEED * SPRING_RATIO[self.level-1]

    def process_buttons(self):
        # See if we hit any buttons
        buttons = self.get_layer(LAYER_NAME_BUTTONS)
        if not buttons:
            return
        hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, buttons
        )
        # Loop through each button we hit (if any)
        for hit in hit_list:
            hit.remove_from_sprite_lists()
            match hit.properties['tile_id']:
                case 5:  # green button
                    sprites: SpriteList = self.get_layer(LAYER_NAME_TALL_GREEN_WORMS)
                    for worm in sprites.sprite_list:
                        # Assume the Tiled map has a shorter green worm in a layer behind each tall green worm.
                        # So all we need to do is remove the taller green worm to reveal the shorter one.
                        worm.remove_from_sprite_lists()
                case 7:  # red button
                    self.activate_springs("Red")
                case 3:  # blue button
                    self.activate_springs("Blue")

    def activate_springs(self, colour):
        sprites: SpriteList = self.get_layer(f"{colour}Springs")
        for inactive_spring in sprites.sprite_list:
            # Replace the inactive spring with an active one
            inactive_spring.remove_from_sprite_lists()

            src = "../Assets/Items/springboardUp.png"
            active_spring = arcade.Sprite(src, TILE_SCALING)
            active_spring.center_x = inactive_spring.center_x
            active_spring.center_y = inactive_spring.center_y
            self.scene[LAYER_NAME_SPRINGS].append(active_spring)

    def on_resize(self, width, height):
        new_width = width if width <= SCREEN_WIDTH else SCREEN_WIDTH
        new_height = height if height <= SCREEN_HEIGHT else SCREEN_HEIGHT

        """ Resize window """
        self.camera.resize(int(new_width), int(new_height))
        self.camera_gui.resize(int(new_width), int(new_height))


def main():
    """Main function"""
    window = MyGame()
    window.setup(CHEATS.get('startLevel') if CHEATS.get('startLevel') else 1)
    arcade.run()


if __name__ == "__main__":
    main()
