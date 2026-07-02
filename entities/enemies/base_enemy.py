from entities.base_living import BaseLiving

class BaseEnemy(BaseLiving):
    def __init__(self, imagem, x, y, animated=False, sprites=1):
        super().__init__(imagem, x, y, animated, sprites)