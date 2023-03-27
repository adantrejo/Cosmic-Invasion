import pygame
from pygame.locals import *
import random
import numpy
import asyncio

# Screen setup
pygame.init()
screen_width = 600
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))


# Define fps
clock = pygame.time.Clock()
fps = 60


# load bg
bg = pygame.image.load('imgs/bg.png')

def draw_bg():
    screen.blit(bg,(0, 0))

# Game variables
pause = False
weapon_type = 1
shield = 0 # 1 = shield
level = 1
game = -1 # -1 lose, 0 running, 1 win
how_2_play = 0 # 1 = how to play screen true
alien_cooldown = 1000 # 1 sec
last_alien_shot = pygame.time.get_ticks()

# Load sounds
explosion_fx = pygame.mixer.Sound('imgs/img_explosion.wav')
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound('imgs/img_explosion2.wav')
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound('imgs/img_laser.wav')
laser_fx.set_volume(0.25)

# Text Font
font20 = pygame.font.SysFont("Constantia", 20)
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont("Constantia", 40)

#define global variable
clicked = False
counter = 0

# Define colors
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)

# Create Text
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Spaceship class + spaceship shooting + movement
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/Spaceship.png')
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = [x, y]
        self.direction = pygame.math.Vector2() # default: x = 0, y = 0
        self.speed = 8
        self.last_shot = pygame.time.get_ticks()
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def input(self):
        # Bullet cooldown
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left >= 0 or key[pygame.K_a] and self.rect.left >= 0:
            self.direction.x = -1
        elif key[pygame.K_RIGHT] and self.rect.right <= screen_width or key[pygame.K_d] and self.rect.right <= screen_width:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if key[pygame.K_UP] and self.rect.top >= 0 or key[pygame.K_w] and self.rect.top >= 0:
            self.direction.y = -1
        elif key[pygame.K_DOWN] and self.rect.bottom <= screen_height or key[pygame.K_s] and self.rect.bottom <= screen_height:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # Shoot bullets
        time_now = pygame.time.get_ticks()
        if weapon_type == 1:
            cooldown = 500
            if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
                laser_fx.play()
                bullet = Bullets1(self.rect.centerx, self.rect.top)
                bullet1_group.add(bullet)
                self.last_shot = time_now

        elif weapon_type == 2:
            cooldown = 1000
            if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
                laser_fx.play()
                bullet = Bullets2of1(self.rect.left, self.rect.top)
                bullet2of1_group.add(bullet)
                self.last_shot = time_now


                bullet = Bullets2of2(self.rect.centerx, self.rect.top)
                bullet2of2_group.add(bullet)

                bullet = Bullets2of3(self.rect.right, self.rect.top)
                bullet2of3_group.add(bullet)

    # spaceship movement speed
    def move(self, speed):
        if self.direction.magnitude() != 0: # checking if vector isn't 0
            self.direction = self.direction.normalize() # changing vector to 1 everytime it isn't 0

        self.rect.center += self.direction * speed # setting speed for all directions.

    def HealthBar(self):                #x and y coordinate                , width and height
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            global game
            game = -2

    def SpaceshipCollision(self):
        self.mask = pygame.mask.from_surface(self.image)
        if pygame.sprite.spritecollide(self, alien_group, True, pygame.sprite.collide_mask):
            self.health_remaining -= 1
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        # Update mask (Transparent background from sprite will be ignored)

    def update(self):
        self.input()
        self.move(self.speed)
        self.HealthBar()
        self.SpaceshipCollision()



# Spaceship group
spaceship_group = pygame.sprite.Group()

spaceship = Spaceship(screen_width / 2, screen_height - 80, 3)
spaceship_group.add(spaceship)





