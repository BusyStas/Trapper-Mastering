"""
Battle system for Trapper-Mastering game.
Implements turn-based combat similar to Pokemon.
"""

import random
from creature import Creature
from player import Player, TRAP_TYPES, HEAL_ITEMS


class BattleResult:
    """Enum for battle outcomes"""
    ONGOING = "ongoing"
    PLAYER_WIN = "player_win"
    PLAYER_LOSE = "player_lose"
    CAUGHT = "caught"
    RAN_AWAY = "ran_away"


class Battle:
    """
    Manages a battle between player and wild creature
    """
    
    def __init__(self, player, wild_creature):
        self.player = player
        self.wild_creature = wild_creature
        self.player_creature = player.get_active_creature()
        self.battle_log = []
        self.result = BattleResult.ONGOING
        
    def add_log(self, message):
        """Add a message to battle log"""
        self.battle_log.append(message)
    
    def get_battle_state(self):
        """Get current state of battle"""
        return {
            'player_creature': self.player_creature,
            'wild_creature': self.wild_creature,
            'log': self.battle_log[-5:],  # Last 5 messages
            'result': self.result
        }
    
    def player_attack(self, move_index):
        """Player creature attacks with selected move"""
        if self.result != BattleResult.ONGOING:
            return
        
        if move_index >= len(self.player_creature.moves):
            self.add_log("Invalid move!")
            return
        
        move = self.player_creature.moves[move_index]
        
        # Determine turn order based on speed
        player_first = self.player_creature.speed >= self.wild_creature.speed
        
        if player_first:
            self._execute_player_move(move)
            if not self.wild_creature.is_fainted():
                self._execute_wild_move()
        else:
            self._execute_wild_move()
            if not self.player_creature.is_fainted():
                self._execute_player_move(move)
        
        self._check_battle_end()
    
    def _execute_player_move(self, move):
        """Execute player's move"""
        damage = self.player_creature.calculate_damage(move, self.wild_creature)
        
        if damage == 0:
            self.add_log(f"{self.player_creature.name}'s {move.name} missed!")
        else:
            self.wild_creature.take_damage(damage)
            self.add_log(f"{self.player_creature.name} used {move.name}! Dealt {damage} damage.")
            
            if self.wild_creature.is_fainted():
                self.add_log(f"Wild {self.wild_creature.name} fainted!")
    
    def _execute_wild_move(self):
        """Execute wild creature's move"""
        if not self.wild_creature.moves:
            return
        
        move = random.choice(self.wild_creature.moves)
        damage = self.wild_creature.calculate_damage(move, self.player_creature)
        
        if damage == 0:
            self.add_log(f"Wild {self.wild_creature.name}'s {move.name} missed!")
        else:
            self.player_creature.take_damage(damage)
            self.add_log(f"Wild {self.wild_creature.name} used {move.name}! Dealt {damage} damage.")
            
            if self.player_creature.is_fainted():
                self.add_log(f"{self.player_creature.name} fainted!")
    
    def attempt_catch(self, trap_name):
        """
        Attempt to catch the wild creature with a trap.
        Based on Pokemon catch rate formula (simplified).
        """
        if self.result != BattleResult.ONGOING:
            return False
        
        # Use the trap
        if not self.player.use_item(trap_name):
            self.add_log("You don't have any traps!")
            return False
        
        trap = TRAP_TYPES.get(trap_name)
        if not trap:
            return False
        
        # Calculate catch chance
        hp_factor = (3 * self.wild_creature.max_hp - 2 * self.wild_creature.current_hp) / (3 * self.wild_creature.max_hp)
        catch_rate = hp_factor * trap.catch_rate * 255
        
        # Shake calculation (simplified)
        shake_check = int((65536 / (255 / catch_rate)) ** 0.25)
        
        self.add_log(f"{self.player.name} threw a {trap_name}!")
        
        # Simulate shakes (1-4 times)
        shakes = 0
        for i in range(4):
            if random.randint(0, 65535) < shake_check:
                shakes += 1
            else:
                break
        
        if shakes == 4:
            # Caught!
            self.add_log(f"Gotcha! {self.wild_creature.name} was caught!")
            self.player.add_creature(self.wild_creature)
            self.result = BattleResult.CAUGHT
            return True
        else:
            self.add_log(f"{self.wild_creature.name} broke free!")
            # Wild creature gets a free turn
            self._execute_wild_move()
            self._check_battle_end()
            return False
    
    def use_heal_item(self, item_name):
        """Use a healing item on player's creature"""
        if self.result != BattleResult.ONGOING:
            return False
        
        if not self.player.use_item(item_name):
            self.add_log("You don't have that item!")
            return False
        
        heal_item = HEAL_ITEMS.get(item_name)
        if not heal_item:
            return False
        
        old_hp = self.player_creature.current_hp
        self.player_creature.heal(heal_item.heal_amount)
        healed = self.player_creature.current_hp - old_hp
        
        self.add_log(f"Used {item_name}! Restored {healed} HP.")
        
        # Wild creature gets a turn
        self._execute_wild_move()
        self._check_battle_end()
        return True
    
    def attempt_run(self):
        """Attempt to run from battle"""
        if self.result != BattleResult.ONGOING:
            return False
        
        # Calculate escape chance based on speed
        player_speed = self.player_creature.speed
        wild_speed = self.wild_creature.speed
        
        escape_chance = (player_speed * 128) / wild_speed + 30
        
        if random.randint(0, 255) < escape_chance:
            self.add_log("Got away safely!")
            self.result = BattleResult.RAN_AWAY
            return True
        else:
            self.add_log("Can't escape!")
            # Wild creature gets a turn
            self._execute_wild_move()
            self._check_battle_end()
            return False
    
    def switch_creature(self, new_creature):
        """Switch to a different creature"""
        if self.result != BattleResult.ONGOING:
            return False
        
        if new_creature.is_fainted():
            self.add_log(f"{new_creature.name} has fainted and can't battle!")
            return False
        
        self.add_log(f"{self.player.name} called back {self.player_creature.name}!")
        self.player_creature = new_creature
        self.add_log(f"Go, {self.player_creature.name}!")
        
        # Wild creature gets a turn
        self._execute_wild_move()
        self._check_battle_end()
        return True
    
    def _check_battle_end(self):
        """Check if battle has ended"""
        if self.wild_creature.is_fainted():
            self.result = BattleResult.PLAYER_WIN
            # Award some money/experience (simplified)
            reward = self.wild_creature.level * 10
            self.player.money += reward
            self.add_log(f"You won! Earned ${reward}.")
        elif self.player_creature.is_fainted():
            # Check if player has other creatures
            next_creature = self.player.get_active_creature()
            if next_creature:
                self.add_log(f"Switch to {next_creature.name}!")
                self.player_creature = next_creature
            else:
                self.result = BattleResult.PLAYER_LOSE
                self.add_log("All your creatures fainted! You lost the battle.")
