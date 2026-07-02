from entities.buildings.base_building import ProductionBuilding


class Barracks(ProductionBuilding):
    COST = 50
    UNITS = {
        "Warrior": 15.0,   # segundos para treinar
        "Archer":  15.0,
    }

    def __init__(self, position, economy, id):
        super().__init__(
            name="Barracks",
            hp=500,
            position=position,
            production_cost=self.COST,
            economy=economy,
            id=id
        )

        # upgrade configuration
        self.min_level = 1
        self.max_level = 2
        # units that require a higher building level
        self.MIN_LEVEL = {
            "Warrior": 1,
            "Archer": 2,
        }
        self.upgrade_cost = 100
        self.upgrade_time = 15.0

    

    def train_warrior(self): return self.train("Warrior", self.UNITS["Warrior"])
    def train_archer(self):  return self.train("Archer",  self.UNITS["Archer"])

    def get_menu_buttons(self):
        base = super().get_menu_buttons()
        return [
            {"label": "Warrior (W)", "action": self.train_warrior},
            {"label": "Archer (A)", "action": self.train_archer},
            *base,
        ]
