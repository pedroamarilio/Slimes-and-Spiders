from entities.buildings.base_building import ProductionBuilding


class Incubator(ProductionBuilding):
    COST = 700
    UNITS = {
        "Slime": 15.0,
        "Dragon": 30.0,
    }

    def __init__(self, position, economy=None, id=None):
        super().__init__(
            name="Incubator",
            hp=500,
            position=position,
            production_cost=self.COST,
            economy=economy,
            id=id,
            image="assets/sprites/incubator.png",
        )
        self.exists = True
        # upgrade configuration
        self.min_level = 1
        self.max_level = 2
        self.MIN_LEVEL = {
            "Slime": 1,
            "Dragon": 2,
        }
        self.upgrade_cost = 200
        self.upgrade_time = 15.0

    def train_slime(self):
        return self.train("Slime", self.UNITS["Slime"])

    def train_dragon(self):
        return self.train("Dragon", self.UNITS["Dragon"])

    def get_menu_buttons(self):
        base = super().get_menu_buttons()
        return [
            {"label": "Slime (S)", "action": self.train_slime},
            {"label": "Dragon (D)", "action": self.train_dragon},
            *base,
        ]
