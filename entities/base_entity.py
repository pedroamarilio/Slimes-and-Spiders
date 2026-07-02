from PPlay.animation import *
from PPlay.sprite import *

class BaseEntity:
    
    def __init__(self, imagem, x, y, animated=False, sprites=1):

        if animated:
            self.sprite = Animation(imagem, sprites, loop=True)
            self.sprite.set_sequence_time(0, sprites, 100, loop=True)
        else:
            self.sprite = Sprite(imagem)

        self.x = x
        self.y = y
        self.id = 0

        self.speed = 0
        self.hp = 100
        self.max_hp = 100

        self.selected = False
        # facing: 1 = right, -1 = left
        self.facing = 1
 


