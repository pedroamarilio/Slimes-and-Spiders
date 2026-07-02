from entities.buildings.base_building import ProductionBuilding


class Tower(ProductionBuilding):
	COST = 100
	UNITS = {
		"Necromancer": 15.0,
		"Healer": 10.0,
	}

	def __init__(self, position, economy=None, id=None):
		# use the ProductionBuilding constructor to get queue/economy behavior
		super().__init__(
			name="Tower",
			hp=800,
			position=position,
			production_cost=self.COST,
			economy=economy,
			id=id,
			image="assets/sprites/tower.png",
		)
		self.exists = True

		# upgrade configuration
		self.min_level = 1
		self.max_level = 2
		self.MIN_LEVEL = {
			"Healer": 1,
			"Necromancer": 2,
		}
		self.upgrade_cost = 150
		self.upgrade_time = 15.0

	def train_necromancer(self):
		return self.train("Necromancer", self.UNITS["Necromancer"])

	def train_healer(self):
		return self.train("Healer", self.UNITS["Healer"])

	def get_menu_buttons(self):
		base = super().get_menu_buttons()
		return [
			{"label": "Necromancer (N)", "action": self.train_necromancer},
			{"label": "Healer (H)", "action": self.train_healer},
			*base,
		]

	# placeholder for tower behavior
	def attack(self, target):
		pass
