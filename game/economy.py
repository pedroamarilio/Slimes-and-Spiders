import assets

class Change:
    def __init__(self, amount, entity_string, position):
        self.id = 0
        self.amount = amount
        self.entity_string = entity_string
        self.position = position

class ChangeManager:
    def __init__(self):
        self.toInitialize = []
        self.change_id = 0
        self.changes = {}
        self.approved = {}

    def initialize(self):
        if not self.toInitialize:
            return [], {}

        changes = []
        approved = {}
        for change in self.toInitialize:
            change.id = self.change_id
            self.change_id += 1
            changes.append(change)
            approved[change.id] = False

        self.toInitialize.clear()
        return changes, approved


class Economy:
    def __init__(self):
        # start game with zero resources by default
        self.resources = 0
        self.army = 0
        self.campfires = 0

    @property
    def army_max(self):
        return 100 + (25 * self.campfires)

    def update(self, changes, approved):
        for change in changes:

            print(change.amount)

            if change.amount > 0:
                self.add_resources(change.amount)
                approved[change.id] = True
            else:
                approved[change.id] = self.spend_resources(-change.amount)

    def add_resources(self, amount):
        self.resources += amount

    def spend_resources(self, amount):
        if self.resources >= amount:
            self.resources -= amount
            return True
        return False