import pygame as pg
import random
import math

WIDTH = 600
HEIGHT = 800
FPS = 60

# colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128,128,128)
BLUE = (0,0,255)

# initialize pygame and create window
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Robot game")
clock = pg.time.Clock()

# load images
robot_img = pg.image.load("robo.png")
ghost_img = pg.image.load("hirvio.png")
coin_img = pg.image.load("kolikko.png")

class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = robot_img
        self.rect = self.image.get_rect()
        pg.sprite.collide_rect_ratio(0.5)
        #pg.draw.rect(self.image,RED,self.rect)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT
        self.speedx = 0
        self.shoot_delay = 333
        self.last_shot = pg.time.get_ticks()
        self.lives = 5
        self.invuln = False
        self.invuln_timer = pg.time.get_ticks()
    
    def update(self):
        # kbm controls
        # movement
        self.speedx = 0
        keystate = pg.key.get_pressed()
        if keystate[pg.K_a]: self.speedx = -4
        if keystate[pg.K_d]: self.speedx = 4
        # shooting
        mousestate = pg.mouse.get_pressed()[0]
        if mousestate: self.shoot()
        
        self.rect.x += self.speedx
        
        # invuln timer when hit
        if self.invuln and pg.time.get_ticks() - self.invuln_timer > 2000:
            self.invuln = False
        
        # stay on screen
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.left < 0: self.rect.left = 0
        
    def shoot(self): 
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx,self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
    
    def take_damage(self):
        self.lives -= 1
        self.invuln = True
        self.invuln_timer = pg.time.get_ticks()        

class Bullet(pg.sprite.Sprite):
    def __init__(self,x,y):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((10,10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = 10
        # shoot to mouse position
        self.pos = (x, y)
        mx,my = pg.mouse.get_pos()
        self.dir = (mx-x, my-y)
        length = math.hypot(*self.dir)
        if length == 0.0:
            self.dir = (0,-1)
        else:
            self.dir = (self.dir[0]/length,self.dir[1]/length)
    
    def update(self):        
        self.pos = (self.pos[0]+self.dir[0]*self.speed,
                    self.pos[1]+self.dir[1]*self.speed)
        self.rect = self.image.get_rect(center = self.pos)
        if self.rect.bottom < 0: self.kill()
        if self.rect.left > WIDTH: self.kill()
        if self.rect.right < 0: self.kill()

class Ghost(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = ghost_img
        self.rect = self.image.get_rect()
        pg.sprite.collide_rect_ratio(0.6)
        self.rect.x = random.randrange(0,WIDTH-self.rect.width)
        self.rect.y = random.randrange(-100,-40)
        self.speedy = random.randrange(1,2) + difficulty//2
        self.speedx = random.randrange(-2,2) + difficulty//2
        self.loaded = True
        
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.bottom in range(100,150) and self.loaded:
            self.shoot()
            self.loaded = False
                
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx *= -1
        if self.rect.bottom > HEIGHT:
            self.kill()
            new_enemy()
    
    def shoot(self):
        bullet = Ghostbullet(self.rect.centerx,self.rect.bottom,self.speedy * 2)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)

class Ghostbullet(pg.sprite.Sprite):
    def __init__(self,x,y,spd):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((10,10))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = spd
        
    def update(self):
        self.rect.y += self.speedy 
      
class Coin(pg.sprite.Sprite):
    def __init__(self,center):
        pg.sprite.Sprite.__init__(self)
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy 
        if self.rect.top > HEIGHT: self.kill()

def new_enemy():
    g = Ghost()
    all_sprites.add(g)
    enemies.add(g)
    
def draw_text(surf, text, size, x, y,color=BLACK):
    font = pg.font.SysFont("Arial",size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_lives(surf, x, y, lives):
    for i in range(lives):
        pg.draw.rect(surf,GREEN,(x+20*i,y,15,15))

def start_screen():
    global running
    screen.fill(GRAY)
    draw_text(screen, "ROBOT GAME", 60, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "a/d keys to move, click to shoot", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press any key to start", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pg.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                waiting = False
            if event.type == pg.KEYUP: waiting = False
            
def game_over():
    global game_start
    global running
    screen.fill(GRAY)
    draw_text(screen, "GAME OVER", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, f"Score: {score}", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "F2 to start new game", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pg.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                running = False
                waiting = False
            if event.type == pg.KEYUP:
                if event.key == pg.K_F2:                
                    game_start = True
                    waiting = False

# start values
mousex = WIDTH / 2
mousey = HEIGHT / 2
score = 0
difficulty = 1
running = True
game_start = True

# game loop
while running:
    clock.tick(FPS)
    # events
    for event in pg.event.get():
        if event.type == pg.QUIT: running = False
        if event.type == pg.MOUSEMOTION:
            mousex = event.pos[0]
            mousey = event.pos[1]

    if game_start:
        start_screen()
        score = 0
        difficulty = 1
        # create sprite groups
        all_sprites = pg.sprite.Group()
        coins = pg.sprite.Group()
        enemies = pg.sprite.Group()
        bullets = pg.sprite.Group()
        enemy_bullets = pg.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(5):
            new_enemy()
        game_start = False
         
    # update
    all_sprites.update()

    # check collisions        
    # player bullet hits enemy
    hits = pg.sprite.groupcollide(bullets,enemies,True,True)
    for hit in hits:
        score += 1
        # chance to spawn coin
        if random.random() > 0.75:
            coin = Coin(hit.rect.center)
            all_sprites.add(coin)
            coins.add(coin)
        new_enemy()
    
    # player hits coin
    hits = pg.sprite.spritecollide(player,coins,True)
    for hit in hits:
        score += 10

    # enemy hits player
    hits = pg.sprite.spritecollide(player,enemies,True)
    if hits:
        if not player.invuln: player.take_damage()
        new_enemy()

    # enemy bullet hits player
    hits = pg.sprite.spritecollide(player,enemy_bullets, True)
    for hit in hits:
        if not player.invuln: player.take_damage()
        
    # spawn new enemy every 50 points
    if score > difficulty * 50:
        new_enemy()
        difficulty += 1
    
    # game over 
    if player.lives <= 0: game_over()
    
    # draw / render
    screen.fill(GRAY)
    all_sprites.draw(screen)
    # draw score
    draw_text(screen, str(score), 20, WIDTH/2, 15)
    # draw lives
    draw_lives(screen,5,5,player.lives)
    # draw aim line
    pg.draw.line(screen, (RED), (player.rect.centerx,player.rect.top), (mousex, mousey), 1)
    # draw damage text
    if player.invuln: draw_text(screen, "DAMAGE", 30, WIDTH / 2, HEIGHT / 3, RED)
    
    # after drawing everything, flip the display
    pg.display.flip()

pg.quit()