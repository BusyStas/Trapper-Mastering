"""
Creature module for Trapper-Mastering game.
Similar to Pokemon in the original games.
"""

import random


class CreatureType:
    """Creature types similar to Pokemon types"""
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"
    ROCK = "Rock"
    GROUND = "Ground"
    FLYING = "Flying"
    ANCIENT = "Ancient"


# Type effectiveness chart (attacker -> defender -> multiplier)
TYPE_EFFECTIVENESS = {
    CreatureType.FIRE: {
        CreatureType.GRASS: 2.0,
        CreatureType.WATER: 0.5,
        CreatureType.FIRE: 0.5,
        CreatureType.ROCK: 0.5,
    },
    CreatureType.WATER: {
        CreatureType.FIRE: 2.0,
        CreatureType.GRASS: 0.5,
        CreatureType.WATER: 0.5,
        CreatureType.GROUND: 2.0,
        CreatureType.ROCK: 2.0,
    },
    CreatureType.GRASS: {
        CreatureType.WATER: 2.0,
        CreatureType.FIRE: 0.5,
        CreatureType.GRASS: 0.5,
        CreatureType.GROUND: 2.0,
        CreatureType.ROCK: 2.0,
    },
    CreatureType.ELECTRIC: {
        CreatureType.WATER: 2.0,
        CreatureType.FLYING: 2.0,
        CreatureType.ELECTRIC: 0.5,
        CreatureType.GROUND: 0.0,
    },
}


class Move:
    """Represents a creature's move/attack"""
    
    def __init__(self, name, move_type, power, accuracy=100):
        self.name = name
        self.type = move_type
        self.power = power
        self.accuracy = accuracy


class Creature:
    """
    Represents a creature (similar to Pokemon)
    """
    
    def __init__(self, name, creature_type, level=5, max_hp=None, attack=None, 
                 defense=None, speed=None, moves=None):
        self.name = name
        self.type = creature_type
        self.level = level
        
        # Base stats (if not provided, use defaults based on level)
        self.max_hp = max_hp or (20 + level * 5)
        self.attack = attack or (5 + level * 2)
        self.defense = defense or (5 + level * 2)
        self.speed = speed or (5 + level * 2)
        
        self.current_hp = self.max_hp
        self.moves = moves or []
        self.status = None  # For status effects like poison, paralysis, etc.
        
    def is_fainted(self):
        """Check if creature has fainted"""
        return self.current_hp <= 0
    
    def take_damage(self, damage):
        """Apply damage to the creature"""
        self.current_hp = max(0, self.current_hp - damage)
    
    def heal(self, amount):
        """Heal the creature"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def full_heal(self):
        """Fully restore HP"""
        self.current_hp = self.max_hp
        self.status = None
    
    def calculate_damage(self, move, target):
        """
        Calculate damage dealt to target using a move.
        Based on Pokemon damage formula (simplified).
        """
        if random.randint(1, 100) > move.accuracy:
            return 0  # Move missed
        
        # Base damage calculation
        level_factor = (2 * self.level / 5) + 2
        damage = (level_factor * move.power * (self.attack / target.defense)) / 50
        damage += 2
        
        # Type effectiveness
        effectiveness = 1.0
        if move.type in TYPE_EFFECTIVENESS:
            if target.type in TYPE_EFFECTIVENESS[move.type]:
                effectiveness = TYPE_EFFECTIVENESS[move.type][target.type]
        
        # STAB (Same Type Attack Bonus)
        if move.type == self.type:
            damage *= 1.5
        
        damage *= effectiveness
        
        # Random factor (85-100%)
        damage *= random.uniform(0.85, 1.0)
        
        return int(damage)
    
    def __str__(self):
        return f"{self.name} (Lv.{self.level}) - {self.current_hp}/{self.max_hp} HP"


# Predefined creatures similar to starter Pokemon
STARTER_CREATURES = {
    "Flamepup": Creature(
        "Flamepup",
        CreatureType.FIRE,
        level=5,
        max_hp=25,
        attack=12,
        defense=8,
        speed=11,
        moves=[
            Move("Scratch", CreatureType.NORMAL, 40),
            Move("Ember", CreatureType.FIRE, 40),
        ]
    ),
    "Aquatail": Creature(
        "Aquatail",
        CreatureType.WATER,
        level=5,
        max_hp=24,
        attack=10,
        defense=11,
        speed=9,
        moves=[
            Move("Tackle", CreatureType.NORMAL, 40),
            Move("Water Gun", CreatureType.WATER, 40),
        ]
    ),
    "Leafsprout": Creature(
        "Leafsprout",
        CreatureType.GRASS,
        level=5,
        max_hp=26,
        attack=11,
        defense=10,
        speed=10,
        moves=[
            Move("Tackle", CreatureType.NORMAL, 40),
            Move("Vine Whip", CreatureType.GRASS, 45),
        ]
    ),
}


# Wild creatures that can be encountered
WILD_CREATURES = [
    lambda: Creature("Rockbug", CreatureType.ROCK, level=random.randint(2, 6),
                     moves=[Move("Tackle", CreatureType.NORMAL, 40)]),
    lambda: Creature("Sparkrat", CreatureType.ELECTRIC, level=random.randint(3, 7),
                     moves=[Move("Quick Attack", CreatureType.NORMAL, 40),
                            Move("Thunder Shock", CreatureType.ELECTRIC, 40)]),
    lambda: Creature("Sandmole", CreatureType.GROUND, level=random.randint(2, 5),
                     moves=[Move("Scratch", CreatureType.NORMAL, 40)]),
    lambda: Creature("Windbird", CreatureType.FLYING, level=random.randint(3, 6),
                     moves=[Move("Peck", CreatureType.FLYING, 35)]),
]


def get_random_wild_creature():
    """Generate a random wild creature"""
    return random.choice(WILD_CREATURES)()
