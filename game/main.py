import pygame as pg
import random
import math
from pygame.locals import *
from pygame import mixer
import os
from os import path
from settings import *
from sprites import *
from dotenv import load_dotenv
from twilio.rest import Client
import pytest


pg.mixer.pre_init(44100,16,2,4096) #initialize sound capabilities of pygame
pg.init()

#Set pygame screen size
display_screen = pg.display.set_mode((WIDTH, HEIGHT))

#Enemy Fireball Timer
enemy1_shoot_event = pg.USEREVENT +1
pg.time.set_timer(enemy1_shoot_event,3000)


class Game:
    """
    Creates the game class to run the game.
    """
    def __init__(self):
        """
        Initializes (sets up) the game class.
        
        Parameters: 
        
            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        
        Source: YouTube Videos KidsCanCode provided information needed for initial setup of code, though code was majorly altered to tailor to project
        
        Source Link: https://www.youtube.com/watch?v=uWvb3QzA48c
        """
        # initialiaze game window, etc.
        self.running = True
        pg.init()
        pg.mixer.init()
        #display_screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
         
    def new(self):
        """
        Starts a new pygame window.
        
        Parameters: 
        
            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        
        Source: YouTube Videos KidsCanCode provided information needed for initial setup of code, though code was majorly altered to tailor to project
        
        Source Link: https://www.youtube.com/watch?v=uWvb3QzA48c
        """
        # start a new game
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.arrows = pg.sprite.Group()
        self.fireballs = pg.sprite.Group()
        self.player = Player(self, 'archer.png')
        self.all_sprites.add(self.player)
        self.enemy1 = Enemy(720, 655, 'wizard.png')
        self.enemy2 = Enemy(WIDTH - 100, HEIGHT - 420, 'wizard.png')
        self.enemy3 = Enemy(WIDTH - 150, HEIGHT - 600, 'wizard.png')
        self.all_sprites.add(self.enemy1, self.enemy2, self.enemy3) 
        self.enemies.add(self.enemy1, self.enemy2, self.enemy3)
        self.previous_time = pg.time.get_ticks()
        self.HP_prev = self.player.health
        
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
      
        self.run()
        
    def run(self):
        """
        Creates the game loop.
        
        Parameters: 
        
            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        
        Source: YouTube Videos KidsCanCode provided information needed for initial setup of code, though code was majorly altered to tailor to project
        
        Source Link: https://www.youtube.com/watch?v=uWvb3QzA48c
        """
        # game loop
        
        self.playing = True
        
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        """
        Method to control sprite's behavior (impact of collisions).
       
        Parameters: 
        
            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        
        Source: YouTube Videos KidsCanCode provided information needed for initial setup of code, though code was majorly altered to tailor to project
        
        Source Link: https://www.youtube.com/watch?v=uWvb3QzA48c     
        """ 
        # game loop -- updates
        self.all_sprites.update()

        if len(self.enemies) == 0:
            self.playing = False 

        #check if player hits platform if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False,)
        
            if hits:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0
                self.player.acc.y = 0        

        hits = pg.sprite.groupcollide(self.enemies, self.arrows, False, True)
        for hit in hits:
            hit.health -= ARROW_DAMAGE
            if hit.health <= 0:
                self.enemies.remove(hit)
            arrow_sound = pg.mixer.Sound('game\sounds\get_hit.ogg')
            pg.mixer.Sound.play(arrow_sound)

        hits = pg.sprite.groupcollide(self.platforms, self.arrows, False, True)
        for hit in hits:
            hit.acc = (0,0)
            hit.vel = (0,0)

        hits = pg.sprite.spritecollide(self.player, self.fireballs, True,  pg.sprite.collide_circle)
        if hits:
            fire_sound = pg.mixer.Sound('game\sounds\enemyhit.ogg')
            pg.mixer.Sound.play(fire_sound)
            self.fireballs.acc = 0
            self.fireballs.vel = 0
            self.player.health -= FIREBALL_DAMAGE
            self.HP_prev = self.player.health + FIREBALL_DAMAGE

       
        if self.player.health <= 0:
            self.playing = False
       
    def events(self):
        """
        Creates the events loop to allow for actions to occur in the pygame window.
       
        Parameters: 
           
            self (self):  keyword we can access the attributes and methods 
            of the class in python 
       
        Source: YouTube Videos KidsCanCode provided information needed for initial setup of code, though code was majorly altered to tailor to project
       
        Source Link: https://www.youtube.com/watch?v=uWvb3QzA48c
        """
        # game loop -- events      
        for event in pg.event.get():

            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                    self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP: #action of player to jump if up key is pressed
                    self.player.jump()
                if event.key == pg.K_SPACE: #action of player to shoot if spacebar is pressed
                    self.current_time = pg.time.get_ticks()
                    if self.current_time - self.previous_time > SHOT_TIME:   
                        self.previous_time = self.current_time
                        self.fire()

            
            if event.type == enemy1_shoot_event:
                self.shoot_fire()
            
    def draw(self):
        """
        Function that allows for the creation of items on the pygame screen.

        Parameters: 

            self (self):  keyword we can access the attributes and methods 
            of the class in python 
       
        Source: YouTube Videos KidsCanCode provided information needed for initial setup of code, though code was majorly altered to tailor to project
       
        Source Link: https://www.youtube.com/watch?v=uWvb3QzA48c
        """
        # game loop -- draw
 
        self.background_image = pg.image.load("game\images\Forest.jpg").convert_alpha()
        self.screen.blit(self.background_image, [0, 0])
        self.all_sprites.draw(self.screen)
        
        #Draw healthbar text
        font = pg.font.Font(pg.font.match_font('cambria'),17)
        text = font.render("HP:",20,GREEN)
        display_screen.blit(text,(20,20))

        if self.player.health > 30:
                hb_color = GREEN
        else: hb_color = RED

        pg.draw.rect(display_screen,hb_color,(50,20,self.player.health,20),0)
        pg.display.flip()

        #Health bar
        if self.player.health < self.HP_prev:
            pg.draw.rect(display_screen,hb_color,(50,20,self.player.health,20),0)
            pg.display.flip()

       # Mob heath
        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy):
                sprite.draw_health()

    def fire(self):
        """
        Used to fire arrows from the player.

        Parameters: 

            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        """  
        arrow = Arrow(int(self.player.rect.centerx),int(self.player.rect.centery), 'uber_tiny.png')
        self.all_sprites.add(arrow)
        self.arrows.add(arrow)

    def shoot_fire(self):
        """
        Creates the fireballs that enemies shoots.

        Parameters: 

            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        """  
        if self.enemy1.health > 0:
            fire_ball1 = Fireball(int(self.enemy1.rect.centerx + 50),int(self.enemy1.rect.centery), 'Fireball1.png')
            self.radius = 15
            self.all_sprites.add(fire_ball1)
            self.fireballs.add(fire_ball1)

        if self.enemy2.health > 0:
            fire_ball2 = Fireball(int(self.enemy2.rect.centerx + 100),int(self.enemy2.rect.centery), 'Fireball1.png')
            self.radius = 15
            self.all_sprites.add(fire_ball2)
            self.fireballs.add(fire_ball2)

        if self.enemy3.health > 0:
            self.radius = 15
            fire_ball3 = Fireball(int(self.enemy3.rect.centerx + 300),int(self.enemy3.rect.centery), 'Fireball1.png')
            self.all_sprites.add(fire_ball3)
            self.fireballs.add(fire_ball3)
  
    def start_screen(self):
        """
        Function to create start screen on the pygame screen.

        Parameters: 

            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        
        Source: Code help to understand structure of the start screen from https://github.com/joshuawillman/The-Lonely-Shooter
        """  
        img_dir = path.join(path.dirname(__file__), 'images')
        title = pg.image.load(path.join(img_dir, "title_text.png")).convert_alpha()
        title = pg.transform.scale(title, (WIDTH, 165))
        background = pg.image.load('game\images\Home_Screen.jpg').convert_alpha()
        background_rect = background.get_rect()

        arrow_keys = pg.image.load(path.join(img_dir, 'arrow_keys.png')).convert_alpha()
        arrow_keys = pg.transform.scale(arrow_keys, (150, 85))

        spacebar = pg.image.load(path.join(img_dir, 'spacebar1.png')).convert_alpha()
        spacebar = pg.transform.scale(spacebar, (150, 50))

        display_screen.blit(background, background_rect)
        display_screen.blit(title, (0,110))
        display_screen.blit(arrow_keys, (720, 570))
        display_screen.blit(spacebar, (720, 670))

        def draw_text(self, surface, text, size, x, y, color):
            """
            Function to draw text on the the start screen.

            Parameters: 

                self (self): keyword we can access the attributes and 
                methods of the class in python 
                
                surface: identifies the screen on which to draw text

                text (str): Words that are desired to be on the pygame 
                screen

                size (int):  Provides the desired text size of words

                x (int): x coordinate of the text on the screen (changing 
                the coordinate moves the text horizontally)

                y (int): y coordinate of the text on the screen (changing 
                the coordinate moves the text vertically)

                color (preset color code from pygame): Determines the color 
                of the text

            Source: Code help to understand structure of the start screen from https://github.com/joshuawillman/The-Lonely-Shooter
            """  
            font = pg.font.Font(pg.font.match_font('cambria'), size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.midtop = (x, y)
            surface.blit(text_surface, text_rect)

        draw_text(self, display_screen, "Are You Ready for the Challenge?", 35, WIDTH/2, HEIGHT/2, WHITE)
        draw_text(self, display_screen, "If so, press [ENTER] to begin", 35, WIDTH/2, (HEIGHT/2) + 50, WHITE)
        draw_text(self, display_screen, "If not, press [Q] to quit", 35, WIDTH/2, (HEIGHT/2) + 100, WHITE)
        draw_text(self, display_screen, "MOVE:", 35, 630, 570, WHITE)
        draw_text(self, display_screen, "SHOOT:", 35, 630, 670, WHITE)

        #code for playing sound from CrouchingPython on YouTube https://www.youtube.com/watch?v=YQ1mixa9RAw
        pg.mixer.music.load('game\sounds\Destiny.mp3')
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)
        pg.display.update()

        while True:
            event = pg.event.poll()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    break
                elif event.key == pg.K_q:
                    pg.quit()
                    self.running = False
            elif event.type == QUIT:
                pg.quit()

    def end_screen_1(self):
        
        """
        Function to create an end screen after the player wins or loses on the pygame screen.
        
        Parameters:

            self (self): keyword we can access the attributes and methods 
            of the class in python 
        
        """  
        if not self.running:
            return

        background = pg.image.load('game\images\onfiretown.png').convert_alpha()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        rect = background.get_rect()
        display_screen.blit(background, rect)
        font = pg.font.Font(pg.font.match_font('cambria'),75)
        text = font.render("GAME OVER",20,WHITE)
        display_screen.blit(text,(275,150))
        font2 = pg.font.Font(pg.font.match_font('cambria'),25)
        text2 = font2.render("Overwhelmed by the enemy onslaught, you fall in battle.",18,WHITE)
        display_screen.blit(text2,(165,260))
        text3 = font2.render("With nobody left to protect the town, it falls into chaos and ruin.",18,WHITE)
        display_screen.blit(text3,(125,300))
        text4 = font2.render("Press [q] to quit",20,GREEN)
        display_screen.blit(text4,(400,350))
        pg.display.flip()

        while True:
            event = pg.event.poll()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    pg.quit()
                    self.running = False
            elif event.type == QUIT:
                pg.quit()
    
    def end_screen_2(self):
        
        if not self.running:
            return

        background = pg.image.load('game\images\Winner_Screen.jpg').convert_alpha()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        rect = background.get_rect()
        display_screen.blit(background, rect)
        font = pg.font.Font(pg.font.match_font('cambria'),75)
        text = font.render("You are the Champion!",20,WHITE)
        display_screen.blit(text,(120,200))
        font2 = pg.font.Font(pg.font.match_font('cambria'),30)
        text2 = font2.render("With your valient bow and arrow you have defeated the wizards!",23,BLACK)
        display_screen.blit(text2,(30,450))
        text3 = font2.render("Your village is celbrating because it is safe...for now!",23,BLACK)
        display_screen.blit(text3,(100,520))
        text4 = font2.render("Press [q] to quit",20,BLACK)
        display_screen.blit(text4,(400,600))
        pg.display.flip()

        self.send_text()

        while True:
            event = pg.event.poll()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    pg.quit()
                    self.running = False
            elif event.type == QUIT:
                pg.quit()
                    
    def send_text(self):

        """
        Sends text containing game stats to user

        Parameters: 

            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        """ 
    
        load_dotenv()

        TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "OOPS, please specify env var called 'TWILIO_ACCOUNT_SID'")
        TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN", "OOPS, please specify env var called 'TWILIO_AUTH_TOKEN'")
        SENDER_SMS  = os.environ.get("SENDER_SMS", "OOPS, please specify env var called 'SENDER_SMS'")
        RECIPIENT_SMS  = os.environ.get("RECIPIENT_SMS", "OOPS, please specify env var called 'RECIPIENT_SMS'")

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

      
        content = "Thank you so much for playing Champions are Coming. In total, you have been playing for " + self.format_time() + " seconds."
        message = client.messages.create(to = RECIPIENT_SMS, from_ = SENDER_SMS, body = content)
        
    def format_time(self):
        """
        Gets the time pygame has been running and ensures it is the proper format for output (in seconds and 2 decimal points)
        
        Parameters: 

            self (self):  keyword we can access the attributes and methods 
            of the class in python 
        """ 
        time = pg.time.get_ticks()
        time_seconds = str(round((time/1000),2))
        return time_seconds
        
    def scrolling_text(self, screen):
        """
        Function to create a screen with scrolling text similar to the Star Wars Exposition Screen.
        
        Parameters: 
            
            self (self): keyword we can access the attributes and methods 
            of the class in python 
            
            screen: the screen on which the scrolling text should display
        
        Source: https://youtu.be/Vbj-CtchRSI
        """              
        centerx, centery = screen.get_rect().centerx, screen.get_rect().centery
        deltaY = centery + 20 

        #Scrolling Story Text
        rolling_text = '''
        Three evil wizards are about to attack your village! 


        They are currently at the edge of the forest...

        You have time to stop them, but must hurry!


        Will you be the hero and save your village? 

        Or will you let it be burned by the wizards' magic?


        Use the arrow keys to move and jump

        and the spacebar to shoot arrows!


        It is your time to let the wizards know that

        A Champion is Coming to foil their plan!


        Press Enter to Save Your Village
        '''

        running = True



        while True:
            event = pg.event.poll()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    break
            elif event.type == QUIT:
                pg.quit()
                sys.exit() 

            screen.fill(0)

            deltaY -=3 #adjusts speed of text
            msg_list = []
            pos_list = []
            i=0

            #Font and Background
            font = pygame.font.SysFont('cambria',35)
            background = pg.image.load('game\images\parchment.png').convert_alpha()
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
            rect = background.get_rect()
            screen.blit(background, rect)

            for line in rolling_text.split('\n'):
                msg = font.render(line,True, BLACK)
                msg_list.append(msg)

                pos = msg.get_rect(center=(centerx,centery + deltaY + i*30)) 
                pos_list.append(pos)
                i = i+1


            if (centery + deltaY + 30*(len(rolling_text.split('\n'))) < 0):
                running = False


            for j in range(i):
                screen.blit(msg_list[j], pos_list[j])
            pygame.display.update()
        exit


#Run game class

g = Game()
g.start_screen()
g.scrolling_text(display_screen)
while g.running:
    g.new()
    if g.player.health > 0:
        g.end_screen_2()
    if g.player.health <= 0:
        g.end_screen_1()

pg.quit()