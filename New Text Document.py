import pygame
from sys import exit
from random import randint, choice
import math

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

background_surf = pygame.image.load('textures/grass.png')
background_surf = pygame.transform.scale(background_surf, (SCREEN_WIDTH,SCREEN_HEIGHT))

#Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_surf = pygame.image.load('textures/cat1.png').convert_alpha()
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
        self.gun_surf = pygame.transform.scale_by(self.gun_surf, 0.2)
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.angle = 0

        self.shoot_cooldown = 750
        self.shoot_wait_constant = 750
        self.last_shot_time = 0
        self.range = 300
        self.got_one = False
        self.bullets = 2
        self.reload_time = 1400

        #gun sounds
        self.gun_sound = pygame.mixer.Sound('audio/gunshot3.mp3')
        self.hit_sound = pygame.mixer.Sound('audio/hitsound.mp3')
        self.reload_sound = pygame.mixer.Sound('audio/reload.mp3')

    def line_circle_collision(self, line_start, line_end, circle_center, circle_radius):
        # Unpack the coordinates of line_start and line_end
        x1, y1 = line_start
        x2, y2 = line_end

        # Unpack the coordinates of circle_center
        x, y = circle_center

        # Calculate the direction vector of the line segment
        dx = x2 - x1
        dy = y2 - y1

        # Calculate the squared length of the line segment
        line_length_squared = dx * dx + dy * dy

        # Calculate the parameter for the closest point on the line to the circle center
        t = ((x - x1) * dx + (y - y1) * dy) / line_length_squared

        # Calculate the closest point on the line to the circle center
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Calculate the distance between the closest point and the circle center
        distance_squared = (x - closest_x) * (x - closest_x) + (y - closest_y) * (y - closest_y)

        # Check if the closest point is within the line segment and the circle intersects
        if t >= 0 and t <= 1 and distance_squared <= circle_radius * circle_radius:
            return True
        else:
            return False

    def shoot(self):
        self.got_one = False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.shoot_cooldown = self.shoot_wait_constant
            self.bullets -= 1
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

            bullet_start = (x_1, y_1)
            bullet_end = (x_3, y_3)

            pygame.draw.line(screen, 'Yellow', (x_1, y_1),(x_3, y_3), 4)

            #check collision with enemies

            for enemy in enemy_group:
                enemy_center = enemy.rect.center
                enemy_radius = enemy.rect.width //2

                if self.line_circle_collision(bullet_start, bullet_end, enemy_center, enemy_radius):
                    if not self.got_one: self.got_one = True
                    pygame.sprite.Sprite.kill(enemy)
                    score_manager.increase()
            if self.got_one: self.hit_sound.play()
        if self.bullets <= 0:
            self.shoot_cooldown = self.reload_time
            self.bullets = 2
            self.reload_sound.play()


    def stayon_player(self):
        player_position = player.sprite.rect.center
        self.rect.center = player_position
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(mouse_pos[1] - player_position[1], mouse_pos[0] - player_position[0])
        self.angle = math.degrees(angle)

        if mouse_pos[0] > self.rect.left:
            self.image = pygame.transform.rotate(self.gun_surf, -self.angle)
        else:
            self.image = pygame.transform.flip(pygame.transform.rotate(self.gun_surf, self.angle), False, True)


    def update(self):
        self.stayon_player()
        self.display_bullets()

    def display_bullets(self):
        bullets_surf = score_font.render(f'bullets: {self.bullets}',False, (64,64,64))
        bullets_rect = bullets_surf.get_rect(center = (int(8 * SCREEN_WIDTH/9),int(8 * SCREEN_HEIGHT/9)))
        screen.blit(bullets_surf,bullets_rect)
        

    def reset(self):
        self.bullets = 2
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()
        if type == 'bork':
            self.enemy_surf = pygame.image.load('textures/bork.png').convert_alpha()
            self.enemy_surf = pygame.transform.scale(self.enemy_surf, (77,77))
            self.speed = 1
        elif type == 'zoomer':
            self.enemy_surf = pygame.image.load('textures/zoomer.png').convert_alpha()
            self.enemy_surf = pygame.transform.scale(self.enemy_surf, (50,50))
            self.speed = 1.3 #this doesnt work cause integers

        self.type = type


        self.image = self.enemy_surf
        self.quadrant = choice(['Top','Bottom','Left','Right'])
        if self.quadrant == 'Top':
            self.rect = self.image.get_rect(midbottom = (randint(0,SCREEN_WIDTH), -5))
        elif self.quadrant == 'Bottom':
            self.rect = self.image.get_rect(midtop = (randint(0,SCREEN_WIDTH), SCREEN_HEIGHT))
        elif self.quadrant == 'Left':
            self.rect = self.image.get_rect(midright = (-5, randint(0, SCREEN_HEIGHT)))
        else: 
            self.rect = self.image.get_rect(midleft = ((SCREEN_WIDTH + 5), randint(0,SCREEN_HEIGHT)))
                                            
        self.x_velocity = 0
        self.y_velocity = 0

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

        #def check_collisions(self, bullets):
         #   hit_list = 
    def zoomer_rotate(self):
        #print("finish this code")
        bruh = 1


    def update(self):
        if self.type == 'zoomer':
            self.zoomer_rotate()
        self.follow_player()
        self.apply_velocity()

