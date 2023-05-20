"""
Catch the Bat
"""
from typing import Optional
import os
import arcade
from arcade import SpriteList


# Dynamic Layers
LAYER_NAME_PLAYER = "Player"

# Static Layers
LAYER_NAME_BUTTONS = "Buttons"
LAYER_NAME_SPRINGS = "Springs"
LAYER_NAME_LOCKED_DOORS = "LockedDoors"
LAYER_NAME_DOOR_PAIR = "DoorPair"
LAYER_NAME_EXITS = "Exits"
LAYER_NAME_SHORT_GREEN_WORMS = "ShortGreenWorms"
LAYER_NAME_TALL_GREEN_WORMS = "TallGreenWorms"
LAYER_NAME_MOVING_PLATFORMS = "MovingPlatforms"
LAYER_NAME_MOVING_ANVILS = "MovingAnvils"
LAYER_NAME_MOVING_CHAINS = "MovingChains"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_EMERALDS = "Emeralds"
LAYER_NAME_ROCKS = "Rocks"
LAYER_NAME_CHAINS = "Chains"
LAYER_NAME_SPIKES = "Spikes"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_LAVA = "Lava"

CHEATS = {'startLevel': 1,
          'restart': 'level',
          'keyLocks': False,
          'emeralds': False,
          'startX': 0,
          'startY': 0,
          }

LAST_LEVEL_NUMBER = 1

UNLOCK_DISTANCE = 41

BLUE_KEY = 36
GREEN_KEY = 37
RED_KEY = 38
YELLOW_KEY = 39
BLUE_LOCK = 96
GREEN_LOCK = 97
RED_LOCK = 98
YELLOW_LOCK = 99
DOOR_BOTTOM_SECTION = 60

KEY_LOCK_COLOURS = ["Red"]

