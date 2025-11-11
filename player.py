"""
Player module for Trapper-Mastering game.
Manages player inventory, party, and items.
"""

from creature import Creature


class Item:
    """Represents an item in the game"""
    
    def __init__(self, name, description, effect_type):
        self.name = name
        self.description = description
        self.effect_type = effect_type  # 'trap', 'heal', 'boost', etc.


class Trap(Item):
    """
    Traps used to catch creatures (similar to Pokeballs)
    """
    
    def __init__(self, name, description, catch_rate):
        super().__init__(name, description, 'trap')
        self.catch_rate = catch_rate  # Base catch rate multiplier


class HealItem(Item):
    """Items that heal creatures"""
    
    def __init__(self, name, description, heal_amount):
        super().__init__(name, description, 'heal')
        self.heal_amount = heal_amount


# Predefined traps (similar to different Pokeball types)
TRAP_TYPES = {
    "Basic Trap": Trap("Basic Trap", "A basic trap for catching creatures.", 1.0),
    "Super Trap": Trap("Super Trap", "A better trap with higher success rate.", 1.5),
    "Ultra Trap": Trap("Ultra Trap", "The best trap available!", 2.0),
}

# Predefined heal items
HEAL_ITEMS = {
    "Potion": HealItem("Potion", "Restores 20 HP", 20),
    "Super Potion": HealItem("Super Potion", "Restores 50 HP", 50),
}


class Player:
    """
    Represents the player character
    """
    
    def __init__(self, name):
        self.name = name
        self.party = []  # List of creatures in party (max 6)
        self.pc_box = []  # Stored creatures
        self.inventory = {
            "Basic Trap": 10,
            "Potion": 5,
        }
        self.money = 1000
        
    def add_creature(self, creature):
        """Add a creature to party or PC"""
        if len(self.party) < 6:
            self.party.append(creature)
            return True
        else:
            self.pc_box.append(creature)
            return False
    
    def get_active_creature(self):
        """Get the first non-fainted creature in party"""
        for creature in self.party:
            if not creature.is_fainted():
                return creature
        return None
    
    def has_usable_creatures(self):
        """Check if player has any non-fainted creatures"""
        return any(not c.is_fainted() for c in self.party)
    
    def add_item(self, item_name, quantity=1):
        """Add item to inventory"""
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
    
    def use_item(self, item_name):
        """Use an item from inventory"""
        if item_name in self.inventory and self.inventory[item_name] > 0:
            self.inventory[item_name] -= 1
            if self.inventory[item_name] == 0:
                del self.inventory[item_name]
            return True
        return False
    
    def get_item_count(self, item_name):
        """Get count of specific item"""
        return self.inventory.get(item_name, 0)
    
    def heal_all_creatures(self):
        """Heal all creatures in party"""
        for creature in self.party:
            creature.full_heal()