#score manager
class Score:
    def __init__(self):
        self.score = 0
        self.high_score = 0

    def increase(self):
        self.score += 1

    def restart(self):
        if self.score>self.high_score:
            self.high_score = self.score
        self.score = 0

    def get_score(self):
        return self.score
    
    def get_high_score(self):
        return self.high_score
    
    def is_high_score(self):
        return self.score > self.high_score
#menu cats
class MenuCat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.cat_surf = pygame.image.load('textures/cat1.png').convert_alpha()
        self.cat_surf = pygame.transform.scale(self.cat_surf, (100,100))
        self.speed = 1.3 #this doesnt work cause integers
        self.image = self.cat_surf
        self.direction = choice(('left','right'))

        self.rect = self.image.get_rect(midbottom = (randint(0,SCREEN_WIDTH), -5))
                                             
        self.y_velocity = randint(1,5)

    def fall_down(self):
        self.rect.y += self.y_velocity
        #self.rect.x += self.x_velocity


    def cleanup(self):
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

    def update(self):
        self.cleanup()
        self.fall_down()

#Methods
def collision_player_enemy():
    for enemy in enemy_group:
        dx = player.sprite.rect.centerx - enemy.rect.centerx
        dy = player.sprite.rect.centery - enemy.rect.centery
        distance_squared = dx**2 + dy**2
        combined_radius = (player.sprite.rect.width + enemy.rect.width)/2

        if distance_squared < (combined_radius**2):
            return False
    
    return True

def restart():
    player.sprite.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    enemy_group.empty()
    player.sprite.gun.reset()

