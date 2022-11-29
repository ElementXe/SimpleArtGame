import pygame as pg
import math
import random as rand

pg.init()

FPS = 120
SCREEN_WIDTH = pg.display.Info().current_w
SCREEN_HEIGHT = pg.display.Info().current_h

SKY = (95, 204, 250)
GREY = (28, 43, 28)
RED = (184, 59, 28)

GRAVITATION = 0.9
GROUND_HEIGHT = 250


class ControlButtons:
    """
    Simple class for re-assigning input keys
    """

    def __init__(self, buttons):
        """
        Initializing of ControlButtons
        :param buttons: list[int, int] - [button to move right, button to move left]
        """
        self.to_right = buttons[0]
        self.to_left = buttons[1]


class Particle:
    """
    Temporary image of effect that fade quickly
    """

    def __init__(self, surface, size, coordinates, texture):
        """
        Initializing a Particle
        :param surface: Pygame Surface object - target surface
        :param size: list[float, float] - [size on the x, size on the y]
        :param coordinates: list[float, float] - [x coordinate of center, y coordinates of center]
        :param texture: string - name of .png file
        """
        self.surface = surface
        self.size = size
        self.coordinates = coordinates
        self.texture = pg.transform.scale(pg.image.load(texture), (self.size[0], self.size[1]))
        self.lifetime = FPS * 1
        self.age = 0

    def draw(self):
        """
        Drawing a Particle
        """
        rect_draw_box = (self.coordinates[0] - self.size[0] / 2,
                         self.coordinates[1] - self.size[1] / 2,
                         self.size[0],
                         self.size[1])
        self.surface.blit(self.texture, rect_draw_box)

    def aging(self):
        """
        Addition one unit of time to the age of Particle
        """
        self.age += 1

    def get_age(self):
        """
        Request for the age
        :return: int - age of Particle
        """
        return self.age

    def get_lifetime(self):
        """
        Request for the lifetime
        :return: int - lifetime of Particle
        """
        return self.lifetime


