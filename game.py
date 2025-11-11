"""
Main game module for Trapper-Mastering.
A Pokemon-like game where you catch creatures using traps.
"""

import random
import json
import os
from creature import STARTER_CREATURES, get_random_wild_creature, Creature, Move
from player import Player
from battle import Battle, BattleResult


class Game:
    """
    Main game class managing game state and flow
    """
    
    def __init__(self):
        self.player = None
        self.current_location = "Starting Town"
        self.locations = {
            "Starting Town": {
                "description": "A peaceful town where your journey begins.",
                "wild_encounter_rate": 0.0,
            },
            "Route 1": {
                "description": "A grassy route filled with wild creatures.",
                "wild_encounter_rate": 0.3,
            },
            "Forest Path": {
                "description": "A dense forest with many creatures.",
                "wild_encounter_rate": 0.5,
            },
            "Mountain Trail": {
                "description": "Rocky terrain where rock-type creatures dwell.",
                "wild_encounter_rate": 0.4,
            },
        }
        
    def start_new_game(self):
        """Start a new game"""
        print("=" * 60)
        print("Welcome to TRAPPER-MASTERING!")
        print("=" * 60)
        print("\nA state-sized adventure awaits you!")
        print("Catch creatures using traps and become the ultimate Trapper Master!\n")
        
        # Get player name
        player_name = input("What is your name? ").strip()
        if not player_name:
            player_name = "Trainer"
        
        self.player = Player(player_name)
        
        # Choose starter creature
        print(f"\nHello, {player_name}!")
        print("Before you begin your journey, choose your first creature:\n")
        
        starters = list(STARTER_CREATURES.keys())
        for i, name in enumerate(starters, 1):
            creature = STARTER_CREATURES[name]
            print(f"{i}. {creature.name} - Type: {creature.type}")
            print(f"   HP: {creature.max_hp}, Attack: {creature.attack}, Defense: {creature.defense}")
            print(f"   Moves: {', '.join(m.name for m in creature.moves)}\n")
        
        while True:
            try:
                choice = int(input("Choose your starter (1-3): "))
                if 1 <= choice <= len(starters):
                    starter_name = starters[choice - 1]
                    # Create a copy of the starter
                    starter = STARTER_CREATURES[starter_name]
                    player_starter = Creature(
                        starter.name,
                        starter.type,
                        starter.level,
                        starter.max_hp,
                        starter.attack,
                        starter.defense,
                        starter.speed,
                        starter.moves.copy()
                    )
                    self.player.add_creature(player_starter)
                    print(f"\nYou chose {starter_name}! Great choice!")
                    break
            except ValueError:
                pass
            print("Invalid choice. Please enter 1, 2, or 3.")
        
        print("\nYour adventure begins now!")
        self.main_menu()
    
    def main_menu(self):
        """Main game menu"""
        while True:
            print("\n" + "=" * 60)
            print(f"Location: {self.current_location}")
            print(f"Money: ${self.player.money}")
            print("=" * 60)
            print("\nWhat would you like to do?")
            print("1. View Party")
            print("2. Check Inventory")
            print("3. Travel to new location")
            print("4. Look for wild creatures")
            print("5. Heal all creatures")
            print("6. Save Game")
            print("7. Quit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                self.view_party()
            elif choice == "2":
                self.view_inventory()
            elif choice == "3":
                self.travel()
            elif choice == "4":
                self.look_for_creatures()
            elif choice == "5":
                self.heal_creatures()
            elif choice == "6":
                self.save_game()
            elif choice == "7":
                print("\nThanks for playing Trapper-Mastering!")
                break
            else:
                print("Invalid choice.")
    
    def view_party(self):
        """Display player's party"""
        print("\n" + "=" * 60)
        print("YOUR PARTY")
        print("=" * 60)
        
        if not self.player.party:
            print("You don't have any creatures yet!")
            return
        
        for i, creature in enumerate(self.player.party, 1):
            status = "FAINTED" if creature.is_fainted() else "OK"
            print(f"{i}. {creature.name} (Lv.{creature.level}) - Type: {creature.type}")
            print(f"   HP: {creature.current_hp}/{creature.max_hp} - Status: {status}")
            print(f"   Attack: {creature.attack}, Defense: {creature.defense}, Speed: {creature.speed}")
            print(f"   Moves: {', '.join(m.name for m in creature.moves)}")
            print()
    
    def view_inventory(self):
        """Display player's inventory"""
        print("\n" + "=" * 60)
        print("INVENTORY")
        print("=" * 60)
        
        if not self.player.inventory:
            print("Your inventory is empty!")
            return
        
        for item_name, quantity in self.player.inventory.items():
            print(f"{item_name}: {quantity}")
    
    def travel(self):
        """Travel to a new location"""
        print("\n" + "=" * 60)
        print("TRAVEL")
        print("=" * 60)
        print("\nWhere would you like to go?")
        
        locations = list(self.locations.keys())
        for i, location in enumerate(locations, 1):
            marker = " (current)" if location == self.current_location else ""
            print(f"{i}. {location}{marker}")
            print(f"   {self.locations[location]['description']}")
        
        print(f"{len(locations) + 1}. Cancel")
        
        try:
            choice = int(input("\nChoice: "))
            if 1 <= choice <= len(locations):
                self.current_location = locations[choice - 1]
                print(f"\nYou traveled to {self.current_location}!")
        except ValueError:
            pass
    
    def look_for_creatures(self):
        """Search for wild creatures"""
        location_data = self.locations[self.current_location]
        encounter_rate = location_data['wild_encounter_rate']
        
        if encounter_rate == 0.0:
            print("\nThere are no wild creatures in this area.")
            return
        
        print("\nSearching for wild creatures...")
        
        if random.random() < encounter_rate:
            wild_creature = get_random_wild_creature()
            print(f"\nA wild {wild_creature.name} (Lv.{wild_creature.level}) appeared!")
            self.start_battle(wild_creature)
        else:
            print("No creatures found. Try again!")
    
    def start_battle(self, wild_creature):
        """Start a battle with a wild creature"""
        if not self.player.has_usable_creatures():
            print("\nAll your creatures have fainted! Heal them first!")
            return
        
        battle = Battle(self.player, wild_creature)
        
        while battle.result == BattleResult.ONGOING:
            self.battle_menu(battle)
        
        # Battle ended
        if battle.result == BattleResult.PLAYER_LOSE:
            print("\nYou rushed back to town and healed your creatures...")
            self.player.heal_all_creatures()
            self.current_location = "Starting Town"
    
    def battle_menu(self, battle):
        """Display battle menu and handle battle actions"""
        print("\n" + "=" * 60)
        print("BATTLE")
        print("=" * 60)
        
        state = battle.get_battle_state()
        player_creature = state['player_creature']
        wild_creature = state['wild_creature']
        
        # Display creatures
        print(f"\nWild {wild_creature.name} (Lv.{wild_creature.level})")
        print(f"HP: {wild_creature.current_hp}/{wild_creature.max_hp}")
        
        print(f"\nYour {player_creature.name} (Lv.{player_creature.level})")
        print(f"HP: {player_creature.current_hp}/{player_creature.max_hp}")
        
        # Display recent battle log
        if state['log']:
            print("\n--- Battle Log ---")
            for message in state['log']:
                print(f"  {message}")
        
        # Battle menu
        print("\nWhat will you do?")
        print("1. Fight")
        print("2. Use Trap")
        print("3. Use Item")
        print("4. Run")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            self.battle_fight_menu(battle, player_creature)
        elif choice == "2":
            self.battle_trap_menu(battle)
        elif choice == "3":
            self.battle_item_menu(battle)
        elif choice == "4":
            battle.attempt_run()
        else:
            print("Invalid choice.")
    
    def battle_fight_menu(self, battle, player_creature):
        """Show fight menu and select move"""
        print("\nChoose a move:")
        for i, move in enumerate(player_creature.moves, 1):
            print(f"{i}. {move.name} (Type: {move.type}, Power: {move.power})")
        
        try:
            move_choice = int(input("\nMove: ")) - 1
            if 0 <= move_choice < len(player_creature.moves):
                battle.player_attack(move_choice)
            else:
                print("Invalid move!")
        except ValueError:
            print("Invalid input!")
    
    def battle_trap_menu(self, battle):
        """Show trap menu and attempt to catch"""
        traps = [(name, count) for name, count in self.player.inventory.items() 
                 if "Trap" in name]
        
        if not traps:
            print("\nYou don't have any traps!")
            return
        
        print("\nChoose a trap:")
        for i, (name, count) in enumerate(traps, 1):
            print(f"{i}. {name} (x{count})")
        
        try:
            trap_choice = int(input("\nTrap: ")) - 1
            if 0 <= trap_choice < len(traps):
                trap_name = traps[trap_choice][0]
                battle.attempt_catch(trap_name)
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid input!")
    
    def battle_item_menu(self, battle):
        """Show item menu and use item"""
        heal_items = [(name, count) for name, count in self.player.inventory.items() 
                      if "Potion" in name]
        
        if not heal_items:
            print("\nYou don't have any healing items!")
            return
        
        print("\nChoose an item:")
        for i, (name, count) in enumerate(heal_items, 1):
            print(f"{i}. {name} (x{count})")
        
        try:
            item_choice = int(input("\nItem: ")) - 1
            if 0 <= item_choice < len(heal_items):
                item_name = heal_items[item_choice][0]
                battle.use_heal_item(item_name)
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid input!")
    
    def heal_creatures(self):
        """Heal all creatures (costs money or only in town)"""
        if self.current_location == "Starting Town":
            print("\nThe town healer restored your creatures to full health!")
            self.player.heal_all_creatures()
        else:
            cost = 50 * len(self.player.party)
            print(f"\nHealing all creatures will cost ${cost}.")
            confirm = input("Proceed? (y/n): ").strip().lower()
            
            if confirm == 'y' and self.player.money >= cost:
                self.player.money -= cost
                self.player.heal_all_creatures()
                print("All creatures healed!")
            elif confirm == 'y':
                print("You don't have enough money!")
            else:
                print("Cancelled.")
    
    def save_game(self):
        """Save game to file"""
        try:
            save_data = {
                'player_name': self.player.name,
                'money': self.player.money,
                'location': self.current_location,
                'party': [self._serialize_creature(c) for c in self.player.party],
                'inventory': self.player.inventory,
            }
            
            with open('savegame.json', 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print("\nGame saved successfully!")
        except Exception as e:
            print(f"\nError saving game: {e}")
    
    def load_game(self):
        """Load game from file"""
        try:
            with open('savegame.json', 'r') as f:
                save_data = json.load(f)
            
            self.player = Player(save_data['player_name'])
            self.player.money = save_data['money']
            self.current_location = save_data['location']
            self.player.inventory = save_data['inventory']
            
            for creature_data in save_data['party']:
                creature = self._deserialize_creature(creature_data)
                self.player.add_creature(creature)
            
            print("\nGame loaded successfully!")
            self.main_menu()
            
        except FileNotFoundError:
            print("\nNo save file found.")
        except Exception as e:
            print(f"\nError loading game: {e}")
    
    def _serialize_creature(self, creature):
        """Convert creature to dict for saving"""
        return {
            'name': creature.name,
            'type': creature.type,
            'level': creature.level,
            'max_hp': creature.max_hp,
            'current_hp': creature.current_hp,
            'attack': creature.attack,
            'defense': creature.defense,
            'speed': creature.speed,
            'moves': [{'name': m.name, 'type': m.type, 'power': m.power, 'accuracy': m.accuracy} 
                     for m in creature.moves],
        }
    
    def _deserialize_creature(self, data):
        """Convert dict to creature"""
        moves = [Move(m['name'], m['type'], m['power'], m['accuracy']) 
                for m in data['moves']]
        
        creature = Creature(
            data['name'],
            data['type'],
            data['level'],
            data['max_hp'],
            data['attack'],
            data['defense'],
            data['speed'],
            moves
        )
        creature.current_hp = data['current_hp']
        return creature


def main():
    """Main entry point"""
    game = Game()
    
    print("=" * 60)
    print("TRAPPER-MASTERING")
    print("=" * 60)
    print("\n1. New Game")
    print("2. Load Game")
    print("3. Exit")
    
    choice = input("\nChoice: ").strip()
    
    if choice == "1":
        game.start_new_game()
    elif choice == "2":
        game.load_game()
    elif choice == "3":
        print("\nGoodbye!")
    else:
        print("\nInvalid choice.")


if __name__ == "__main__":
    main()