# Bullet type 1
class Bullets1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def bulletmovement(self):
        self.rect.y -= 7
        if self.rect.bottom < 0:
            self.kill()

    def bulletcolliding(self):
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

            random_chance = numpy.random.uniform(1, 100)
            #heart
            if spaceship.health_remaining < 3 and len(heartitem_group) == 0:
                if random_chance >= 11 and random_chance <= 15 and level >= 4:
                    heartitem = HeartItem(self.rect.centerx, self.rect.centery)
                    heartitem_group.add(heartitem)

            # changes of item drop
            #Weapon
            if len(alien_group) >= 5 and len(switchweaponitem_group) == 0 and weapon_type == 1:
                if random_chance >= 1 and random_chance <= 5 and level >= 3:
                    switchweaponitem = SwitchWeaponItem(self.rect.centerx, self.rect.centery)
                    switchweaponitem_group.add(switchweaponitem)

            #Shield
            if len(alien_group) >= 5 and len(shielditem_group) == 0 and shield == 0:
                if random_chance >= 17 and random_chance <= 19 and level >= 5:
                    shielditem = ShieldItem(self.rect.centerx, self.rect.centery)
                    shielditem_group.add(shielditem)

    def update(self):
        self.bulletmovement()
        self.bulletcolliding()


bullet1_group = pygame.sprite.Group()




# Bullet type 2
class Bullets2of1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def bulletcolliding(self):
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

            random_chance = numpy.random.uniform(1, 100)

            # Heart
            if spaceship.health_remaining < 3 and len(heartitem_group) == 0:
                if random_chance >= 11 and random_chance <= 15 and level >= 4:
                    heartitem = HeartItem(self.rect.centerx, self.rect.centery)
                    heartitem_group.add(heartitem)

            # Shield
            if len(alien_group) >= 5 and len(shielditem_group) == 0 and shield == 0:
                if random_chance >= 17 and random_chance <= 19 and level >= 5:
                    shielditem = ShieldItem(self.rect.centerx, self.rect.centery)
                    shielditem_group.add(shielditem)

    def update(self):
        self.rect.y -= 7
        self.rect.x -= 1
        if self.rect.bottom < 0:
            self.kill()
        self.bulletcolliding()

bullet2of1_group = pygame.sprite.Group()


class Bullets2of2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def bulletcolliding(self):
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

            random_chance = numpy.random.uniform(1, 100)

            # Heart
            if spaceship.health_remaining < 3 and len(heartitem_group) == 0:
                if random_chance >= 11 and random_chance <= 15 and level >= 4:
                    heartitem = HeartItem(self.rect.centerx, self.rect.centery)
                    heartitem_group.add(heartitem)

            # Shield
            if len(alien_group) >= 5 and len(shielditem_group) == 0 and shield == 0:
                if random_chance >= 17 and random_chance <= 19 and level >= 5:
                    shielditem = ShieldItem(self.rect.centerx, self.rect.centery)
                    shielditem_group.add(shielditem)

    def update(self):
        self.rect.y -= 7
        if self.rect.bottom < 0:
            self.kill()
        self.bulletcolliding()

bullet2of2_group = pygame.sprite.Group()


class Bullets2of3(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def bulletcolliding(self):
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

            random_chance = numpy.random.uniform(1, 100)
            # Heart
            if spaceship.health_remaining < 3 and len(heartitem_group) == 0:
                if random_chance >= 11 and random_chance <= 15 and level >= 4:
                    heartitem = HeartItem(self.rect.centerx, self.rect.centery)
                    heartitem_group.add(heartitem)

            # Shield
            if len(alien_group) >= 5 and len(shielditem_group) == 0 and shield == 0:
                if random_chance >= 17 and random_chance <= 19 and level >= 5:
                    shielditem = ShieldItem(self.rect.centerx, self.rect.centery)
                    shielditem_group.add(shielditem)
    def update(self):
        self.rect.y -= 7
        self.rect.x += 1
        if self.rect.bottom < 0:
            self.kill()
        self.bulletcolliding()

bullet2of3_group = pygame.sprite.Group()


# Switch weapon item
class SwitchWeaponItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f'imgs/WeaponItem{num}.png')
            img = pygame.transform.scale(img, (40, 40))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def ItemSpeed(self):
        self.rect.y += 3

    def ItemCollide(self):
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            self.kill()
            global weapon_type
            weapon_type = 2
        if self.rect.top >= screen_height:
            self.kill()

    def ItemAnimation(self):
        spin_speed = 10
        # update explosion animation
        self.counter += 1
        if self.counter >= spin_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.image = self.images[self.index]
            self.index += 1
        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= spin_speed:
            self.index = 0

    def update(self):
        self.ItemCollide()
        self.ItemSpeed()
        self.ItemAnimation()

