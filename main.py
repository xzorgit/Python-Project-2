import pygame
from sys import exit
from random import randint, choice
import math

#Constants
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

#Load background image and scale to screen
background_surf = pygame.image.load('textures/grass.png')
background_surf = pygame.transform.scale(background_surf, (SCREEN_WIDTH,SCREEN_HEIGHT))

#Classes
#Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #Player surface and image
        self.player_surf = pygame.image.load('textures/cat1.png').convert_alpha()
        self.player_surf = pygame.transform.scale(self.player_surf, (65,65))
        self.image = self.player_surf
        self.cool_sound = pygame.mixer.Sound('audio/cool.mp3')
        self.cool_chime = pygame.mixer.Sound('audio/coolchime.mp3')

        #Place the player in the center at the start of the game
        self.rect = self.player_surf.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))

        #Player variables 
        self.health = 100 #Unused implement later maybe
        self.x_velocity = 0
        self.y_velocity = 0
        self.x_accel = 0
        self.y_accel = 0
        self.max_velocity = 3
        self.acceleration = 0.65
        self.friction = 0.8

        #cool_meter values
        self.cool_meter = 0
        self.max_meter = 20

        #gun recoil variables
        self.recoil_acceleration = 1.5  # Adjust the recoil acceleration as needed

        #Inherits Gun or whatever
        self.gun = Gun(self) 

    #Set velocity based on directional wasd input (handle keyboard input)
    def player_key_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y_accel = self.acceleration
        elif keys[pygame.K_s]:
            self.y_accel = -self.acceleration
        else:
            self.y_accel = 0
        if keys[pygame.K_d]:
            self.x_accel = self.acceleration
        elif keys[pygame.K_a]:
            self.x_accel = -self.acceleration
        else:
            self.x_accel = 0
    #Handle mouse input
    def player_mouse_input(self):
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  #if left mouse button is pressed
            self.gun.shoot()

    #Handle movement of player
    def apply_velocity(self):
        self.x_velocity += self.x_accel
        self.y_velocity += self.y_accel

        self.rect.y -= self.y_velocity
        self.rect.x += self.x_velocity

        if self.x_accel == 0:
            self.x_velocity *= self.friction
        if self.y_accel == 0:
            self.y_velocity *= self.friction

        # Limit the maximum velocity
        self.x_velocity = min(self.max_velocity, max(-self.max_velocity, self.x_velocity))
        self.y_velocity = min(self.max_velocity, max(-self.max_velocity, self.y_velocity))


        #Keep player within the bounds of the screen
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        elif self.rect.top < 0:
            self.rect.top = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0

    #Unused, implement later
    def get_health(self):
        return self.health
    
    #Unused implement later
    def set_health(self, new_health):
        self.health = new_health

    def increase_cool_meter(self, value):
        self.cool_meter += value

    def display_cool_meter(self):
        cool_meter_surf = score_font.render(f'cool meter: {self.cool_meter}',False, (64,64,64))
        cool_meter_rect = cool_meter_surf.get_rect(center = (SCREEN_WIDTH//2,int(8 * SCREEN_HEIGHT/9)))
        screen.blit(cool_meter_surf,cool_meter_rect)

    def display_bullets(self):
        if self.gun.is_reloading():
            bullets_surf = score_font.render('reloading',False, (64,64,64))
            bullets_rect = bullets_surf.get_rect(center = (int(8 * SCREEN_WIDTH/9),int(8 * SCREEN_HEIGHT/9)))
        else:
            bullets_surf = score_font.render(f'bullets: {self.gun.bullets}',False, (64,64,64))
            bullets_rect = bullets_surf.get_rect(center = (int(8 * SCREEN_WIDTH/9),int(8 * SCREEN_HEIGHT/9)))
        
        screen.blit(bullets_surf,bullets_rect)

    def cool_logic(self):
        self.display_cool_meter()
        if self.cool_meter >= self.max_meter:
            self.cool_meter = 0
            self.cool_sound.play()
            self.cool_chime.play()
            #do cool meter stuff
            print("cool!")

    #Call all neccesary functions to update the player
    def update(self):
        self.cool_logic()
        self.player_key_input()
        self.player_mouse_input()
        self.apply_velocity()
        self.display_bullets()

    #Resets player and gun
    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Reset player's position
        self.cool_meter = 0  # Reset cool meter to 0
        self.gun.reset()


#Gun Class
class Gun(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.gun_surf = pygame.image.load('textures/gun_image.png').convert_alpha()
        self.gun_surf = pygame.transform.scale_by(self.gun_surf, 0.2)
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        self.angle = 0

        #Initialize gun variables
        self.shoot_cooldown = 750
        self.shoot_wait_constant = 750
        #og = 300
        self.range = 300
        self.got_one = False
        self.bullets = 2
        self.reload_time = 1300
        self.last_shot_time  = pygame.time.get_ticks()
        self.reload_start_time = -1

        #Gun sounds
        self.gun_sound = pygame.mixer.Sound('audio/gunshot3.mp3')
        self.hit_sound = pygame.mixer.Sound('audio/hitsound.mp3')
        self.reload_sound = pygame.mixer.Sound('audio/reload.mp3')

        #Combo sounds
        self.wow_sound = pygame.mixer.Sound('audio/wow.mp3')
        self.nice_sound = pygame.mixer.Sound('audio/nice.mp3')
        self.yipee_sound = pygame.mixer.Sound('audio/yipee.mp3')
        self.holymoly_sound = pygame.mixer.Sound('audio/holymoly.mp3')

    #Returns true if the bullet (line segment) collides with any enemies. Should probably rename to make it more clear
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

    #Shoot gun
    def shoot(self):
        self.got_one = False #is used to only play the hit sound once and only once, even if collision with multiple enemies
        current_time = pygame.time.get_ticks()
        #If a shot at this time is valid
        if current_time - self.last_shot_time > self.shoot_cooldown:
            #Shooting bullet logic
            self.shoot_cooldown = self.shoot_wait_constant
            self.bullets -= 1
            self.last_shot_time = current_time

            self.gun_sound.play()
            mouse_pos = pygame.mouse.get_pos()

            #this could be done in a method or something but it took me so long to figure out im just not gonna touch it
            #shoots a bullet with length self.range starting at player position going towards the mouse position
            x_1 = self.player.rect.center[0]
            y_1 = self.player.rect.center[1]

            x_2 = mouse_pos[0] 
            y_2 = mouse_pos[1]

            angle = math.atan2(y_2 - y_1, x_2 - x_1)  # Calculate the angle between the player and mouse position, measured in radians

            #Calculates the ending position of the bullet
            x_3 = x_1 + self.range * math.cos(angle)  # Calculate the endpoint of the line using sohcahtoa ;)
            y_3 = y_1 + self.range * math.sin(angle)

            bullet_start = (x_1, y_1)
            bullet_end = (x_3, y_3)

            #draws the bullet to the screen
            pygame.draw.line(screen, 'Yellow', (x_1, y_1),(x_3, y_3), 4)

            if abs(angle) > 3.14/2:
                orientation = 'left'
            else:
                orientation = 'right'

            #check bullet collision with enemies
            hits = 0
            for enemy in enemy_group:
                enemy_center = enemy.rect.center
                enemy_radius = enemy.rect.width //2

                if self.line_circle_collision(bullet_start, bullet_end, enemy_center, enemy_radius):
                    if not self.got_one: self.got_one = True
                    pygame.sprite.Sprite.kill(enemy)
                    score_manager.increase()
                    blood_splat_group.add(BloodSplat(enemy_center, orientation))
                    hits += 1
            if self.got_one and hits >= 2:
                self.hit_sound.play() #Plays the hitsound only once
                if hits == 3:
                    self.nice_sound.play()
                elif hits == 4:
                    #wow
                    self.wow_sound.play()
                elif hits == 5:
                    self.yipee_sound.play()
                elif hits > 5:
                    self.holymoly_sound.play()
                self.player.increase_cool_meter((hits-1)*2)
            print("hits: ", hits)

        #reloads gun , could put this in a reload() method maybe
        if self.bullets <= 0:
            self.reload_start_time = pygame.time.get_ticks()
            self.shoot_cooldown = self.reload_time
            self.bullets = 2
            self.reload_sound.play()

    def is_reloading(self):
        #complete this code
        current_time = pygame.time.get_ticks()
        #If a shot at this time is valid
        if current_time < self.reload_start_time + self.reload_time:
            return True
        return False
    

    #keeps gun centered on the players position
    def stayon_player(self):
        player_position = player.sprite.rect.center
        self.rect.center = player_position
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(mouse_pos[1] - player_position[1], mouse_pos[0] - player_position[0])
        self.angle = math.degrees(angle)

        #Flips the gun depending on the position of the mouse so it is facing the right way
        if mouse_pos[0] > self.rect.left:
            self.image = pygame.transform.rotate(self.gun_surf, -self.angle)
        else:
            self.image = pygame.transform.flip(pygame.transform.rotate(self.gun_surf, self.angle), False, True)

    #Calls methods to update the gun position and display the bullet counter
    def update(self):
        self.stayon_player()

    #Sets bullets to 2, I will have to change this later if I have guns with different types    
    def reset(self):
        self.last_shot_time  = pygame.time.get_ticks()
        self.bullets = 2
            
#Enemy class
#Takes in string type to identify what kind of enemy it is
class Enemy(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()
        #Initialize variables depending on the type
        if type == 'bork':
            self.enemy_surf = pygame.image.load('textures/bork.png').convert_alpha()
            self.enemy_surf = pygame.transform.scale(self.enemy_surf, (77,77))
            self.max_velocity = 2
            self.acceleration = 0.1
            self.friction = 0.8
        elif type == 'zoomer':
            self.enemy_surf = pygame.image.load('textures/zoomer.png').convert_alpha()
            self.enemy_surf = pygame.transform.scale(self.enemy_surf, (60,60))
            self.max_velocity = 2.8
            self.acceleration = 0.03
            self.friction = 0.8


        self.type = type
        self.image = self.enemy_surf
        #Spawns enemy outside of the screen from a random part
        self.quadrant = choice(['Top','Bottom','Left','Right'])
        if self.quadrant == 'Top':
            self.rect = self.image.get_rect(midbottom = (randint(0,SCREEN_WIDTH), -5))
        elif self.quadrant == 'Bottom':
            self.rect = self.image.get_rect(midtop = (randint(0,SCREEN_WIDTH), SCREEN_HEIGHT + 5))
        elif self.quadrant == 'Left':
            self.rect = self.image.get_rect(midright = (-5, randint(0, SCREEN_HEIGHT)))
        else: 
            self.rect = self.image.get_rect(midleft = ((SCREEN_WIDTH + 5), randint(0,SCREEN_HEIGHT)))
                                            
        #initialize velocity variables
        self.x_velocity = 0
        self.y_velocity = 0
        self.x_accel = 0
        self.y_accel = 0
  

    #Applies the velocity
    def apply_velocity(self):
        self.x_velocity += self.x_accel
        self.y_velocity += self.y_accel
        self.rect.y -= self.y_velocity
        self.rect.x += self.x_velocity

        if self.x_accel == 0:
            self.x_velocity *= self.friction
        if self.y_accel == 0:
            self.y_velocity *= self.friction

        if abs(self.x_velocity) > self.max_velocity:
            self.x_velocity = math.copysign(self.max_velocity, self.x_velocity)
        if abs(self.y_velocity) > self.max_velocity:
            self.y_velocity = math.copysign(self.max_velocity, self.y_velocity)



    #Changes x and y velocity to always move towards player
    def follow_player(self):
        player_position = player.sprite.rect.center
        if self.rect.center[0] < player_position[0]:
            self.x_accel = 1 * self.acceleration
        elif self.rect.center[0] > player_position[0]:
            self.x_accel = -1 * self.acceleration
        else:
            self.x_velocity = 0
            self.x_accel = 0
        if self.rect.center[1] < player_position[1]:
            self.y_accel = -1 * self.acceleration
        elif self.rect.center[1] > player_position[1]:
            self.y_accel = 1 * self.acceleration
        else: 
            self.y_velocity = 0
            self.y_accel = 0

    def update(self):
        self.follow_player()
        self.apply_velocity()

#Blood splat class
class BloodSplat(pygame.sprite.Sprite):
    def __init__(self, position, orientation):
        super().__init__()
        blood_png = 'textures/blood' + str(randint(1,6)) + '.png'
        self.image = pygame.image.load(blood_png).convert_alpha()
        if orientation == 'right':
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=position)
        self.transparency = 255

    def increase_transparency(self):
        self.transparency += -1.5
        self.image.set_alpha(self.transparency)

    def update(self):
        if self.transparency<=0:
            self.kill()
        self.increase_transparency()

#Score manager
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
    
#MenuCat Class (falling cats in the menu screen)
class MenuCat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.cat_surf = pygame.image.load('textures/cat1.png').convert_alpha()
        self.cat_surf = pygame.transform.scale(self.cat_surf, (100,100))
        self.image = self.cat_surf
        #Spawn MenuCat at a random horizontal position above the screen
        self.rect = self.image.get_rect(midbottom = (randint(-5,SCREEN_WIDTH + 5), -5))
                                             
        self.y_velocity = randint(1,5)

    #Applies velocity to the y position
    def fall_down(self):
        self.rect.y += self.y_velocity

    #kill instance if below screen
    def cleanup(self):
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

    #Calls methods to update menucats
    def update(self):
        self.cleanup()
        self.fall_down()

#Methods
#Checks collision between the player and and enemies (returns True if collision)
#there might be an easier way to do this using pygame, but idk i just did some math
def collision_player_enemy():
    for enemy in enemy_group:
        dx = player.sprite.rect.centerx - enemy.rect.centerx
        dy = player.sprite.rect.centery - enemy.rect.centery
        distance_squared = dx**2 + dy**2
        combined_radius = (player.sprite.rect.width + enemy.rect.width)/2

        if distance_squared < (combined_radius**2):
            return True
    return False

#Sets the player position back to the center of the screen, clears all enemies, resets gun
def restart():
    enemy_group.empty()
    blood_splat_group.empty()
    player.sprite.reset()

#Display score using score_manager, I could maybe put this inside of Score
def display_score():
    score_surf = score_font.render(f'Score: {score_manager.get_score()}',False, (64,64,64))
    score_rect = score_surf.get_rect(center = (SCREEN_WIDTH//2,20))
    screen.blit(score_surf,score_rect)

#Function to handle inverting the color for the play button. Could create a Menu class to handle this and stuff
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
game_state = 'render' #This is simply to avoid a bug where if you click "play" on the first frame,

#Groups
#Player GroupSingle
player = pygame.sprite.GroupSingle()
player.add(Player())

#Gun GroupSingle
#Is this even necessary? Player already inherits Gun or whatever.
#Idk this may be why the bullet count does not display properly. game still works functionally ¯\_(ツ)_/¯
gun = pygame.sprite.GroupSingle()
gun.add(Gun(player))

#Enemy Group
enemy_group = pygame.sprite.Group()

#Blood splat group
blood_splat_group = pygame.sprite.Group()

#Menu Cats Group (the cats that fall down the screen in the start)
menu_cats_group = pygame.sprite.Group()

#Create instance of Score class to handle the score
score_manager = Score()

#Initialize fonts
gameover_font = pygame.font.Font('font/Pixeltype.ttf', 150)
message_font = pygame.font.Font('font/Pixeltype.ttf', 100)
score_font = pygame.font.Font('font/Pixeltype.ttf', 50)

#Sounds and Songs
pygame.mixer.init()

punch_sound = pygame.mixer.Sound('audio/punch.mp3')
splat_sound = pygame.mixer.Sound('audio/splat.mp3')

#Just keeping this here to easily access the song names
#songs.append(pygame.mixer.Sound('audio/songs/1. Miniature Fantasy - Platform Racing Two Cast.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/2. Paradise On E - Parker Brothers and Andrea Prairie-Isochromatic.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/3. Crying Soul - Andrew Dreamscaper Parker, Bounce Parker.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/4. My Vision - Tom Maestro.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/5. Switchblade - Katie Reasoner and Sandy Kenny Alzini Parker.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/6. The Wires - Katie Reasoner, Andrew Dreamscaper Parker and Cheez Ratnam Usina.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/7. Before Mydnite - Tom Maestro and Failand Ratnam.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/8. Broked It - Sally Whitney Touch.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/9. Hello - Tom Montegmory Martin.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/10. Pyrokinesis - Katie Reasoner, Tom Montegmory Martin and Sean Tucker.mp3'))
#songs.append(pygame.mixer.Sound('audio/songs/11. Flowerz n Herbz - Tom Montegmory Martin and Brunalle Brunzolaitis.mp3'))

#Load and play menu song 
pygame.mixer.music.load('audio/songs/9. Hello - Tom Montegmory Martin.mp3')
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play()

#colors used for menu background rgb
colors = [0,0,0]

#Game loop
while True:
    #Event handlers
    for event in pygame.event.get():
        #Quit if they press the x on the top right
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        #Checks enemy timers during gameplay to spawn them
        if game_state == 'gameplay':
            if event.type == bork_timer:
                enemy_group.add(Enemy('bork'))
            elif event.type == zoomer_timer:
                enemy_group.add(Enemy('zoomer'))
        #Menu logic
        if game_state == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #Checks if you click the play button
                if play_button_rect.collidepoint(event.pos):
                    game_state = 'gameplay'
                    punch_sound.play()
                    pygame.mixer.music.load('audio/songs/5. Switchblade - Katie Reasoner and Sandy Kenny Alzini Parker.mp3')
                    pygame.mixer.music.play()
                    #Handles restarting the game, clears score and gets rid of the menu cats (could clean this up into one method or something)
                    restart()
                    score_manager.restart()
                    menu_cats_group.empty()
            #Add a menu cat if the timer goes off
            if event.type == menu_cat_timer:
                menu_cats_group.add(MenuCat())
        #Game over screen logic
        if game_state == 'gameover':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_button_rect.collidepoint(event.pos):
                    game_state = 'menu'
                    punch_sound.play()
                    pygame.mixer.music.load('audio/songs/9. Hello - Tom Montegmory Martin.mp3')
                    pygame.mixer.music.play()
    
    #Game logic
    if game_state == 'gameplay':
        #Draw background
        screen.blit(background_surf, (0,0))

        #Update blood splats
        for splat in blood_splat_group:
            splat.update()
        blood_splat_group.draw(screen)

        #Draw and update player sprite
        player.draw(screen)
        player.update()

        #Draw and update Gun (might be redundant, player inherits gun or something)
        gun.draw(screen)
        gun.update()

        #Update all enemies in enemy_group
        for enemy in enemy_group:
            enemy.update()

        #Draw enemy_group
        enemy_group.draw(screen)

        #Draw the score
        display_score()

        #Check for collision between player and enemies
        if collision_player_enemy():
            death_time = pygame.time.get_ticks()
            #uses 'death' and not 'gameover' to avoid a bug where clicking play on the first frame crashes
            game_state = 'death'
            splat_sound.play()
            pygame.mixer.music.fadeout(500)

    #Menu screen logic
    elif game_state =='menu' or game_state == 'render':
        screen.fill((colors[0],colors[1],colors[2]))
        for cat in menu_cats_group:
            cat.update()

        menu_cats_group.draw(screen)
        title_message = gameover_font.render(f'cat with a gun', False,'Black')
        title_message_rect = title_message.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//6))
        screen.blit(title_message, title_message_rect)

        x = pygame.time.get_ticks()//7.5
        
        #Makes the rgb values change sinusoidally relative to the time. this can be represented by https://www.desmos.com/calculator/xddjgp28yz
        #This could be cleaned up and improved alot, instead of checking each value of i I could set each value
        #of colors to be equally far apart and apply the same function to each color. This could also be in a method
        #or could be moved up
        for i in range(len(colors)):
            if i == 0:
                colors[i] = (math.sin((x/255)*255) +255)/2
            elif i == 1:
                colors[i] = (math.sin((x / 255) + 2 * math.pi * (2 / 3)) * 255 + 255) / 2
            elif i == 2:
                colors[i] = (math.sin((x / 255) + 2 * math.pi * (1 / 3)) * 255 + 255) / 2
        
        play_message = message_font.render(f'PLAY', False,'Black')
        play_message_rect = play_message.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        scaled_surf = pygame.transform.scale_by(play_message, 1.2)
        play_button_rect = scaled_surf.get_rect(center = (SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
        pygame.draw.rect(screen,color_invert(colors),play_button_rect,border_radius= 20) #inverts the background color to get the play button color
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

        #High score logic
        if score_manager.is_high_score():
            high_score_text = message_font.render(f'High score!', False, 'Blue')
        else: 
            high_score_text = message_font.render(f'High Score: {score_manager.get_high_score()}', False, 'Blue')
        high_score_text_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2,1.5*SCREEN_HEIGHT//2))
        screen.blit(high_score_text, high_score_text_rect)

        game_state = 'gameover'


        #If player presses any key to restart gameplay
        if any(pygame.key.get_pressed()) and pygame.time.get_ticks() > death_time + restart_delay:
            game_state = 'gameplay'
            restart()
            score_manager.restart()
            pygame.mixer.music.play()
        
    pygame.display.update()
    clock.tick(60) #framerate = 60