def display_score():
    score_surf = score_font.render(f'Score: {score_manager.get_score()}',False, (64,64,64))
    score_rect = score_surf.get_rect(center = (SCREEN_WIDTH//2,20))
    screen.blit(score_surf,score_rect)

def color_invert(colors):
    inverted_colors = []
    for i in range(len(colors)):
        inverted_colors.append(255 - colors[i])
    return inverted_colors



#Create Screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('cat with a gun')

#Timers
bork_timer = pygame.USEREVENT + 1
pygame.time.set_timer(bork_timer, 500)

zoomer_timer = pygame.USEREVENT + 2
pygame.time.set_timer(zoomer_timer, 5000)

menu_cat_timer = pygame.USEREVENT + 3
pygame.time.set_timer(menu_cat_timer, 500)




#Initialize Variables
#game_active = True
restart_delay = 1500
clock = pygame.time.Clock()
game_state = 'menu'

#Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

#old
gun = pygame.sprite.GroupSingle()
gun.add(Gun(player))

#new
#gun = Gun(player.sprite)

enemy_group = pygame.sprite.Group()
#enemy_group.add(Enemy('bork'))

#menu cats
menu_cats_group = pygame.sprite.Group()

#Score
score_manager = Score()

#Font
gameover_font = pygame.font.Font('font/Pixeltype.ttf', 150)
message_font = pygame.font.Font('font/Pixeltype.ttf', 100)
score_font = pygame.font.Font('font/Pixeltype.ttf', 50)

game_state = 'render'

#Songs
pygame.mixer.init()


songs = []
#songs.append(pygame.mixer.Sound('audio/songs/1. Miniature Fantasy - Platform Racing Two Cast.mp3'))
songs.append(pygame.mixer.Sound('audio/songs/2. Paradise On E - Parker Brothers and Andrea Prairie-Isochromatic.mp3'))
songs.append(pygame.mixer.Sound('audio/songs/3. Crying Soul - Andrew Dreamscaper Parker, Bounce Parker.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/4. My Vision - Tom Maestro.mp3'))
songs.append(pygame.mixer.Sound('audio/songs/5. Switchblade - Katie Reasoner and Sandy Kenny Alzini Parker.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/6. The Wires - Katie Reasoner, Andrew Dreamscaper Parker and Cheez Ratnam Usina.mp3'))
songs.append(pygame.mixer.Sound('audio/songs/7. Before Mydnite - Tom Maestro and Failand Ratnam.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/8. Broked It - Sally Whitney Touch.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/9. Hello - Tom Montegmory Martin.mp3'))
songs.append(pygame.mixer.Sound('audio/songs/10. Pyrokinesis - Katie Reasoner, Tom Montegmory Martin and Sean Tucker.mp3'))
songs.append(pygame.mixer.Sound('audio/songs/11. Flowerz n Herbz - Tom Montegmory Martin and Brunalle Brunzolaitis.mp3'))

punch_sound = pygame.mixer.Sound('audio/punch.mp3')
splat_sound = pygame.mixer.Sound('audio/splat.mp3')

for song in songs:
    song.set_volume(0.3)



#old
#songs[randint(0,len(songs)-1)].play()

pygame.mixer.music.load('audio/songs/9. Hello - Tom Montegmory Martin.mp3')
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play()

#background rgb
colors = [0,0,0]
inverse_colors = [0,0,0]

#Game loop
while True:
    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit() #breaks out of the while True loop
        if game_state == 'gameplay':
            if event.type == bork_timer:
                enemy_group.add(Enemy('bork'))
            elif event.type == zoomer_timer:
                enemy_group.add(Enemy('zoomer'))
        if game_state == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button_rect.collidepoint(event.pos):
                    game_state = 'gameplay'
                    punch_sound.play()
                    pygame.mixer.music.load('audio/songs/5. Switchblade - Katie Reasoner and Sandy Kenny Alzini Parker.mp3')
                    pygame.mixer.music.play()
                    restart()
                    score_manager.restart()
                    menu_cats_group.empty()
            if event.type == menu_cat_timer:
                menu_cats_group.add(MenuCat())
        if game_state == 'gameover':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_button_rect.collidepoint(event.pos):
                    game_state = 'menu'
                    punch_sound.play()
                    pygame.mixer.music.load('audio/songs/9. Hello - Tom Montegmory Martin.mp3')
                    pygame.mixer.music.play()
    
    if game_state == 'gameplay':
        #Draw background
        screen.blit(background_surf, (0,0))

        #Draw player sprite
        player.draw(screen)
        player.update()

        #Update Gun
        #gun.update()
        #old
        gun.draw(screen)
        gun.update()

        #Update all enemies
        for enemy in enemy_group:
            enemy.update()

        enemy_group.draw(screen)

        display_score()

        #check for collision

        if not collision_player_enemy():
            death_time = pygame.time.get_ticks()
            game_state = 'death'
            splat_sound.play()
            pygame.mixer.music.fadeout(500)

    elif game_state =='menu' or game_state == 'render':
        screen.fill((colors[0],colors[1],colors[2]))
        for cat in menu_cats_group:
            cat.update()

        menu_cats_group.draw(screen)
        title_message = gameover_font.render(f'cat with a gun', False,'Black')
        title_message_rect = title_message.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//6))
        screen.blit(title_message, title_message_rect)

        x = pygame.time.get_ticks()//7.5

        for i in range(len(colors)):
            if i == 0:
                colors[i] = (math.sin((x/255)*255) +255)/2
            elif i == 1:
                colors[i] = (math.sin((x / 255) + 2 * math.pi * (2 / 3)) * 255 + 255) / 2
            elif i == 2:
                colors[i] = (math.sin((x / 255) + 2 * math.pi * (1 / 3)) * 255 + 255) / 2
        inverse_colors = color_invert(colors)
        play_message = message_font.render(f'PLAY', False,'Black')
        play_message_rect = play_message.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        scaled_surf = pygame.transform.scale_by(play_message, 1.2)
        play_button_rect = scaled_surf.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        pygame.draw.rect(screen,inverse_colors,play_button_rect,border_radius= 20)
        screen.blit(play_message, play_message_rect)
        game_state = 'menu'

    
    elif game_state == 'gameover' or game_state == 'death':
        #End Screen
        screen.fill('Red')
        gameover_message = gameover_font.render(f'GAME OVER', False,'Black')
        gameover_message_rect = gameover_message.get_rect(center = (SCREEN_WIDTH//2,SCREEN_WIDTH//6))
        screen.blit(gameover_message,gameover_message_rect)

        restart_message = message_font.render(f'press any key to restart', False,'Black')
        restart_message_rect = restart_message.get_rect(center = (SCREEN_WIDTH//2,SCREEN_WIDTH//2))
        screen.blit(restart_message,restart_message_rect)

        score_text = score_text = message_font.render(f'Score: {score_manager.get_score()}', False, 'White')
        score_text_rect = score_text.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//1.8))
        screen.blit(score_text, score_text_rect)

        menu_message = message_font.render(f'menu', False,'Black')
        menu_message_rect = menu_message.get_rect(center = (int(6 * SCREEN_WIDTH//7),SCREEN_HEIGHT//10))
        menu_button_surf = pygame.transform.scale_by(menu_message, 1.2)
        menu_button_rect = menu_button_surf.get_rect(center = menu_message_rect.center)
        pygame.draw.rect(screen,'Pink',menu_button_rect,border_radius= 20)
        screen.blit(menu_message, menu_message_rect)


        if score_manager.is_high_score():
            high_score_text = message_font.render(f'High score!', False, 'Blue')
        else: 
            high_score_text = message_font.render(f'High Score: {score_manager.get_high_score()}', False, 'Blue')
        high_score_text_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2,1.5*SCREEN_HEIGHT//2))
        screen.blit(high_score_text, high_score_text_rect)

        game_state = 'gameover'



        if any(pygame.key.get_pressed()) and pygame.time.get_ticks() > death_time + restart_delay:
            game_state = 'gameplay'
            restart()
            score_manager.restart()
            pygame.mixer.music.play()
        


        
 

    pygame.display.update()
    clock.tick(60)