import pygame as py
import sys
from random import randint, choice
from abc import ABC, abstractmethod

class Player:
    def __init__(self,x,width,height,speed):
        self._sprite = player_model_image
        self._sprite = py.transform.scale(self.sprite,(width,height))
        self._x = x
        self.y = 600
        self.width = width
        self.height = height
        self.speed = speed
        self.rect = self.sprite.get_rect(topleft=(self.x,self.y))
    
    def draw(self):
        py.draw.rect(screen,(0,0,0),self.rect)
        screen.blit(self.sprite,self.rect)
    
    def change_size(self,multiplier):
        self.width *= multiplier
        self.height *= multiplier
        self._sprite = py.transform.scale(self.sprite,(self.width,self.height))
        self.rect = self.sprite.get_rect(topleft=(self.x,self.y))
    
    @property
    def sprite(self):
        return self._sprite
    @sprite.setter
    def sprite(self,new_sprite):
        self._sprite = py.transform.scale(new_sprite,(self.width,self.height))

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self,x):
        if type(x) is int:
            if x > 0 and x <= 800-self.width:
                self._x = x
        self.rect = py.Rect(self.x,self.y-self.height,self.width,self.height)

class Block:
    def __init__(self,x,speed,size):
        self.sprite = box_model_image
        self.sprite = py.transform.scale(self.sprite,(size,size))
        self.x = x
        self.y = 0
        self.speed = speed
        self.size = size
        self.rect = self.sprite.get_rect(topleft=(self.x,self.y))
        self.rect.width, self.rect.height = self.size, self.size

    def update(self):
        self.y += self.speed
        self.rect = self.sprite.get_rect(topleft=(self.x,self.y))
        self.rect.width,self.rect.height = self.size,self.size

    def draw(self):
        py.draw.rect(screen,(0,0,0),self.rect)
        screen.blit(self.sprite,self.rect)

class PowerUp(Block,ABC): # Inherits Block for it's movement behavior.
    def __init__(self,x,speed,size,image):
        super().__init__(x,speed,size)
        self.sprite = image
        self.sprite = py.transform.scale(self.sprite,(size,size))
    @abstractmethod
    def power_up(self,player):
        """Implemented by other classes"""
        pass

class SpeedPowerUp(PowerUp):
    def power_up(self,player):
        player.speed += 2

class SpeedPowerDown(PowerUp):
    def power_up(self,player):
        player.speed -= 2

class SizePowerUp(PowerUp):
    def power_up(self,player):
        player.change_size(1.5)
    
class SizePowerDown(PowerUp):
    def power_up(self,player):
        player.change_size(2 / 3)

class ScorePowerUp(PowerUp):
    def power_up(self,_):
        global score
        score += 5

py.init()

WIDTH, HEIGHT = 800,600
screen = py.display.set_mode((WIDTH,HEIGHT))
py.display.set_caption('Dodge the boxes')

clock = py.time.Clock()
FPS = 60

box_model_image = py.image.load('Box.png').convert_alpha()

player_model_image = py.image.load('player.png').convert_alpha()
dead_player_image = py.image.load('playerdead.png').convert_alpha()

def game(started=False):
    global score
    global power_image
    player = Player(400,100,50,5)

    power_ups = [SpeedPowerUp,SpeedPowerDown,SizePowerUp,SizePowerDown,ScorePowerUp]
    power_image = {SpeedPowerUp:py.image.load('speedupgrade.png').convert_alpha(),SpeedPowerDown:py.image.load('speeddowngrade.png').convert_alpha(),SizePowerUp:py.image.load('sizeupgrade.png').convert_alpha(),SizePowerDown:py.image.load('sizedowngrade.png').convert_alpha(),ScorePowerUp:py.image.load('pointupgrade.png').convert_alpha()}

    active_power_ups = []

    blocks: list[Block] = []
    spawn_timer = 0
    spawn_delay = 30
    score_timer = 0
    score_delay = 60
    score = 0
    game_over = False
    render_count =  0

    power_up_delay = 600
    power_up_timer = 0

    font = py.font.SysFont(None,36)

    running = True

    while running:
        clock.tick(FPS)

        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
                py.quit()
                sys.exit()
            if event.type == py.KEYDOWN:
                if (event.key == py.K_RETURN or event.key == py.K_KP_ENTER) and game_over:
                    game(True)
                    break
                if not started:
                    started = True
        

        if not game_over and started:
            keys = py.key.get_pressed()
            if keys[py.K_LEFT]:
                player.x -= player.speed
            elif keys[py.K_RIGHT]:
                player.x += player.speed

            spawn_timer += 1
            if spawn_timer >= spawn_delay:
                blocks.append(Block(randint(0,600),randint(1,10),randint(25,75)))
                spawn_timer = 0

            score_timer += 1
            if score_timer >= score_delay:
                score += 1
                score_timer = 0

            screen.fill((200,179,162))
            for block in blocks:
                block.update()
                block.draw()
                if player.rect.colliderect(block.rect):
                    player.sprite = dead_player_image
                    player.draw()
                    game_over = True

            power_up_timer += 1
            if power_up_timer >= power_up_delay:
                next_power = choice(power_ups)
                active_power_ups.append(next_power(randint(0,600),randint(1,10),50,power_image[next_power]))
                power_up_timer = 0
            
            for power_up in active_power_ups:
                power_up.update()
                power_up.draw()
                if player.rect.colliderect(power_up.rect):
                    power_up.power_up(player)
                    active_power_ups.remove(power_up)
            active_power_ups = [pu for pu in active_power_ups if pu.y < 600]

            blocks = [b for b in blocks if b.y < 600]

            player.draw()

            score_text = font.render(f'Score: {score}',True,(255,255,255),(150,75,0))

            screen.blit(score_text,(50,50))

        elif game_over and started:
            if render_count == 0:
                player_loss = font.render('You lost!',True,(255,255,255))
                
                end_score_text = font.render(f'Score: {score}',True,(255,255,255))

                play_again = font.render('Press Enter to play again', True, (255,255,255))

                screen.blit(player_loss,(300,50))
                screen.blit(end_score_text,(300,150))
                screen.blit(play_again,(300,250))
                render_count += 1
        else:
            screen.fill((200,179,162))
            title = font.render('Dodge The Blocks!',True,(255,255,255),(150,75,0))
            screen.blit(title,(275,100))
            start_text = font.render('Press any key to start',True,(255,255,255),(150,75,0))
            screen.blit(start_text,(275,200))

            tutorial = font.render('Press the arrow keys to move. Avoid the boxes!',True,(255,255,255),(150,75,0))
            tutorial0 = font.render('Touch power ups to use them! The power ups are as following:',True,(255,255,255),(150,75,0))
            power_up_explanations = ['Speed Increase: Increases the player\'s speed.','Speed Decrease: Decreases the player\'s speed.','Size Increase: Increases the player\'s size.','Size Decrease: Decreases the player\'s size.','Point Increase: Gives the player 5 points.']
            screen.blit(tutorial,(0,300))
            screen.blit(tutorial0,(0,325))
            value = 350
            for explanation in power_up_explanations:
                rendered = font.render(explanation,True,(255,255,255),(150,75,0))
                screen.blit(rendered,(0,value))
                value += 25
        
        py.display.flip()

game()
