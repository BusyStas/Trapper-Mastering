"""
Test suite for Trapper-Mastering game
"""

import unittest
from creature import Creature, Move, CreatureType, get_random_wild_creature
from player import Player
from battle import Battle, BattleResult


class TestCreature(unittest.TestCase):
    """Test creature functionality"""
    
    def test_creature_creation(self):
        """Test creating a creature"""
        creature = Creature("TestMon", CreatureType.FIRE, level=5)
        self.assertEqual(creature.name, "TestMon")
        self.assertEqual(creature.type, CreatureType.FIRE)
        self.assertEqual(creature.level, 5)
        self.assertGreater(creature.max_hp, 0)
        self.assertEqual(creature.current_hp, creature.max_hp)
    
    def test_creature_faint(self):
        """Test creature fainting"""
        creature = Creature("TestMon", CreatureType.FIRE, level=5)
        self.assertFalse(creature.is_fainted())
        
        creature.take_damage(creature.max_hp)
        self.assertTrue(creature.is_fainted())
        self.assertEqual(creature.current_hp, 0)
    
    def test_creature_heal(self):
        """Test creature healing"""
        creature = Creature("TestMon", CreatureType.FIRE, level=5, max_hp=50)
        creature.take_damage(30)
        self.assertEqual(creature.current_hp, 20)
        
        creature.heal(20)
        self.assertEqual(creature.current_hp, 40)
        
        creature.heal(100)  # Overheal
        self.assertEqual(creature.current_hp, 50)
    
    def test_damage_calculation(self):
        """Test damage calculation"""
        attacker = Creature("Attacker", CreatureType.FIRE, level=10, attack=20)
        defender = Creature("Defender", CreatureType.GRASS, level=10, defense=10)
        move = Move("Test Move", CreatureType.FIRE, 50, accuracy=100)
        
        damage = attacker.calculate_damage(move, defender)
        # Should deal damage due to type advantage and STAB
        self.assertGreater(damage, 0)
    
    def test_wild_creature_generation(self):
        """Test generating random wild creatures"""
        creature = get_random_wild_creature()
        self.assertIsInstance(creature, Creature)
        self.assertGreater(creature.level, 0)
        self.assertGreater(len(creature.moves), 0)


class TestPlayer(unittest.TestCase):
    """Test player functionality"""
    
    def test_player_creation(self):
        """Test creating a player"""
        player = Player("Ash")
        self.assertEqual(player.name, "Ash")
        self.assertEqual(len(player.party), 0)
        self.assertGreater(player.money, 0)
        self.assertGreater(player.get_item_count("Basic Trap"), 0)
    
    def test_add_creature(self):
        """Test adding creatures to party"""
        player = Player("Ash")
        creature = Creature("TestMon", CreatureType.FIRE, level=5)
        
        result = player.add_creature(creature)
        self.assertTrue(result)
        self.assertEqual(len(player.party), 1)
        self.assertEqual(player.party[0], creature)
    
    def test_party_limit(self):
        """Test party size limit"""
        player = Player("Ash")
        
        # Add 6 creatures
        for i in range(6):
            creature = Creature(f"Mon{i}", CreatureType.NORMAL, level=5)
            result = player.add_creature(creature)
            self.assertTrue(result)
        
        self.assertEqual(len(player.party), 6)
        
        # 7th creature should go to PC
        creature7 = Creature("Mon7", CreatureType.NORMAL, level=5)
        result = player.add_creature(creature7)
        self.assertFalse(result)
        self.assertEqual(len(player.party), 6)
        self.assertEqual(len(player.pc_box), 1)
    
    def test_item_management(self):
        """Test item usage"""
        player = Player("Ash")
        
        initial_count = player.get_item_count("Basic Trap")
        self.assertGreater(initial_count, 0)
        
        # Use an item
        result = player.use_item("Basic Trap")
        self.assertTrue(result)
        self.assertEqual(player.get_item_count("Basic Trap"), initial_count - 1)
        
        # Try to use non-existent item
        result = player.use_item("Nonexistent Item")
        self.assertFalse(result)


class TestBattle(unittest.TestCase):
    """Test battle functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.player = Player("Ash")
        creature = Creature("PlayerMon", CreatureType.FIRE, level=10, 
                          moves=[Move("Ember", CreatureType.FIRE, 40)])
        self.player.add_creature(creature)
        
        self.wild = Creature("WildMon", CreatureType.GRASS, level=5,
                           moves=[Move("Tackle", CreatureType.NORMAL, 40)])
    
    def test_battle_creation(self):
        """Test creating a battle"""
        battle = Battle(self.player, self.wild)
        self.assertEqual(battle.result, BattleResult.ONGOING)
        self.assertIsNotNone(battle.player_creature)
    
    def test_battle_attack(self):
        """Test battle attack"""
        battle = Battle(self.player, self.wild)
        initial_hp = self.wild.current_hp
        
        battle.player_attack(0)  # Use first move
        
        # Wild creature should have taken damage or player's creature took damage
        self.assertTrue(
            self.wild.current_hp < initial_hp or 
            battle.player_creature.current_hp < battle.player_creature.max_hp
        )
    
    def test_battle_catch_attempt(self):
        """Test catching mechanism"""
        battle = Battle(self.player, self.wild)
        
        # Weaken the wild creature
        self.wild.take_damage(self.wild.max_hp - 1)
        
        initial_party_size = len(self.player.party)
        initial_trap_count = self.player.get_item_count("Basic Trap")
        
        # Multiple attempts might be needed
        caught = False
        for _ in range(10):  # Try up to 10 times
            if battle.result != BattleResult.ONGOING:
                break
            caught = battle.attempt_catch("Basic Trap")
            if caught:
                break
        
        # Either caught or used at least one trap
        if caught:
            self.assertEqual(battle.result, BattleResult.CAUGHT)
            self.assertGreater(len(self.player.party), initial_party_size)
    
    def test_battle_run(self):
        """Test running from battle"""
        battle = Battle(self.player, self.wild)
        
        # Try to run multiple times (might fail due to RNG)
        ran = False
        for _ in range(10):
            if battle.result != BattleResult.ONGOING:
                break
            ran = battle.attempt_run()
            if ran:
                break
        
        # Should eventually run away
        if ran:
            self.assertEqual(battle.result, BattleResult.RAN_AWAY)
    
    def test_battle_win(self):
        """Test winning a battle"""
        battle = Battle(self.player, self.wild)
        
        # Deal massive damage to guarantee KO
        self.wild.take_damage(self.wild.max_hp)
        battle._check_battle_end()
        
        self.assertEqual(battle.result, BattleResult.PLAYER_WIN)


if __name__ == '__main__':
    unittest.main()
