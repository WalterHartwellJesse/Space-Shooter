import pygame
from os.path import join
from random import randint , uniform
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images' , 'player.png' ,)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 200))
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2 , WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        #Cooldown
        self.can_shoot =  True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

    def laser_timer(self):
        if not self.can_shoot:
            current_time =  pygame.time.get_ticks()
            if current_time- self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self , dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        recent_keys = pygame.key.get_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(player_wep , self.rect.midtop , (all_sprites , Laser_sprites))
            self.can_shoot = False
            laser_sound.play()
            self.laser_shoot_time = pygame.time.get_ticks()
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(Star , Groups , surf):
        super().__init__(Groups)
        Star.image = star_surf
        Star.rect = star_surf.get_frect(center = (randint(0 , WINDOW_WIDTH),randint (0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self ,surf , pos , groups):
        super().__init__(groups)
        self.image = surf
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_frect(midbottom = pos)
    def update(self , dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, pos,surf,  groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.dir = pygame.Vector2(uniform(-0.5,0.5) ,1)
        self.speed = randint(400,500)
    def update(self, dt):
        self.rect.center += self.dir * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
    
def collision():
    global running  
    meteor_player_collision = pygame.sprite.spritecollide(player ,Meteor_sprites , True , pygame.sprite.collide_mask)
    if meteor_player_collision:
        explosion_sound.play()
        AnimatedExplosion(explosion_frames,  meteor_player_collision[0].rect.center, all_sprites)
        running = False
    for laser in Laser_sprites:
        meteor_laser_collision = pygame.sprite.spritecollide(laser , Meteor_sprites , True)
        if meteor_laser_collision:
            explosion_sound.play()
            AnimatedExplosion(explosion_frames, meteor_laser_collision[0].rect.center, all_sprites)
            laser.kill()

def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True,'#f5f5f5')
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2 , WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf,text_rect)
    pygame.draw.rect(display_surface , (240 , 240 , 240) ,text_rect.inflate(30 , 40).move(0 , -5) , 7 , 10)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self,frames , pos , groups):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_frect(center = pos)
    def update(self , dt):
        self.frames_index += 20 * dt
        if self.frames_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frames_index) % len(self.frames)]

#General setup
clock = pygame.time.Clock()
pygame.init()
WINDOW_WIDTH,WINDOW_HEIGHT =  1280 , 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
running = True
pygame.display.set_caption("SpacePewPew")

#Plain surface
surf = pygame.Surface((100,200))
surf.fill("aquamarine3")
x = 400
speed = 300
star_surf =  pygame.image.load(join('images', 'star.png')).convert_alpha()

#Sprites
all_sprites = pygame.sprite.Group()
Meteor_sprites = pygame.sprite.Group()
Laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites,star_surf)
player = Player(all_sprites)

#Import your images
meteor = pygame.image.load(join('images' , 'meteor.png')).convert_alpha()
player_wep = pygame.image.load(join('images' , 'laser.png'))
font = pygame.font.Font(join('images' ,'Oxanium-Bold.ttf') , 30)
explosion_frames = [pygame.image.load(join('images' ,'explosion' , f'{i}.png')).convert_alpha() for i in range(21)]

#Import Sounds
laser_sound = pygame.mixer.Sound(join('audio' ,'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio' , 'explosion.wav'))
game_music =  pygame.mixer.Sound(join('audio' , 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops= -1)

#Positions for each images
player_wep_rect = player_wep.get_frect(bottomleft = (20 , WINDOW_HEIGHT + 20) )

#custom events 
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)
while running:
    dt = clock.tick() / 1000
    #Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x , y = randint(0 , WINDOW_WIDTH) , randint(-200 ,-100)
            Meteor((x , y) , meteor , (all_sprites , Meteor_sprites))
    #UPDATING
    all_sprites.update(dt)
    collision()
    #Draw the game
    display_surface.fill("#526958")
    all_sprites.draw(display_surface)
    display_score()
    pygame.display.update()

    #Test collisions



pygame.quit()
