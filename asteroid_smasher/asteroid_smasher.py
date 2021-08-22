"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroid_smasher

TODO:
[X] Make asteroids crash
[X] Keyboard shortcuts on screen
[X] If player wins the level, tell them they've won
[ ] (M) Show a grey bar for the lazer while you can't shoot - when it's full, it goes blue and you can shoot
[ ] (M) When you shoot, blue lazar bar reduces, when you're not shooting it increases - if you run out, lazer overheats, have to wait for grey bar again
[ ] (M) Make at least some of the asteroids change direction towards you
[ ] (S) When you've lost, don't show the spaceship
[ ] (S) Ask "Do you want to restart?" when Enter is pressed
[ ] (S) Prevent mouse from creating too many asteroids
[ ] (S) Prevent mouse from creating asteroids too close to player
[ ] (S) Bullets can wrap around, but only once
[ ] (S) Our own bullets can kill us!
[ ] (S) When you've won, the spaceship flies off the screen
[ ] (S) Bullets can wrap a random number of times
[ ] (S) Randomly (not too often) a new asteroid can appear (but only if game is not over)
[ ] (L) Tell the player if they get a score on the leaderboard (they can enter a name when they get on)
[ ] (M) 2 players can play at the same time
[ ] (S) Can't add asteroids after you've won
[ ] (L) Make a home screen (leaderboard, play, level selection)
[ ] (L) Make different prize levels
[ ] (M) Prizes can give different spaceships
[ ] (L) Add settings (silent mode, turn on/off features, adjust limits)
[ ] (S) Make shortcuts right-aligned (automatically fit on the screen)
[ ] (M) Split into different files
[ ] (M) Add instructions
"""
import random
import math
import arcade
import os

from typing import cast

STARTING_LIVES = 4
STARTING_ASTEROID_COUNT = 1
SCALE = 0.5
OFFSCREEN_SPACE = 0
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Asteroid Smasher"
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE
SPACESHIPS = ["playerShip1_orange","playerShip2_orange","playerShip3_orange","playerShip1_green"]
NOT_SPLITTING = 0
SPLITTING = 50


class TurningSprite(arcade.Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def update(self):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


class ShipSprite(arcade.Sprite):
    """
    Sprite that represents our space ship.

    Derives from arcade.Sprite.
    """
    def __init__(self, filename, scale):
        """ Set up the space ship. """

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 4
        self.drag = 0.05
        self.respawning = 0
        self.game_over = False

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        # If we are in the middle of respawning, this is non-zero.
        self.respawning = 1
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.angle = 0

    def update(self):
        """
        Update our position and other particulars.
        """
        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 250:
                self.respawning = 0
                self.alpha = 255
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        self.change_y = math.cos(math.radians(self.angle)) * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y

        # If the ship goes off-screen, move it to the other side of the window
        if self.right < 0:
            self.left = SCREEN_WIDTH

        if self.left > SCREEN_WIDTH:
            self.right = 0

        if self.bottom < 0:
            self.top = SCREEN_HEIGHT

        if self.top > SCREEN_HEIGHT:
            self.bottom = 0

        """ Call the parent class. """
        super().update()

    def draw(self):
        if not self.game_over:
            super().draw()

class AsteroidSprite(arcade.Sprite):
    """ Sprite that represents an asteroid. """

    def __init__(self, image_file_name, scale):
        super().__init__(image_file_name, scale=scale)
        self.size = 0
        self.splitting = SPLITTING

    def update(self):
        """ Move the asteroid around. """
        if self.splitting > NOT_SPLITTING:
            self.splitting -= 1

        super().update()
        if self.center_x < LEFT_LIMIT:
            self.center_x = RIGHT_LIMIT
        if self.center_x > RIGHT_LIMIT:
            self.center_x = LEFT_LIMIT
        if self.center_y > TOP_LIMIT:
            self.center_y = BOTTOM_LIMIT
        if self.center_y < BOTTOM_LIMIT:
            self.center_y = TOP_LIMIT


class BulletSprite(TurningSprite):
    """
    Class that represents a bullet.

    Derives from arcade.TurningSprite which is just a Sprite
    that aligns to its direction.
    """

    def update(self):
        super().update()
        if self.center_x < -100 or self.center_x > 1500 or \
                self.center_y > 1100 or self.center_y < -100:
            self.remove_from_sprite_lists()


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.frame_count = 0

        self.game_over = False

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = None
        self.lives = STARTING_LIVES

        # Sounds
        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")

        self.meteor_image_list = (":resources:images/space_shooter/meteorGrey_big1.png",
                                ":resources:images/space_shooter/meteorGrey_big2.png",
                                ":resources:images/space_shooter/meteorGrey_big3.png",
                                ":resources:images/space_shooter/meteorGrey_big4.png")

        self.set_mouse_visible(True)


    def create_asteroid(self, center_x = None, center_y = None):
        image_no = random.randrange(4)
        enemy_sprite = AsteroidSprite(self.meteor_image_list[image_no], SCALE)
        enemy_sprite.guid = "Asteroid"

        enemy_sprite.center_x = center_x or random.randrange(LEFT_LIMIT, RIGHT_LIMIT)
        enemy_sprite.center_y = center_y or random.randrange(BOTTOM_LIMIT, TOP_LIMIT)

        enemy_sprite.change_x = random.random() * 2 - 1
        enemy_sprite.change_y = random.random() * 2 - 1

        enemy_sprite.change_angle = (random.random() - 0.5) * 2
        enemy_sprite.size = 4
        self.all_sprites_list.append(enemy_sprite)
        self.asteroid_list.append(enemy_sprite)

    def start_new_game(self):
        """ Set up the game and initialize the variables. """

        self.frame_count = 0
        self.game_over = False
        self.paused = False

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.current_ship = 0
        self.player_sprite = ShipSprite(f":resources:images/space_shooter/{SPACESHIPS[self.current_ship]}.png"
                                        , SCALE)
        self.all_sprites_list.append(self.player_sprite)
        self.lives = STARTING_LIVES

        # Set up the little icons that represent the player lives.
        cur_pos = 10
        for i in range(self.lives):
            life = arcade.Sprite(":resources:images/space_shooter/playerLife1_orange.png", SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.all_sprites_list.append(life)
            self.ship_life_list.append(life)

        # Make the asteroids
        for i in range(STARTING_ASTEROID_COUNT):
            self.create_asteroid()

    def number_of_asteroids(self):
        return len(self.asteroid_list)

    def on_draw(self):
        """
        Render (draw) the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.all_sprites_list.draw()

        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 70, arcade.color.WHITE, 13)

        output = f"Asteroid Count: {self.number_of_asteroids()}"
        arcade.draw_text(output, 10, 50, arcade.color.WHITE, 13)

        arcade.draw_text(
            "Keys: Esc=Exit, Enter=New Game, Pause=Pause/Unpause, Space=Shoot, Left/Right=Turn, Up/Down=Move, MouseClick=New Asteroid",
            400, 5, arcade.color.AERO_BLUE, 13)

        if self.game_won:
            arcade.draw_text("YOU WON!", self.width / 2, self.height / 2,
                            arcade.color.YELLOW, 50, align="center", anchor_x="center",
                            anchor_y="center", rotation=8)
            return

        if self.game_over:
            arcade.draw_text("GAME OVER!", self.width / 2, self.height / 2,
                            arcade.color.YELLOW, 50, align="center", anchor_x="center",
                            anchor_y="center", rotation=8)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.paused:
            self.create_asteroid(x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called whenever a key is pressed. """
        
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        if symbol == arcade.key.ENTER:
            self.start_new_game()
        if symbol == arcade.key.PAUSE:
            self.paused = False if self.paused else True

        if not self.game_over and not self.paused:
            # Shoot if the player hit the space bar and we aren't respawning.
            if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
                bullet_sprite = BulletSprite(":resources:images/space_shooter/laserBlue01.png", SCALE)
                bullet_sprite.guid = "Bullet"

                bullet_speed = 13
                bullet_sprite.change_y = \
                    math.cos(math.radians(self.player_sprite.angle)) * bullet_speed
                bullet_sprite.change_x = \
                    -math.sin(math.radians(self.player_sprite.angle)) \
                    * bullet_speed

                bullet_sprite.center_x = self.player_sprite.center_x
                bullet_sprite.center_y = self.player_sprite.center_y
                bullet_sprite.update()

                self.all_sprites_list.append(bullet_sprite)
                self.bullet_list.append(bullet_sprite)

                arcade.play_sound(self.laser_sound)

            if symbol == arcade.key.LEFT:
                self.player_sprite.change_angle = 3
            elif symbol == arcade.key.RIGHT:
                self.player_sprite.change_angle = -3
            elif symbol == arcade.key.UP:
                self.player_sprite.thrust = 0.15
            elif symbol == arcade.key.DOWN:
                self.player_sprite.thrust = -.2

    def on_key_release(self, symbol, modifiers):
        """ Called whenever a key is released. """
        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = 0

    def split_asteroid(self, asteroid: AsteroidSprite):
        """ Split an asteroid into chunks. """
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1

        if asteroid.size == 4:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = [":resources:images/space_shooter/meteorGrey_med1.png",
                              ":resources:images/space_shooter/meteorGrey_med2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 3

                enemy_sprite.splitting = SPLITTING

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)
                self.hit_sound1.play()

        elif asteroid.size == 3:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = [":resources:images/space_shooter/meteorGrey_small1.png",
                              ":resources:images/space_shooter/meteorGrey_small2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 2

                enemy_sprite.splitting = SPLITTING

                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)
                self.hit_sound2.play()

        elif asteroid.size == 2:
            for i in range(3):
                image_no = random.randrange(2)
                image_list = [":resources:images/space_shooter/meteorGrey_tiny1.png",
                              ":resources:images/space_shooter/meteorGrey_tiny2.png"]

                enemy_sprite = AsteroidSprite(image_list[image_no],
                                              SCALE * 1.5)

                enemy_sprite.center_y = y
                enemy_sprite.center_x = x

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                enemy_sprite.splitting = SPLITTING
                
                self.all_sprites_list.append(enemy_sprite)
                self.asteroid_list.append(enemy_sprite)
                self.hit_sound3.play()

        elif asteroid.size == 1:
            self.hit_sound4.play()

    def process_bullets_colliding_with_asteroids(self):
        for bullet in self.bullet_list:
                asteroids_plain = arcade.check_for_collision_with_list(bullet, self.asteroid_list)
                asteroids_spatial = arcade.check_for_collision_with_list(bullet, self.asteroid_list)
                if len(asteroids_plain) != len(asteroids_spatial):
                    print("ERROR")

                asteroids = asteroids_spatial

                for asteroid in asteroids:
                    self.split_asteroid(cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
                    asteroid.remove_from_sprite_lists()
                    bullet.remove_from_sprite_lists()
    
    def process_asteroids_colliding_with_asteroids(self):
        asteroids_to_split : AsteroidSprite = []
        for asteroid in self.asteroid_list:
            collided = False
            asteroids_colliding = arcade.check_for_collision_with_list(asteroid, self.asteroid_list)
            
            for collision in asteroids_colliding:
                if collision != asteroid and collision.splitting == NOT_SPLITTING and asteroid.splitting == NOT_SPLITTING:
                    asteroids_to_split.append(collision)
                    asteroids_to_split.append(asteroid)
                    collided = True
                    break
            
            if collided:
                break
        
        for asteroid in asteroids_to_split:
            self.split_asteroid(cast(AsteroidSprite, asteroid))  # expected AsteroidSprite, got Sprite instead
            asteroid.remove_from_sprite_lists()
    
    def on_update(self, x):
        """ Move everything """

        if self.paused:
            return
        
        self.frame_count += 1

        self.all_sprites_list.update() 

        self.process_bullets_colliding_with_asteroids()
        self.process_asteroids_colliding_with_asteroids()

        if self.game_over:
            return

        if self.player_sprite.respawning:
            return
 
        if self.number_of_asteroids() == 0:
            self.game_won = True
            self.game_over = True
            self.player_sprite.game_over = True
            print("You won!")
            return
        
        asteroids = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)

        if len(asteroids) == 0:
            return

        if self.lives > 0:
            self.lives -= 1
            self.current_ship += 1
            self.player_sprite.respawn()
            self.split_asteroid(cast(AsteroidSprite, asteroids[0]))
            asteroids[0].remove_from_sprite_lists()
            self.ship_life_list.pop().remove_from_sprite_lists()
            print("Crash")
        else:
            self.game_over = True
            self.player_sprite.game_over = True
            print("Game over")
                    


def main():
    window = MyGame()
    window.start_new_game()
    arcade.run()


if __name__ == "__main__":
    main()
