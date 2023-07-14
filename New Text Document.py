import pygame
from sys import exit
from random import randint
import math

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

background_surf = pygame.image.load('textures/grass.png')
background_surf = pygame.transform.scale(background_surf, (SCREEN_WIDTH,SCREEN_HEIGHT))

print("hello")


#Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_surf = pygame.image.load('textures/transparentcirclewithface.png').convert_alpha()
        self.player_surf = pygame.transform.scale(self.player_surf, (65,65))
        self.image = self.player_surf
        #self.image = self.player_walk[self.player_index]
        self.rect = self.player_surf.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.health = 100
        self.x_velocity = 0
        self.y_velocity = 0

        #Inherits Gun or whatever
        self.gun = Gun(self)
        #self.gun_group = pygame.sprite.GroupSingle()
        #self.gun_group.add(self.gun)

    def player_key_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y_velocity = 3
        elif keys[pygame.K_s]:
            self.y_velocity = -3
        else:
            self.y_velocity = 0
        if keys[pygame.K_d]:
            self.x_velocity = 3
        elif keys[pygame.K_a]:
            self.x_velocity = -3
        else:
            self.x_velocity = 0

    def player_mouse_input(self):
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Check the left mouse button
            #self.gun_sound.play()
            self.gun.shoot()

    def apply_velocity(self):
        self.rect.y -= self.y_velocity
        self.rect.x += self.x_velocity
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        elif self.rect.top < 0:
            self.rect.top = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0

    def get_health(self):
        return self.health
    
    def set_health(self, new_health):
        self.health = new_health

    def update(self):
        self.player_key_input()
        self.player_mouse_input()
        self.apply_velocity()
        #self.gun_group.update()

class Gun(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.gun_surf = pygame.image.load('textures/gun_image.png').convert_alpha()
        self.gun_surf = pygame.transform.scale(self.gun_surf, (65,65))
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.angle = 0
        self.shoot_cooldown = 400
        self.last_shot_time = 0
        self.range = 200
        #self.gun_sound = pygame.mixer.Sound('audio/gunshot.mp3')
        self.gun_sound = pygame.mixer.Sound('audio/gunshot3.mp3')


    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.last_shot_time = current_time

            self.gun_sound.play()
            mouse_pos = pygame.mouse.get_pos()

            x_1 = self.player.rect.center[0]
            y_1 = self.player.rect.center[1]

            x_2 = mouse_pos[0] 
            y_2 = mouse_pos[1]

            angle = math.atan2(y_2 - y_1, x_2 - x_1)  # Calculate the angle between the player and mouse position, measured in radians

            x_3 = x_1 + self.range * math.cos(angle)  # Calculate the endpoint of the line using sohcahtoa ;)
            y_3 = y_1 + self.range * math.sin(angle)

            pygame.draw.line(screen, 'Yellow', (x_1, y_1),(x_3, y_3), 4)





    def stayon_player(self):
        player_position = player.sprite.rect.center
        self.rect.center = player_position


    def update(self):
        self.stayon_player()
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.enemy_surf = pygame.image.load('textures/enemy.png').convert_alpha()
        self.enemy_surf = pygame.transform.scale(self.enemy_surf, (77,77))
        self.image = self.enemy_surf
        self.rect = self.image.get_rect(center = (randint(0,500),randint(0,500)))
        self.x_velocity = 0
        self.y_velocity = 0
        self.speed = 1

    def apply_velocity(self):
        self.rect.y -= self.y_velocity
        self.rect.x += self.x_velocity

    def follow_player(self):
        player_position = player.sprite.rect.center
        if self.rect.center[0] < player_position[0]:
            self.x_velocity = 1 * self.speed
        elif self.rect.center[0] > player_position[0]:
            self.x_velocity = -1 * self.speed
        else:
            self.x_velocity = 0
        if self.rect.center[1] < player_position[1]:
            self.y_velocity = -1 * self.speed
        elif self.rect.center[1] > player_position[1]:
            self.y_velocity = 1 * self.speed
        else: self.y_velocity = 0

    def update(self):
        self.follow_player()
        self.apply_velocity()



#Methods
def collision_player_enemy():
    for enemy in enemy_group:
        dx = player.sprite.rect.centerx - enemy.rect.centerx
        dy = player.sprite.rect.centery - enemy.rect.centery
        distance_squared = dx**2 + dy**2
        combined_radius = (player.sprite.rect.width + enemy.rect.width)/2

        if distance_squared < (combined_radius**2):
            print('collision')
            return False
    
    return True

#Create Screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('shooter')

#Timers
enemy_timer = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_timer, 1500)

#Initialize Variables
game_active = True
clock = pygame.time.Clock()

#Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

gun = pygame.sprite.GroupSingle()
gun.add(Gun(player))

enemy_group = pygame.sprite.Group()
enemy_group.add(Enemy())


#Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit() #breaks out of the while True loop
        if game_active:
            if event.type == enemy_timer:
                enemy_group.add(Enemy())
    
    if game_active:
        #Draw background
        screen.blit(background_surf, (0,0))

        #Draw player sprite
        player.draw(screen)
        player.update()

        #Update Gun
        #gun.update()

        gun.draw(screen)
        gun.update()

        #Update all enemies
        for enemy in enemy_group:
            enemy.update()

        enemy_group.draw(screen)

        #check for collision
        game_active = collision_player_enemy()

        
 

    pygame.display.update()
    clock.tick(60)