switchweaponitem_group = pygame.sprite.Group()

class SwitchWeaponItemtext(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f'imgs/WeaponItem{num}.png')
            img = pygame.transform.scale(img, (40, 40))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def ItemAnimation(self):
        spin_speed = 10
        # update explosion animation
        self.counter += 1
        if self.counter >= spin_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.image = self.images[self.index]
            self.index += 1
        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= spin_speed:
            self.index = 0

    def update(self):
        self.ItemAnimation()

switchweaponitemtext_group = pygame.sprite.Group()

class HeartItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f'imgs/heart{num}.png')
            img = pygame.transform.scale(img, (40, 40))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def ItemSpeed(self):
        self.rect.y += 3

    def ItemCollide(self):
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            self.kill()
            if spaceship.health_remaining < 3:
                spaceship.health_remaining += 1
        if self.rect.top >= screen_height:
            self.kill()

    def ItemAnimation(self):
        spin_speed = 10
        # update explosion animation
        self.counter += 1
        if self.counter >= spin_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.image = self.images[self.index]
            self.index += 1
        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= spin_speed:
            self.index = 0

    def update(self):
        self.ItemCollide()
        self.ItemSpeed()
        self.ItemAnimation()

heartitem_group = pygame.sprite.Group()

#h2p screen
class HeartItemtext(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f'imgs/heart{num}.png')
            img = pygame.transform.scale(img, (50, 50))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def ItemAnimation(self):
        spin_speed = 10
        # update explosion animation
        self.counter += 1
        if self.counter >= spin_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.image = self.images[self.index]
            self.index += 1
        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= spin_speed:
            self.index = 0

    def update(self):
        self.ItemAnimation()


heartitemtext_group = pygame.sprite.Group()


class ShieldItem(pygame.sprite.Sprite):
    def __init__(self, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f'imgs/ShieldItem{num}.png')
            img = pygame.transform.scale(img, (40, 40))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


    def ItemSpeed(self):
        self.rect.y += 3

    def ItemCollide(self):
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            self.kill()
            global shield
            shield = 1
            shieldcircle = Shieldcircle(1)
            shieldcircle_group.add(shieldcircle)
        if self.rect.top >= screen_height:
            self.kill()

    def ItemAnimation(self):
        spin_speed = 10
        # update explosion animation
        self.counter += 1
        if self.counter >= spin_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.image = self.images[self.index]
            self.index += 1
        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= spin_speed:
            self.index = 0

    def update(self):
        self.ItemCollide()
        self.ItemSpeed()
        self.ItemAnimation()

shielditem_group = pygame.sprite.Group()


class ShieldItemtext(pygame.sprite.Sprite):
    def __init__(self, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 5):
            img = pygame.image.load(f'imgs/ShieldItem{num}.png')
            img = pygame.transform.scale(img, (50, 50))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


    def ItemAnimation(self):
        spin_speed = 10
        # update explosion animation
        self.counter += 1
        if self.counter >= spin_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.image = self.images[self.index]
            self.index += 1
        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= spin_speed:
            self.index = 0

    def update(self):
        self.ItemAnimation()

shielditemtext_group = pygame.sprite.Group()


