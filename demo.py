#!/usr/bin/env python3
"""
Demo script to showcase Trapper-Mastering game features
"""

from creature import STARTER_CREATURES, get_random_wild_creature, Creature, Move, CreatureType
from player import Player
from battle import Battle, BattleResult


def demo_game():
    """Run a simple demo of the game"""
    print("=" * 70)
    print("TRAPPER-MASTERING - GAME DEMO")
    print("=" * 70)
    print()
    
    # Create a player
    print("1. Creating a new player...")
    player = Player("Demo Player")
    print(f"   Player: {player.name}")
    print(f"   Starting money: ${player.money}")
    print(f"   Starting inventory: {player.inventory}")
    print()
    
    # Add a starter creature
    print("2. Choosing starter creature: Flamepup (Fire type)")
    starter = STARTER_CREATURES["Flamepup"]
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
    player.add_creature(player_starter)
    print(f"   {player_starter}")
    print(f"   Type: {player_starter.type}")
    print(f"   Moves: {', '.join(m.name for m in player_starter.moves)}")
    print()
    
    # Show all starter options
    print("3. All available starter creatures:")
    for name, creature in STARTER_CREATURES.items():
        print(f"   - {creature.name} ({creature.type})")
        print(f"     Stats: HP={creature.max_hp}, ATK={creature.attack}, " +
              f"DEF={creature.defense}, SPD={creature.speed}")
    print()
    
    # Generate a wild creature
    print("4. Encountering a wild creature...")
    wild = get_random_wild_creature()
    print(f"   A wild {wild.name} (Lv.{wild.level}) appeared!")
    print(f"   Type: {wild.type}")
    print(f"   HP: {wild.current_hp}/{wild.max_hp}")
    print()
    
    # Start a battle
    print("5. Starting a battle...")
    battle = Battle(player, wild)
    print(f"   {player_starter.name} vs {wild.name}")
    print()
    
    # Simulate a few turns
    print("6. Battle simulation:")
    turn = 1
    while battle.result == BattleResult.ONGOING and turn <= 5:
        print(f"\n   Turn {turn}:")
        print(f"   Player's {player_starter.name}: {player_starter.current_hp}/{player_starter.max_hp} HP")
        print(f"   Wild {wild.name}: {wild.current_hp}/{wild.max_hp} HP")
        
        # Player attacks
        battle.player_attack(0)  # Use first move
        
        # Show battle log
        state = battle.get_battle_state()
        if state['log']:
            for msg in state['log'][-2:]:  # Last 2 messages
                print(f"   > {msg}")
        
        turn += 1
        
        # If wild creature is low on HP, try to catch
        if wild.current_hp < wild.max_hp * 0.3 and battle.result == BattleResult.ONGOING:
            print(f"\n   Attempting to catch {wild.name} with Basic Trap...")
            caught = battle.attempt_catch("Basic Trap")
            if caught:
                print(f"   SUCCESS! {wild.name} was caught!")
                break
    
    print()
    
    # Show final results
    print("7. Battle Results:")
    print(f"   Battle outcome: {battle.result}")
    print(f"   Player's party size: {len(player.party)}")
    print(f"   Remaining Basic Traps: {player.get_item_count('Basic Trap')}")
    print()
    
    # Show party
    print("8. Player's Party:")
    for i, creature in enumerate(player.party, 1):
        status = "FAINTED" if creature.is_fainted() else "OK"
        print(f"   {i}. {creature.name} (Lv.{creature.level}) - {creature.current_hp}/{creature.max_hp} HP - {status}")
    print()
    
    # Demonstrate type effectiveness
    print("9. Type Effectiveness Example:")
    fire_creature = Creature("Flamepup", CreatureType.FIRE, level=10, attack=20,
                            moves=[Move("Ember", CreatureType.FIRE, 50)])
    grass_creature = Creature("Leafsprout", CreatureType.GRASS, level=10, defense=15)
    water_creature = Creature("Aquatail", CreatureType.WATER, level=10, defense=15)
    
    move = fire_creature.moves[0]
    
    damage_to_grass = fire_creature.calculate_damage(move, grass_creature)
    damage_to_water = fire_creature.calculate_damage(move, water_creature)
    
    print(f"   Flamepup's Ember vs Leafsprout (Fire > Grass): ~{damage_to_grass} damage (SUPER EFFECTIVE)")
    print(f"   Flamepup's Ember vs Aquatail (Fire < Water): ~{damage_to_water} damage (Not very effective)")
    print()
    
    print("=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print("\nTo play the full game, run: python game.py")
    print()


if __name__ == "__main__":
    demo_game()