# --- Constants
SCREEN_TITLE = "Catch the Bat"

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
GRAVITY = 0.4
PLAYER_JUMP_SPEED = 9
LAVA_RATIO = 0.2
SPRING_RATIO = [1.7, 2.2]
PLAYER_START_X = [85, 50]
PLAYER_START_Y = [128, 58]
GAME_OVER_TIMER = 70
LEVEL_WON_TIMER = 50

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = ":resources:images/animated_characters/male_person/malePerson"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load textures for climbing
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            # Players current texture is 0..8, but climbing textures are 0..1
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT,
                         SCREEN_TITLE, resizable=True)

        # Set the path to start with this program
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Our TileMap Object
        self.tile_map = None
        self.end_of_map = 0

        # Our Scene Object
        self.scene: Optional[arcade.Scene] = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A non-scrolling camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.score = 0
        self.emeralds_to_collect = 0
        self.keys_collected = []
        self.locks_unlocked = []

        self.game_over_countdown = 0
        self.level_won_countdown = 0
        self.level = 0

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over_sound = arcade.load_sound(":resources:sounds/gameover1.wav")

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
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        map_name = f"./TiledMap/Levels/level{level:02d}.tmx"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_BUTTONS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_SPRINGS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_LOCKED_DOORS: {
                "use_spatial_hash": True,
            },
            # Only optimising using spatial hash for first 2 door pairs
            f"{LAYER_NAME_DOOR_PAIR}1": {
                "use_spatial_hash": True,
            },
            f"{LAYER_NAME_DOOR_PAIR}2": {
                "use_spatial_hash": True,
            },
            LAYER_NAME_EXITS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_SHORT_GREEN_WORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_TALL_GREEN_WORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_EMERALDS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_CHAINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_SPIKES: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MOVING_PLATFORMS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_MOVING_ANVILS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_MOVING_CHAINS: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_LAVA: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
        }

        # Load in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        emeralds_layer: SpriteList = self.get_layer(LAYER_NAME_EMERALDS)
        if emeralds_layer and not CHEATS.get('emeralds'):
            self.emeralds_to_collect = len(emeralds_layer.sprite_list)
            print(f'{self.emeralds_to_collect} emeralds to collect')

        # Keep track of the score
        self.score = 0
        self.keys_collected = []
        self.locks_unlocked = []

        if CHEATS.get('emeralds'):
            self.emeralds_to_collect = CHEATS.get('emeralds')

        if CHEATS.get('keyLocks'):
            self.keys_collected = [key_lock for key_lock in KEY_LOCK_COLOURS]
            self.locks_unlocked = [key_lock for key_lock in KEY_LOCK_COLOURS]

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = CHEATS.get('startX') if CHEATS.get('startX') else PLAYER_START_X[level - 1]
        self.player_sprite.center_y = CHEATS.get('startY') if CHEATS.get('startY') else PLAYER_START_Y[level - 1]
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # --- Other stuff
        # Set the background color
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the 'physics engine'
        barrier_sprites: SpriteList = self.get_layer(LAYER_NAME_PLATFORMS)

        locked_doors = self.get_layer(LAYER_NAME_LOCKED_DOORS)
        if locked_doors:
            barrier_sprites.extend(locked_doors)

        rocks = self.get_layer(LAYER_NAME_ROCKS)
        if rocks:
            barrier_sprites.extend(rocks)

        tall_green_worms = self.get_layer(LAYER_NAME_TALL_GREEN_WORMS)
        if tall_green_worms:
            barrier_sprites.extend(tall_green_worms)

        short_green_worms = self.get_layer(LAYER_NAME_SHORT_GREEN_WORMS)
        if short_green_worms:
            barrier_sprites.extend(short_green_worms)
        for colour in KEY_LOCK_COLOURS:
            locks = self.get_layer(f"{colour}Lock")
            if locks:
                barrier_sprites.extend(locks)

        moving_platforms: SpriteList = self.get_layer(LAYER_NAME_MOVING_PLATFORMS)
        if not moving_platforms:
            moving_platforms = SpriteList()
        moving_anvils = self.get_layer(LAYER_NAME_MOVING_ANVILS)
        if moving_anvils:
            moving_platforms.extend(moving_anvils)
        moving_chains = self.get_layer(LAYER_NAME_MOVING_CHAINS)
        if moving_chains:
            moving_platforms.extend(moving_chains)

        ladder_sprites: SpriteList = self.get_layer(LAYER_NAME_CHAINS)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            platforms=moving_platforms,
            gravity_constant=GRAVITY,
            ladders=ladder_sprites,
            walls=barrier_sprites
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
        self.gui_camera.use()

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

    def process_key_change(self):
        """
        Called when we change a key up/down, or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                    self.physics_engine.can_jump(y_distance=10)
                    and not self.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        match key:
            case arcade.key.UP | arcade.key.W | arcade.key.SPACE:
                self.up_pressed = True
            case arcade.key.DOWN | arcade.key.S:
                self.down_pressed = True
            case arcade.key.LEFT | arcade.key.A:
                self.left_pressed = True
            case arcade.key.RIGHT | arcade.key.D:
                self.right_pressed = True
            case arcade.key.ESCAPE:
                self.close()
            case arcade.key.ENTER:
                self.process_doors_on_enter()
            case arcade.key.BACKSPACE:
                self.setup(self.level if CHEATS.get('restart') == 'level' else 1)
        self.process_key_change()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        match key:
            case arcade.key.LEFT | arcade.key.A:
                self.left_pressed = False
            case arcade.key.RIGHT | arcade.key.D:
                self.right_pressed = False
            case arcade.key.UP | arcade.key.W | arcade.key.SPACE:
                self.up_pressed = False
                self.jump_needs_reset = False
            case arcade.key.DOWN | arcade.key.S:
                self.down_pressed = False
        self.process_key_change()

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
                if self.level == LAST_LEVEL_NUMBER:
                    self.close()
                self.level = self.level + 1
                self.setup(self.level)
            return

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_key_change()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_key_change()

        # Update Animations
        self.scene.update_animation(
            delta_time, [LAYER_NAME_PLAYER]
        )

        self.process_emeralds_and_rocks()
        self.process_coins()

        for key_lock in KEY_LOCK_COLOURS:
            self.process_keys_and_locks(key_lock)

        self.process_lava()
        self.process_springs()
        self.process_spikes()
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
            arcade.play_sound(self.collect_coin_sound)

            # Add to the score
            match hit.properties['tile_id']:
                case 16:  # bronze
                    self.score += 1
                case 18:  # silver
                    self.score += 2
                case 17:  # gold
                    self.score += 3

    def process_emeralds_and_rocks(self):
        emeralds_layer: SpriteList = self.get_layer(LAYER_NAME_EMERALDS)
        if not emeralds_layer:
            return

        # See if we hit an emerald
        emerald_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, emeralds_layer
        )
        if not emerald_hit_list:
            return

        # Loop through each emerald we hit (if any)
        for emerald in emerald_hit_list:
            # Pick up the emerald
            self.emeralds_to_collect = self.emeralds_to_collect - 1
            emerald.remove_from_sprite_lists()
            if self.emeralds_to_collect == 0:
                rocks_list = self.get_layer(LAYER_NAME_ROCKS)
                # Remove the rocks
                for rock in rocks_list:
                    rock.remove_from_sprite_lists()
        print(f'{self.emeralds_to_collect} emeralds to collect')

    def process_keys_and_locks(self, colour):
        # See if we hit the key
        keys = self.get_layer(f"{colour}Key")
        if keys:
            key_hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, keys
            )
            # Loop through each key or lock we hit (if any)
            for key in key_hit_list:
                # Pick up the key
                self.keys_collected.append(colour)
                key.remove_from_sprite_lists()

        # See if we hit the lock
        locks = self.get_layer(f"{colour}Lock")
        if not locks:
            return

        closest_lock = arcade.get_closest_sprite(
            self.player_sprite, locks
        )
        if not closest_lock:
            return

        lock, distance = closest_lock
        # If we're next to the lock, and we already have the corresponding key...
        if distance <= UNLOCK_DISTANCE and colour in self.keys_collected:
            # ...unlock it
            self.locks_unlocked.append(colour)
            lock.remove_from_sprite_lists()
            # If we've unlocked all the locks...
            if len(self.locks_unlocked) >= len(KEY_LOCK_COLOURS):
                # ... unlock all the doors
                door_sprite_list: SpriteList = self.get_layer(LAYER_NAME_LOCKED_DOORS)
                if door_sprite_list:
                    doors = [door for door in door_sprite_list.sprite_list]
                    for door in doors:
                        # Assume the Tiled map has an open door hidden in a layer behind each locked door.
                        # So all we need to do is remove the locked door to reveal the unlocked one.
                        door.remove_from_sprite_lists()

    def process_doors_on_enter(self):
        # See if we're at an exit
        exits_layer = self.get_layer(LAYER_NAME_EXITS)
        if exits_layer:
            hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, exits_layer
            )
            if len(hit_list) > 0:
                self.set_level_won()
                return

        # See if we're at a door that's in a door pair
        # Assume up to 2 door pairs
        for num in range(2):
            door_pair_layer = self.get_layer(f"{LAYER_NAME_DOOR_PAIR}{num + 1}")
            if door_pair_layer:
                hit_list = arcade.check_for_collision_with_list(
                    self.player_sprite, door_pair_layer
                )
                if len(hit_list) == 1:
                    # Crate a copy of the Door Pair Sprite List
                    doors = [door for door in door_pair_layer.sprite_list]
                    # Remove the door (from the copy) that the player has collided with
                    doors.remove(hit_list[0])
                    # This should leave only one door left (in the copy) which is the door we want to transport to
                    for door in doors:
                        # Ignore top sections of doors (we want to transport to the bottom section)
                        if door.properties['tile_id'] == DOOR_BOTTOM_SECTION:
                            # Set the player position to be the position of the bottom section of the door
                            self.player_sprite.center_x = door.center_x
                            self.player_sprite.center_y = door.center_y

    def process_lava(self):
        # See if we hit any lava
        lava_layer = self.get_layer(LAYER_NAME_LAVA)
        if lava_layer:
            hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, lava_layer
            )
            # Loop through each spring we hit (if any)
            for _ in hit_list:
                # Spring the player
                self.player_sprite.change_y = PLAYER_JUMP_SPEED * LAVA_RATIO
                self.set_game_over()

    def process_springs(self):
        # See if we hit any springs
        springs_layer = self.get_layer(LAYER_NAME_SPRINGS)
        if springs_layer:
            hit_list = arcade.check_for_collision_with_list(
                self.player_sprite, springs_layer
            )
            # Loop through each spring we hit (if any)
            for _ in hit_list:
                # Spring the player
                self.player_sprite.change_y = PLAYER_JUMP_SPEED * SPRING_RATIO[self.level - 1]

    def process_spikes(self):
        # See if we hit any spikes
        yellow_spikes_layer = self.get_layer(LAYER_NAME_SPIKES)
        if not yellow_spikes_layer:
            return

        hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, yellow_spikes_layer
        )
        if len(hit_list) > 0:
            self.set_game_over()

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
                case 9:  # yellow button
                    self.deactivate_spikes("Yellow")

    def activate_springs(self, colour):
        sprites: SpriteList = self.get_layer(f"{colour}Springs")
        for inactive_spring in sprites.sprite_list:
            # Replace the inactive spring with an active one
            inactive_spring.remove_from_sprite_lists()

            src = "TiledMap/TileSets/Tiles/platformer-art-complete-pack-0/Base pack/Items/springboardUp.png"
            active_spring = arcade.Sprite(src, TILE_SCALING)
            active_spring.center_x = inactive_spring.center_x
            active_spring.center_y = inactive_spring.center_y
            self.scene[LAYER_NAME_SPRINGS].append(active_spring)

    def deactivate_spikes(self, colour):
        sprites: SpriteList = self.get_layer(f"{colour}Spikes")
        if sprites:
            spikes = [spike for spike in sprites.sprite_list]
            for spike in spikes:
                # Remove the spike
                spike.remove_from_sprite_lists()

    def on_resize(self, width, height):
        """ Resize window """
        super().on_resize(width, height)
        self.camera.resize(int(width), int(height))
        self.gui_camera.resize(int(width), int(height))


def main():
    """Main function"""
    window = MyGame()
    window.setup(CHEATS.get('startLevel') if CHEATS.get('startLevel') else 1)
    arcade.run()


if __name__ == "__main__":
    main()