class Ground:
    """
    Flat ground located at the bottom of the screen
    """

    def __init__(self, surface):
        """
        Initializing a Ground
        :param surface: Pygame Surface object - target surface
        """
        self.surface = surface
        self.draw_box = (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
        self.texture = pg.transform.scale(pg.image.load("textures/ground.png"), (SCREEN_WIDTH, GROUND_HEIGHT))

    def draw(self):
        """
        Drawing a Ground
        """
        self.surface.blit(self.texture, self.draw_box)


def is_in_hitbox_part(point, hitbox_part):
    """
    Check if point is in a part of hitbox
    :param point: list[float, float] - [x coordinate of point, y coordinates of point]
    :param hitbox_part: list[4 x float] - [x coordinate of center, y coordinates of center,
                                           distance to the edge on x, distance to the edge on y]
    :return: bool - is point in a part of hitbox
    """
    return abs(point[0] - hitbox_part[0]) < hitbox_part[2] and abs(point[1] - hitbox_part[1]) < hitbox_part[3]


class Projectile:
    """
    Abstract class of projectile, that can move and interact with environment
    """

    def __init__(self, surface, coordinates, velocity):
        """
        Initializing a Projectile
        :param surface: Pygame Surface object - target surface
        :param coordinates: list[float, float] - [x coordinate of center, y coordinates of center]
        :param velocity: list[float, float] - [x velocity, y velocity]
        """
        self.surface = surface
        self.rad = 0
        self.damage = 0
        self.coordinates = coordinates
        self.velocity = velocity
        self.color = "#000000"

    def draw(self):
        """
        Drawing a Projectile
        """
        pg.draw.circle(self.surface, self.color, (self.coordinates[0], self.coordinates[1]), self.rad)

    def move(self):
        """
        Moving a Projectile within a time unit
        """
        self.velocity[1] += GRAVITATION
        self.coordinates[0] += self.velocity[0]
        self.coordinates[1] += self.velocity[1]

    def is_hit_vehicle(self, veh):
        """
        Check if Projectile hit the Vehicle
        :param veh: Vehicle object - the Vehicle with which collision is checked
        :return: bool - is Vehicle hit
        """
        lu_corner = [self.coordinates[0] - self.rad, self.coordinates[1] - self.rad]
        ru_corner = [self.coordinates[0] + self.rad, self.coordinates[1] - self.rad]
        rd_corner = [self.coordinates[0] + self.rad, self.coordinates[1] + self.rad]
        ld_corner = [self.coordinates[0] - self.rad, self.coordinates[1] + self.rad]
        for hitbox_part in veh.hitbox:
            if is_in_hitbox_part(lu_corner, hitbox_part):
                return True
            if is_in_hitbox_part(ru_corner, hitbox_part):
                return True
            if is_in_hitbox_part(rd_corner, hitbox_part):
                return True
            if is_in_hitbox_part(ld_corner, hitbox_part):
                return True
        return False

    def is_hit_ground(self):
        """
        Check if Projectile hit the Ground
        :return: bool - is Ground hit
        """
        return self.coordinates[1] - self.rad > SCREEN_HEIGHT - GROUND_HEIGHT / 2

    def is_out_of_screen(self):
        """
        Check if Projectile is out of screen (on the x)
        :return: bool - is Projectile out of screen (on the x)
        """
        return self.coordinates[0] < -self.rad or self.coordinates[0] > SCREEN_WIDTH + self.rad

    def get_damage(self):
        """
        Request for the damage
        :return: int - damage of Projectile
        """
        return self.damage

    def get_type(self):
        """
        Request for the type
        """
        pass


class Shell(Projectile):
    """
    Projectile fired from a tank gun in artillery mod
    """

    def __init__(self, surface, coordinates, velocity):
        """
        Initializing a Shell
        :param surface: Pygame Surface object - target surface
        :param coordinates: list[float, float] - [x coordinate of center, y coordinates of center]
        :param velocity: list[float, float] - [x velocity, y velocity]
        """
        super().__init__(surface, coordinates, velocity)
        self.rad = 8
        self.damage = 3

    def death(self):
        """
        Processing death effects of the Shell
        :return: Particle object - image of the explosion
        """
        return Particle(self.surface,
                        (self.rad * 5, self.rad * 5),
                        (self.coordinates[0], SCREEN_HEIGHT - (GROUND_HEIGHT / 2 + 2.5 * self.rad)),
                        "textures/land_explosion.png")

    def get_type(self):
        """
        Request for the type
        :return: string - "Shell"
        """
        return "Shell"


class Shrapnel(Projectile):
    """
    Projectile fired in the amount of 5 pieces from a tank gun in shotgun mod
    """

    def __init__(self, surface, coordinates, velocity):
        """
        Initializing a Shrapnel
        :param surface: Pygame Surface object - target surface
        :param coordinates: list[float, float] - [x coordinate of center, y coordinates of center]
        :param velocity: list[float, float] - [x velocity, y velocity]
        """
        super().__init__(surface, coordinates, velocity)
        self.rad = 3
        self.damage = 1

    def get_type(self):
        """
        Request for the type
        :return: string - "Shrapnel"
        """
        return "Shrapnel"


class Bomb(Projectile):
    """
    Projectile dropped from an airship
    """

    def __init__(self, surface, coordinates, velocity):
        """
        Initializing a Bomb
        :param surface: Pygame Surface object - target surface
        :param coordinates: list[float, float] - [x coordinate of center, y coordinates of center]
        :param velocity: list[float, float] - [x velocity, y velocity]
        """
        super().__init__(surface, coordinates, velocity)
        self.rad = 10
        self.color = RED
        self.damage = 5

    def death(self):
        """
        Processing death effects of the Bomb
        :return: Particle object - image of the explosion
        """
        return Particle(self.surface,
                        (self.rad * 8, self.rad * 8),
                        (self.coordinates[0], SCREEN_HEIGHT - (GROUND_HEIGHT / 2 + 4 * self.rad)),
                        "textures/land_explosion.png")

    def get_type(self):
        """
        Request for the type
        :return: string - "Bomb"
        """
        return "Bomb"


class Vehicle:
    """
    Abstract class of vehicle, that can move, interact with environment and sometimes be controlled by player
    """

    def __init__(self, surface):
        """
        Initializing a Vehicle
        :param surface: Pygame Surface object - target surface
        """
        self.surface = surface
        self.exp_points = 0
        self.hit_points = 0
        self.size = []
        self.coordinates = []
        self.velocity = []
        self.hitbox = []
        self.texture = pg.transform.scale(pg.image.load("textures/default.png"), (10, 10))

    def update_hitbox(self):
        """
        Updating hitbox of Vehicle after one time unit
        """
        pass

    def draw(self):
        """
        Drawing a Vehicle
        """
        draw_box = (self.coordinates[0] - self.size[0] / 2,
                    self.coordinates[1] - self.size[1] / 2,
                    self.size[0],
                    self.size[1])
        self.surface.blit(self.texture, draw_box)

    def move(self):
        """
        Moving a Vehicle within a time unit
        """
        self.update_hitbox()
        self.coordinates[0] += self.velocity[0]
        self.coordinates[1] += self.velocity[1]

    def take_damage(self, damage):
        """
        Taking damage after collision with Projectile
        :param damage: int - damage of Projectile
        """
        self.hit_points -= damage

    def death(self):
        """
        Processing death effects of the Vehicle (base realization)
        :return: Particle object - image of the explosion
        :return: int - experience points from killing the Vehicle
        """
        explosion_particle = Particle(self.surface, self.size, self.coordinates, "textures/air_explosion.png")
        return explosion_particle, self.exp_points

    def is_dead(self):
        """
        Check if Vehicle's hit points below zero
        :return: bool - is Projectile dead
        """
        return self.hit_points < 0

    def get_type(self):
        """
        Request for the type
        """
        pass


class Tank(Vehicle):
    """
    Vehicle controlled by player, that can move and carries a gun
    """

    def __init__(self, surface, spawn_point, control_buttons):
        """
        Initializing a Tank
        :param surface: Pygame Surface object - target surface
        :param spawn_point: float - x coordinate of spawn point
        :param control_buttons: ControlButtons object - buttons to move left and right
        """
        super().__init__(surface)
        self.exp_points = 10
        self.hit_points = 10
        self.size = [100, 60]
        self.coordinates = [spawn_point, SCREEN_HEIGHT - (GROUND_HEIGHT / 2 + 30)]
        self.velocity = [0, 0]
        self.hitbox = [[self.coordinates[0], self.coordinates[1] + 21, self.size[0] / 2, 9],
                       [self.coordinates[0], self.coordinates[1] + 4, 36, 7],
                       [self.coordinates[0], self.coordinates[1] - 17, 25, 13]]
        self.texture = pg.transform.scale(pg.image.load("textures/tank.png"), (self.size[0], self.size[1]))
        self.control_buttons = control_buttons
        self.score = 0

    def update_hitbox(self):
        """
        Updating hitbox of Tank after one time unit
        """
        self.hitbox = [[self.coordinates[0], self.coordinates[1] + 21, self.size[0] / 2, 9],
                       [self.coordinates[0], self.coordinates[1] + 4, 36, 7],
                       [self.coordinates[0], self.coordinates[1] - 17, 25, 13]]

    def control(self, event):
        """
        Controlling of tank using assigned control buttons
        :param event: Pygame event object - any event from queue
        """
        if event.type == pg.KEYDOWN:
            if event.key == self.control_buttons.to_right:
                self.velocity[0] = 5
            if event.key == self.control_buttons.to_left:
                self.velocity[0] = -5
        if event.type == pg.KEYUP:
            if event.key == self.control_buttons.to_right or event.key == self.control_buttons.to_left:
                self.velocity[0] = 0

    def death(self):
        """
        Processing death effects of the Tank
        :return: Particle object - image of the explosion
        :return: int - experience points from killing the Vehicle
        """
        explosion_particle = Particle(self.surface,
                                      [self.size[0] * 2, self.size[1] * 4],
                                      [self.coordinates[0], self.coordinates[1] - 1.5 * self.size[1]],
                                      "textures/land_explosion.png")
        return explosion_particle, self.exp_points

    def get_type(self):
        """
        Request for the type
        :return: string - "Tank"
        """
        return "Tank"


class AirBalloon(Vehicle):
    """
    Air balloon - simple base target
    """

    def __init__(self, surface):
        """
        Initializing an AirBalloon
        :param surface: Pygame Surface object - target surface
        """
        super().__init__(surface)
        self.exp_points = 1
        self.hit_points = 1
        self.size = [90, 120]
        self.coordinates = [rand.randint(self.size[0], SCREEN_WIDTH - self.size[0]),
                            rand.randint(self.size[1], SCREEN_HEIGHT - GROUND_HEIGHT - self.size[1])]
        self.velocity = [0, 0]
        self.hitbox = [[self.coordinates[0], self.coordinates[1] + 44, 8, 16],
                       [self.coordinates[0], self.coordinates[1] + 15, 39, 13],
                       [self.coordinates[0], self.coordinates[1] - 19, self.size[0] / 2, 21],
                       [self.coordinates[0], self.coordinates[1] - 50, 38, 10]]
        self.texture = pg.transform.scale(pg.image.load("textures/air_balloon.png"), (self.size[0], self.size[1]))

    def update_hitbox(self):
        """
        Updating hitbox of AirBalloon after one time unit
        """
        self.hitbox = [[self.coordinates[0], self.coordinates[1] + 44, 8, 16],
                       [self.coordinates[0], self.coordinates[1] + 15, 39, 13],
                       [self.coordinates[0], self.coordinates[1] - 19, self.size[0] / 2, 21],
                       [self.coordinates[0], self.coordinates[1] - 50, 38, 10]]

    def get_type(self):
        """
        Request for the type
        :return: string - "AirBalloon"
        """
        return "AirBalloon"


class Airship(Vehicle):
    """
    Airship - moving target that can drop bombs
    """

    def __init__(self, surface):
        """
        Initializing an AirBalloon
        :param surface: Pygame Surface object - target surface
        """
        super().__init__(surface)
        self.exp_points = 3
        self.hit_points = 4
        self.size = [300, 160]
        self.direction = rand.randint(0, 1)
        if self.direction == 0:
            self.coordinates = [SCREEN_WIDTH * self.direction - self.size[0],
                                rand.randint(self.size[1], SCREEN_HEIGHT - GROUND_HEIGHT - self.size[1])]
            self.velocity = [rand.randint(1, 5), 0]
        else:
            self.coordinates = [SCREEN_WIDTH * self.direction + self.size[0],
                                rand.randint(self.size[1], SCREEN_HEIGHT - GROUND_HEIGHT - self.size[1])]
            self.velocity = [rand.randint(-5, -1), 0]
        self.hitbox = [[self.coordinates[0] - 125, self.coordinates[1] - 14, 24, 62],
                       [self.coordinates[0] - 50, self.coordinates[1], 51, 56],
                       [self.coordinates[0] + 42, self.coordinates[1], 40, self.size[1] / 2],
                       [self.coordinates[0] + 114, self.coordinates[1], 36, 10]]
        self.texture = pg.transform.flip(
            pg.transform.scale(pg.image.load("textures/airship.png"), (self.size[0], self.size[1])),
            bool(self.direction),
            False)

    def update_hitbox(self):
        """
        Updating hitbox of Airship after one time unit
        """
        self.hitbox = [[self.coordinates[0] - 125, self.coordinates[1] - 14, 24, 62],
                       [self.coordinates[0] - 50, self.coordinates[1], 51, 56],
                       [self.coordinates[0] + 42, self.coordinates[1], 40, self.size[1] / 2],
                       [self.coordinates[0] + 114, self.coordinates[1], 36, 10]]

    def drop_bomb(self):
        """
        Spawning Bomb under the Airship cockpit
        :return: Bomb object - new Bomb
        """
        return Bomb(self.surface, [self.coordinates[0] + 35, self.coordinates[1] + 91], [0, 0])

    def get_type(self):
        """
        Request for the type
        :return: string - "Airship"
        """
        return "Airship"


class Gun:
    """
    Abstract class of gun, that can shoot and move together with any vehicle
    """
    def __init__(self, surface, coordinates):
        """
        Initializing a Gun
        :param surface: Pygame Surface object - target surface
        :param coordinates: list[float, float] - [x coordinate of chamber, y coordinates of chamber]
        """
        self.width = 12
        self.length = 4
        self.surface = surface
        self.coordinates = [coordinates[0], coordinates[1] - 15]
        self.fire_power = 10
        self.fire_on = 0
        self.angle = 1
        self.color = GREY

    def move_to(self, new_coordinates):
        """
        Moving Gun together with its vehicle
        :param new_coordinates: list[float, float] - [x coordinate of chamber, y coordinates of chamber]
        """
        self.coordinates = [new_coordinates[0], new_coordinates[1]]

    def fire_start(self, event):
        """
        Switching to shooting mod
        :param event: Pygame event - any event from queue
        """
        if event.type == pg.MOUSEBUTTONDOWN:
            self.fire_on = 1

    def fire_end(self, event):
        """
        Shooting Projectile towards the cursor
        :param event: Pygame event - any event from queue
        """
        pass

    def targetting(self, event):
        """
        Aiming towards the cursor
        :param event: Pygame event - any event from queue
        """
        pi = math.pi
        if event.type == pg.MOUSEMOTION:
            if event.pos[0] - self.coordinates[0] == 0:
                self.angle = -pi / 2
            elif event.pos[1] - self.coordinates[1] > 0:
                if event.pos[0] - self.coordinates[0] > 0:
                    self.angle = 0
                else:
                    self.angle = pi
            elif event.pos[1] - self.coordinates[1] < 0 and event.pos[0] - self.coordinates[0] > 0:
                self.angle = math.atan((event.pos[1] - self.coordinates[1]) / (event.pos[0] - self.coordinates[0]))
            else:
                self.angle = math.atan((event.pos[1] - self.coordinates[1]) / (event.pos[0] - self.coordinates[0])) + pi

    def draw(self):
        """
        Drawing a Gun
        """
        x = self.coordinates[0]
        y = self.coordinates[1]
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        length = self.length
        width = self.width
        pg.draw.polygon(
            self.surface,
            self.color,
            ((x - width / 2 * sin, y + width / 2 * cos),
             (x + length * 10 * cos - width / 2 * sin, y + length * 10 * sin + width / 2 * cos),
             (x + length * 10 * cos + width / 2 * sin, y + length * 10 * sin - width / 2 * cos),
             (x + width / 2 * sin, y - width / 2 * cos))
        )

    def power_up(self):
        """
        Increase in the strength of the shot power after a time unit
        """
        if self.fire_on and self.fire_power < 50:
            self.fire_power += 1

    def get_type(self):
        """
        Request for the type
        """
        pass


class Artillery(Gun):
    """
    Gun that can fire one large projectile (Shell) at a time
    """
    def fire_end(self, event):
        """
        Projectile shot towards the cursor
        :param event: Pygame event - any event from queue
        :return: list[Projectiles object] - new projectiles created by shot
        """
        x = self.coordinates[0]
        y = self.coordinates[1]
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        length = self.length
        speed = self.fire_power
        if event.type == pg.MOUSEBUTTONUP:
            start_coordinates = [x + length * 10 * cos, y + length * 10 * sin]
            new_projectiles = [Shell(self.surface, start_coordinates, [speed * cos, speed * sin])]
            self.fire_on = 0
            self.fire_power = 10
            return new_projectiles

    # noinspection DuplicatedCode
    def draw(self):
        """
        Drawing artillery gun with narrow-angle aim
        """
        x = self.coordinates[0]
        y = self.coordinates[1]
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        length = self.length
        width = self.width
        speed = self.fire_power
        trans_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        pg.draw.polygon(
            trans_surface,
            RED + (120,),
            ((x - width / 2 * sin, y + width / 2 * cos),
             (x + length * speed * cos - width / 2 * sin, y + length * speed * sin + width / 2 * cos),
             (x + length * speed * cos + width / 2 * sin, y + length * speed * sin - width / 2 * cos),
             (x + width / 2 * sin, y - width / 2 * cos))
        )
        self.surface.blit(trans_surface, (0, 0))
        super().draw()

    def get_type(self):
        """
        Request for the type
        :return: string - "Artillery"
        """
        return "Artillery"


class Shotgun(Gun):
    """
    Gun that can fire five small projectiles (Shrapnel) at a time
    """
    def fire_end(self, event):
        """
        Projectile shot towards the cursor
        :param event: Pygame event - any event from queue
        :return: list[Projectiles object] - new projectiles created by shot
        """
        if event.type == pg.MOUSEBUTTONUP:
            s_x = self.coordinates[0] + self.length * 10 * math.cos(self.angle)
            s_y = self.coordinates[1] + self.length * 10 * math.sin(self.angle)
            speed = self.fire_power
            ang = self.angle
            pi = math.pi
            new_projectiles = [
                Shrapnel(self.surface, [s_x, s_y], [speed * math.cos(ang + pi / 12), speed * math.sin(ang + pi / 12)]),
                Shrapnel(self.surface, [s_x, s_y], [speed * math.cos(ang + pi / 24), speed * math.sin(ang + pi / 24)]),
                Shrapnel(self.surface, [s_x, s_y], [speed * math.cos(ang), speed * math.sin(ang)]),
                Shrapnel(self.surface, [s_x, s_y], [speed * math.cos(ang - pi / 24), speed * math.sin(ang - pi / 24)]),
                Shrapnel(self.surface, [s_x, s_y], [speed * math.cos(ang - pi / 12), speed * math.sin(ang - pi / 12)])
            ]
            self.fire_on = 0
            self.fire_power = 10
            return new_projectiles

    # noinspection DuplicatedCode
    def draw(self):
        """
        Drawing shotgun with wide-angle aim
        """
        x = self.coordinates[0]
        y = self.coordinates[1]
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        length = self.length
        width = self.width
        speed = self.fire_power
        trans_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        aim_width = self.width + ((self.fire_power - 10) / 40) * 70
        pg.draw.polygon(
            trans_surface,
            RED + (120,),
            ((x + length * 10 * cos - width / 2 * sin, y + length * 10 * sin + width / 2 * cos),
             (x + length * self.fire_power * cos - aim_width / 2 * sin, y + length * speed * sin + aim_width / 2 * cos),
             (x + length * self.fire_power * cos + aim_width / 2 * sin, y + length * speed * sin - aim_width / 2 * cos),
             (x + length * 10 * cos + width / 2 * sin, y + length * 10 * sin - width / 2 * cos))
        )
        self.surface.blit(trans_surface, (0, 0))
        super().draw()

    def get_type(self):
        """
        Request for the type
        :return: string - "Shotgun"
        """
        return "Shotgun"


class Gameplay:
    """
    Gameplay itself
    """
    def __init__(self, surface):
        """
        Initialising of Gameplay
        :param surface: Pygame Surface object - target surface
        """
        self.surface = surface
        self.ground = Ground(surface)
        self.tanks_list = [Tank(surface, 300, ControlButtons([100, 97])),
                           Tank(surface, 1200, ControlButtons([1073741903, 1073741904]))]
        self.tank_under_control = 0
        self.guns_list = [Artillery(surface, self.tanks_list[0].coordinates),
                          Shotgun(surface, self.tanks_list[1].coordinates)]
        self.score_list = [0, 0]
        self.targets_list = []
        self.projectiles_list = []
        self.particles_list = []
        self.clock = pg.time.Clock()
        self.finished = False

    def create_new_target(self):
        """
        Creating one new target (AirBalloon or Airship) with small chance (about once every five seconds)
        """
        if len(self.targets_list) < 4 and rand.random() < 1 / (FPS * 5):
            if rand.random() < 0.2:
                self.targets_list.append(Airship(self.surface))
            else:
                self.targets_list.append(AirBalloon(self.surface))

    def draw_objects(self):
        """
        Drawing background and every vehicle, gun, projectile and particle
        """
        self.surface.fill(SKY)
        self.ground.draw()
        for gun in self.guns_list:
            gun.draw()
        for tank in self.tanks_list:
            tank.draw()
        for target in self.targets_list:
            target.draw()
        for projectile in self.projectiles_list:
            projectile.draw()
        for particle in self.particles_list:
            particle.draw()

    def display_update(self):
        """
        Updating display to reflect changes of objects
        """
        pg.display.update()
        self.clock.tick(FPS)

    def process_input(self):
        """
        Processing all player input
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.finished = True

            elif event.type == pg.KEYDOWN:
                if event.key == 32 and self.tank_under_control == 0 and len(self.tanks_list) != 1:
                    self.tanks_list[self.tank_under_control].velocity = [0, 0]
                    self.tank_under_control = 1
                elif event.key == 32 and self.tank_under_control == 1:
                    self.tanks_list[self.tank_under_control].velocity = [0, 0]
                    self.tank_under_control = 0
                if event.key == 1073742048 and self.guns_list[self.tank_under_control].get_type() == "Artillery":
                    self.guns_list[self.tank_under_control] = Shotgun(self.surface, self.tanks_list[0].coordinates)
                elif event.key == 1073742048 and self.guns_list[self.tank_under_control].get_type() == "Shotgun":
                    self.guns_list[self.tank_under_control] = Artillery(self.surface, self.tanks_list[0].coordinates)

            self.tanks_list[self.tank_under_control].control(event)
            self.guns_list[self.tank_under_control].targetting(event)
            self.guns_list[self.tank_under_control].fire_start(event)
            new_projectiles = self.guns_list[self.tank_under_control].fire_end(event)
            if new_projectiles is not None:
                self.projectiles_list = self.projectiles_list + new_projectiles

        self.guns_list[self.tank_under_control].power_up()

    def move_object(self):
        """
        Moving every vehicle, gun and projectile according to thy movement rules
        """
        for tank in self.tanks_list:
            tank.move()
        for target in self.targets_list:
            target.move()
        for projectile in self.projectiles_list:
            projectile.move()
        self.guns_list[self.tank_under_control].move_to([self.tanks_list[self.tank_under_control].coordinates[0],
                                                         self.tanks_list[self.tank_under_control].coordinates[1] - 15])

    def ai_acts(self):
        """
        Acting of artificial intelligence of vehicles
        """
        for target in self.targets_list:
            if target.get_type() == "Airship" and rand.random() < 1 / (FPS * 5):
                self.projectiles_list.append(target.drop_bomb())

    def projectile_remove(self, projectile):
        if projectile in self.projectiles_list:
            self.projectiles_list.remove(projectile)

    def check_hit(self):
        """
        Checking if projectile hit something or out of screen and processing it
        """
        for projectile in self.projectiles_list:
            for target in self.targets_list:
                if projectile.is_hit_vehicle(target):
                    target.take_damage(projectile.get_damage())
                    self.projectile_remove(projectile)
            for tank in self.tanks_list:
                if projectile.is_hit_vehicle(tank):
                    tank.take_damage(projectile.get_damage())
                    self.projectile_remove(projectile)
            if projectile.is_hit_ground():
                if projectile.get_type() == "Shell" or projectile.get_type() == "Bomb":
                    self.particles_list.append(projectile.death())
                self.projectile_remove(projectile)
            if projectile.is_out_of_screen():
                self.projectile_remove(projectile)

    def remove_vehicle(self):
        """
        Removing dead vehicles from lists
        """
        for target in self.targets_list:
            if target.is_dead():
                new_particle, new_experience = target.death()
                self.particles_list.append(new_particle)
                self.score_list[self.tank_under_control] += new_experience
                self.targets_list.remove(target)

        for tank in self.tanks_list:
            if tank.is_dead():
                new_particle, new_experience = tank.death()
                self.particles_list.append(new_particle)
                self.score_list[self.tank_under_control] += new_experience
                self.guns_list.pop(self.tanks_list.index(tank))
                self.tanks_list.remove(tank)

    def process_particles(self):
        """
        Increase of particle age and removing particles that are too old
        """
        for particle in self.particles_list:
            particle.aging()
            if particle.get_age() > particle.get_lifetime():
                self.particles_list.remove(particle)

    def check_tanks(self):
        """
        Checking number of tanks and doing relevant changes in control mechanism
        """
        if len(self.tanks_list) == 1:
            self.tank_under_control = 0
        if len(self.tanks_list) == 0:
            self.finished = True


screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

game = Gameplay(screen)

while not game.finished:
    game.create_new_target()
    game.draw_objects()
    game.display_update()
    game.process_input()
    game.move_object()
    game.ai_acts()
    game.check_hit()
    game.remove_vehicle()
    game.process_particles()
    game.check_tanks()

pg.quit()