class Shieldcircle(pygame.sprite.Sprite):
    def __init__(self, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/Shield.png')
        self.rect = self.image.get_rect()
        self.health = health

    def ItemCollide(self):
        global shield

        if pygame.sprite.spritecollide(self, alien_bullet_group, True):
            self.kill()
            shield = 0

        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            shield = 0


    def update(self):
        self.rect.center = spaceship.rect.center
        self.ItemCollide()



shieldcircle_group = pygame.sprite.Group()


# Aliens 1
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/Alien.png')
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.countery = 0
        # counter for side to side movement
        self.counterx = 0
        self.move_directionx = 1
        self.move_directiony = 1


    def level1(self):
        # Movement for alien 1 in level 1
        self.rect.y += 2
        if self.rect.y >= 20:
            self.rect.y = 20
            self.rect.x += self.move_directionx
            self.countery += 1

        # When alien reached 100, it stops then moves side to  side
        if abs(self.countery) > 80:
            self.move_directionx *= -1
            self.countery *= self.move_directionx

    def level2(self):
        # Movement for alien 1 in level 2
        self.rect.y += self.move_directiony * 2
        self.countery += 1
        if self.countery > 70:
            self.move_directiony = 0
            self.counterx += 1
            self.rect.x += self.move_directionx
            if abs(self.counterx) > 80:
                self.move_directionx *= -1
                #0, 1, .... 80, -81, -80, -79..... 0 (middle), .... 80 (left side),....
                self.counterx *= self.move_directionx

    def level3(self):
        # Movement for alien 1 in level 2
        self.rect.y += self.move_directiony * 2
        self.countery += 1
        if self.countery > 120:
            self.move_directiony = 0
            self.counterx += 1
            self.rect.x += self.move_directionx
            if abs(self.counterx) > 80:
                self.move_directionx *= -1
                #0, 1, .... 80, -81, -80, -79..... 0 (middle), .... 80 (left side),....
                self.counterx *= self.move_directionx


    def level4(self):
        # Movement for alien 1 in level 4
        self.rect.y += self.move_directiony * 2
        self.countery += 1
        if self.countery > 170:
            self.move_directiony = 0
            self.counterx += 1
            self.rect.x += self.move_directionx
            if abs(self.counterx) > 80:
                self.move_directionx *= -1
                #0, 1, .... 80, -81, -80, -79..... 0 (middle), .... 80 (left side),....
                self.counterx *= self.move_directionx


    def level5(self):

        # Movement for alien 1 in level 2
        self.rect.y += self.move_directiony * 2
        self.countery += 1
        if self.countery > 215:
            self.move_directiony = 0
            self.counterx += 1
            self.rect.x += self.move_directionx
            if abs(self.counterx) > 80:
                self.move_directionx *= -1
                #0, 1, .... 80, -81, -80, -79..... 0 (middle), .... 80 (left side),....
                self.counterx *= self.move_directionx

    def level6(self):

        # Movement for alien 1 in level 2
        self.rect.y += self.move_directiony * 2
        self.countery += 1
        if self.countery > 265:
            self.move_directiony = 0
            self.counterx += 1
            self.rect.x += self.move_directionx
            if abs(self.counterx) > 80:
                self.move_directionx *= -1
                #0, 1, .... 80, -81, -80, -79..... 0 (middle), .... 80 (left side),....
                self.counterx *= self.move_directionx

    def update(self):
        if level == 1:
            self.level1()
        elif level == 2:
            self.level2()
        elif level == 3:
            self.level3()
        elif level == 4:
            self.level4()
        elif level == 5:
            self.level5()
        elif level == 6:
            self.level6()


alien_group = pygame.sprite.Group()

# Level 1 alien setup
def create_aliens1():
    for num in range(5):
        alien = Aliens(100 + num * 100, -100)
        alien_group.add(alien)

# Level 2 alien setup
def create_aliens2():
    for row in range(2):
        for col in range(5):
            alien = Aliens(100 + col * 100, row * -100)
            alien_group.add(alien)

# Level 3 alien setup
def create_aliens3():
    for row in range(3):
        for col in range(5):
            alien = Aliens(100 + col * 100, row * -100)
            alien_group.add(alien)

# Level 4 alien setup
def create_aliens4():
    for row in range(4):
        for col in range(5):
            alien = Aliens(100 + col * 100, row * -100)
            alien_group.add(alien)

# Level 5 alien setup
def create_aliens5():
    for row in range(5):
        for col in range(5):
            alien = Aliens(100 + col * 100, row * -100)
            alien_group.add(alien)
# Level 6 alien setup
def create_aliens6():
    for row in range(6):
        for col in range(5):
            alien = Aliens(100 + col * 100, row * -100)
            alien_group.add(alien)




class AlienBullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/alien_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def BulletSpeed(self):
        self.rect.y += 4
        if self.rect.top >= screen_height:
            self.kill()


    def BulletCollision(self):
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            spaceship.health_remaining -= 1
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

    def update(self):
        self.BulletSpeed()
        self.BulletCollision()

alien_bullet_group = pygame.sprite.Group()

# Create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'imgs/exp{num}.png')
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            # add the image to list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        #update explosion animation
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

explosion_group = pygame.sprite.Group()


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.click = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                self.click = True
                action = True


        if pygame.mouse.get_pressed()[0] == 0:
            self.click = False

        # Draw button on screen
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

start_img = pygame.image.load('imgs/Start_button.png').convert_alpha()
pause_img = pygame.image.load('imgs/pause_button.png').convert_alpha()
rsm_img = pygame.image.load('imgs/Resume_button.png').convert_alpha()
home_img = pygame.image.load('imgs/home_button.png').convert_alpha()
how_to_play_img = pygame.image.load('imgs/HTP_Button.png').convert_alpha()


#create button instances
start_button = Button(screen_width / 2 - 130, 320, start_img, 5)
htp_button = Button(screen_width / 2 + 130, 340, how_to_play_img, 5)


# how to play screen
class how2playscreen():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        screen.blit(self.image, (self.rect.x, self.rect.y))




# Gameloop
run = True

while run:

    # fps
    clock.tick(fps)

    # Draw bg
    draw_bg()



    if game == 0:

        # Drawing aliens based on level
        if len(alien_group) == 0 and level == 1:
            create_aliens2()
            level += 1
            weapon_type = 1
        elif len(alien_group) == 0 and level == 2:
            create_aliens3()
            level += 1
            weapon_type = 1
        elif len(alien_group) == 0 and level == 3:
            create_aliens4()
            level += 1
            weapon_type = 1
        elif len(alien_group) == 0 and level == 4:
            create_aliens5()
            level += 1
            weapon_type = 1
        elif len(alien_group) == 0 and level == 5:
            create_aliens6()
            level += 1
            weapon_type = 1
        elif len(alien_group) == 0 and level == 6:
            game = 1
            weapon_type = 1


        # draw sprite groups
        spaceship_group.draw(screen)
        bullet1_group.draw(screen)
        bullet2of1_group.draw(screen)
        bullet2of2_group.draw(screen)
        bullet2of3_group.draw(screen)
        alien_group.draw(screen)
        alien_bullet_group.draw(screen)
        switchweaponitem_group.draw(screen)
        explosion_group.draw(screen)
        heartitem_group.draw(screen)
        shielditem_group.draw(screen)
        shieldcircle_group.draw(screen)


    # Pause settings
        if pause == False:

            spaceship.update()
            bullet1_group.update()
            bullet2of1_group.update()
            bullet2of2_group.update()
            bullet2of3_group.update()
            alien_group.update()
            switchweaponitem_group.update()
            heartitem_group.update()
            shielditem_group.update()
            alien_bullet_group.update()
            shieldcircle_group.update()


            # Alien Shooting
            time_now = pygame.time.get_ticks()

            if level == 1:

                if len(alien_group) <= 1:
                    alien_cooldown = 1300
                if len(alien_group) >= 3:
                    alien_cooldown = 1000
                if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    # Pick random alien from group
                    attack_alien = random.choice(alien_group.sprites())
                    alien_bullet = AlienBullets(attack_alien.rect.centerx, attack_alien.rect.bottom)
                    alien_bullet_group.add(alien_bullet)
                    last_alien_shot = time_now

            elif level == 2:
                if len(alien_group) <= 2:
                    alien_cooldown = 1300
                if len(alien_group) >= 3:
                    alien_cooldown = 900
                if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    # Pick random alien from group
                    attack_alien = random.choice(alien_group.sprites())
                    alien_bullet = AlienBullets(attack_alien.rect.centerx, attack_alien.rect.bottom)
                    alien_bullet_group.add(alien_bullet)
                    last_alien_shot = time_now
            elif level == 3:
                if len(alien_group) <= 3:
                    alien_cooldown = 1300
                if len(alien_group) >= 4:
                    alien_cooldown = 800
                if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    # Pick random alien from group
                    attack_alien = random.choice(alien_group.sprites())
                    alien_bullet = AlienBullets(attack_alien.rect.centerx, attack_alien.rect.bottom)
                    alien_bullet_group.add(alien_bullet)
                    last_alien_shot = time_now

            elif level == 4:
                if len(alien_group) <= 4:
                    alien_cooldown = 1300
                if len(alien_group) >= 3:
                    alien_cooldown = 700
                if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    # Pick random alien from group
                    attack_alien = random.choice(alien_group.sprites())
                    alien_bullet = AlienBullets(attack_alien.rect.centerx, attack_alien.rect.bottom)
                    alien_bullet_group.add(alien_bullet)
                    last_alien_shot = time_now

            elif level == 5:
                if len(alien_group) <= 5:
                    alien_cooldown = 1300
                if len(alien_group) >= 3:
                    alien_cooldown = 600
                if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    # Pick random alien from group
                    attack_alien = random.choice(alien_group.sprites())
                    alien_bullet = AlienBullets(attack_alien.rect.centerx, attack_alien.rect.bottom)
                    alien_bullet_group.add(alien_bullet)
                    last_alien_shot = time_now

            elif level == 6:
                if len(alien_group) <= 6:
                    alien_cooldown = 1300
                if len(alien_group) >= 3:
                    alien_cooldown = 500
                if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
                    # Pick random alien from group
                    attack_alien = random.choice(alien_group.sprites())
                    alien_bullet = AlienBullets(attack_alien.rect.centerx, attack_alien.rect.bottom)
                    alien_bullet_group.add(alien_bullet)
                    last_alien_shot = time_now

            #Draw Button on screen
            pause_button = Button(screen_width - 80, 10, pause_img, 3)

            # Draw text
            draw_text(f"Level: {level}", font20, white, screen_width - 80, 80)

            # if paused button clicked
            key = pygame.key.get_pressed()
            if key[pygame.K_p]:
                pause = True
            if pause_button.draw():
                pause = True

        elif pause == True:
            resume_button = Button(screen_width / 2 - 130, 440, rsm_img, 5)
            home_button = Button(screen_width / 2 - 60, 440, home_img, 5)

            key = pygame.key.get_pressed()

            #resume button pushed
            if resume_button.draw() or key[pygame.K_r]:
                pause = False

            #home button pushed
            if home_button.draw() or key[pygame.K_h]:
                pause = False
                level = 1
                game = -1
                weapon_type = 1
                shield = 0
                #delete all groups
                alien_group.empty()
                alien_bullet_group.empty()
                heartitem_group.empty()
                switchweaponitem_group.empty()
                shielditem_group.empty()
                shieldcircle_group.empty()
                bullet1_group.empty()
                bullet2of1_group.empty()
                bullet2of2_group.empty()
                bullet2of3_group.empty()
                spaceship.kill()
                #put spaceship back
                spaceship = Spaceship(screen_width / 2, screen_height - 100, 3)
                spaceship_group.add(spaceship)
                spaceship.health_remaining = 3




    #Win Screen
    if game == 1:
        spaceship.kill()
        youwin_img = pygame.image.load('imgs/You_win.png').convert_alpha()
        youwin_text = how2playscreen(screen_width / 2 - 96, 200, youwin_img, 0.5)
        #delete all groups
        alien_group.empty()
        alien_bullet_group.empty()
        heartitem_group.empty()
        switchweaponitem_group.empty()
        shielditem_group.empty()
        shieldcircle_group.empty()
        bullet1_group.empty()
        bullet2of1_group.empty()
        bullet2of2_group.empty()
        bullet2of3_group.empty()
        home_button = Button(screen_width / 2 - 65, 420, home_img, 5)

        #if start/home button pressed
        key = pygame.key.get_pressed()
        if start_button.draw():
            print('again')
            level = 1
            spaceship = Spaceship(screen_width / 2, screen_height - 100, 3)
            spaceship_group.add(spaceship)
            spaceship.health_remaining = 3
            game = 0
            # starter aliens
            create_aliens1()

        elif home_button.draw() or key[pygame.K_h]:
            pause = False
            level = 1
            game = -1
            weapon_type = 1
            shield = 0
            # delete all groups
            alien_group.empty()
            alien_bullet_group.empty()
            heartitem_group.empty()
            switchweaponitem_group.empty()
            bullet1_group.empty()
            bullet2of1_group.empty()
            bullet2of2_group.empty()
            bullet2of3_group.empty()
            shielditem_group.empty()
            spaceship.kill()
            # put spaceship back
            spaceship = Spaceship(screen_width / 2, screen_height - 100, 3)
            spaceship_group.add(spaceship)
            spaceship.health_remaining = 3

    #Start screen
    if game == -1:
        title_img = pygame.image.load('imgs/Cosmic_invasion.png').convert_alpha()
        htptxt_text = how2playscreen(screen_width / 2 - 160, 150, title_img, 0.5)
        heartitemtext_group.empty()
        heartitemtext_group.empty()
        heartitemtext_group.empty()

        if htp_button.draw():
            how_2_play = 1
            heartitemtext = HeartItemtext(screen_width / 2 - 250, 200)
            heartitemtext_group.add(heartitemtext)
            shielditemtext = ShieldItemtext(screen_width / 2 - 250, 270)
            heartitemtext_group.add(shielditemtext)
            switchweapontext = SwitchWeaponItemtext(screen_width / 2 - 250, 340)
            heartitemtext_group.add(switchweapontext)

        #Button
        key = pygame.key.get_pressed()
        if start_button.draw() or key[pygame.K_s]:
            print('Start')
            game = 0
            # starter aliens
            create_aliens1()

    if how_2_play == 1:
        # start screen disappear
        game = -3


    # Lose screen
    if game == -2:
        # delete all groups
        alien_group.empty()
        alien_bullet_group.empty()
        heartitem_group.empty()
        switchweaponitem_group.empty()
        bullet1_group.empty()
        bullet2of1_group.empty()
        bullet2of2_group.empty()
        bullet2of3_group.empty()

        draw_text(f"You made it to level  {level}", font40, white, screen_width / 2 - 180, 200)
        #again = button(screen_width / 2 - 90, 450, 'Play Again')
        if start_button.draw():
            print('again')
            level = 1
            game = 0
            weapon_type = 1
            spaceship = Spaceship(screen_width / 2, screen_height - 100, 3)
            spaceship_group.add(spaceship)
            spaceship.health_remaining = 3
            # starter aliens
            create_aliens1()

    #How to play screen
    if game == -3:
        htptxt_img = pygame.image.load('imgs/How_to_play_text.png').convert_alpha()
        htptxt_text = how2playscreen(screen_width / 2 - 160, 50, htptxt_img, 0.5)
        htpdes_img = pygame.image.load('imgs/h2p_description.png').convert_alpha()
        htpdes_text = how2playscreen(screen_width / 2 - 299, 100, htpdes_img, 0.2)
        # heart
        htphearttxt_img = pygame.image.load('imgs/Heart_text.png').convert_alpha()
        htphearttxt_text = how2playscreen(screen_width / 2 - 270, 170, htphearttxt_img, 0.2)
        htpheartdes_img = pygame.image.load('imgs/Heart_description.png').convert_alpha()
        htpheartdes_text = how2playscreen(screen_width / 2 - 220, 190, htpheartdes_img, 0.2)
        # shield
        htpshieldtxt_img = pygame.image.load('imgs/Shield_text.png').convert_alpha()
        htpshieldttxt_text = how2playscreen(screen_width / 2 - 270, 225, htpshieldtxt_img, 0.2)
        htpshielddes_img = pygame.image.load('imgs/Shield_description.png').convert_alpha()
        htpshielddes_text = how2playscreen(screen_width / 2 - 220, 250, htpshielddes_img, 0.2)
        # weapon
        htpweapontxt_img = pygame.image.load('imgs/WeaponItem_text.png').convert_alpha()
        htpweaponttxt_text = how2playscreen(screen_width / 2 - 270, 300, htpweapontxt_img, 0.2)
        htpweapondes_img = pygame.image.load('imgs/Weaponitem_description.png').convert_alpha()
        htpweapondes_text = how2playscreen(screen_width / 2 - 220, 320, htpweapondes_img, 0.2)

        # heart/shield/weapon animation
        heartitemtext_group.draw(screen)
        heartitemtext_group.update()
        shielditemtext_group.draw(screen)
        shielditemtext_group.update()
        switchweaponitem_group.draw(screen)
        switchweaponitem_group.update()

        # home button
        home_button = Button(screen_width / 2 - 70, 500, home_img, 5)
        if home_button.draw() or key[pygame.K_h]:
            how_2_play = 0
            game = -1






    explosion_group.update()

    # Exit loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False



    # Update Loop
    pygame.display.update()




pygame.quit()

# All code is done by Adan Trejo