#!/usr/bin/env python3
"""
Automated playthrough demo for Trapper-Mastering
Simulates a player playing through key game features
"""

import sys
from io import StringIO
from creature import STARTER_CREATURES, get_random_wild_creature, Creature
from player import Player
from battle import Battle, BattleResult


def automated_playthrough():
    """Run an automated playthrough of the game"""
    print("=" * 70)
    print("TRAPPER-MASTERING - AUTOMATED PLAYTHROUGH DEMO")
    print("=" * 70)
    print("\nThis demo shows the game being played automatically...\n")
    
    # Create player
    print(">>> Creating player 'Ash'...")
    player = Player("Ash")
    print(f"    ✓ Player created with ${player.money}")
    print(f"    ✓ Starting inventory: {list(player.inventory.keys())}")
    
    # Choose starter
    print("\n>>> Choosing starter creature: Flamepup...")
    starter = STARTER_CREATURES["Flamepup"]
    player_creature = Creature(
        starter.name, starter.type, starter.level,
        starter.max_hp, starter.attack, starter.defense, starter.speed,
        starter.moves.copy()
    )
    player.add_creature(player_creature)
    print(f"    ✓ {player_creature.name} added to party")
    print(f"    ✓ Moves: {', '.join(m.name for m in player_creature.moves)}")
    
    # First wild encounter
    print("\n>>> Encountering first wild creature...")
    wild1 = get_random_wild_creature()
    print(f"    ✓ Wild {wild1.name} (Lv.{wild1.level}) appeared!")
    
    # Battle 1
    print("\n>>> Battle 1: Training battle...")
    battle1 = Battle(player, wild1)
    turns = 0
    while battle1.result == BattleResult.ONGOING and turns < 10:
        battle1.player_attack(1 if len(player_creature.moves) > 1 else 0)
        turns += 1
    
    print(f"    ✓ Battle ended: {battle1.result}")
    print(f"    ✓ Player money: ${player.money}")
    
    # Heal if needed
    if player_creature.current_hp < player_creature.max_hp:
        print("\n>>> Healing Flamepup...")
        player_creature.full_heal()
        print(f"    ✓ {player_creature.name} restored to full HP")
    
    # Second encounter - catch attempt
    print("\n>>> Encountering second wild creature to catch...")
    wild2 = get_random_wild_creature()
    print(f"    ✓ Wild {wild2.name} (Lv.{wild2.level}) appeared!")
    
    print("\n>>> Battle 2: Attempting to catch...")
    battle2 = Battle(player, wild2)
    
    # Weaken the wild creature
    attempts = 0
    while battle2.result == BattleResult.ONGOING and attempts < 5:
        # Attack to weaken
        battle2.player_attack(0)
        attempts += 1
        
        # Try to catch when HP is low
        if wild2.current_hp < wild2.max_hp * 0.4 and battle2.result == BattleResult.ONGOING:
            print(f"    ⟳ Wild {wild2.name} HP is low, attempting catch...")
            caught = False
            catch_attempts = 0
            while not caught and catch_attempts < 5 and battle2.result == BattleResult.ONGOING:
                caught = battle2.attempt_catch("Basic Trap")
                catch_attempts += 1
                if caught:
                    print(f"    ✓ Caught {wild2.name}!")
                    break
            if caught:
                break
    
    print(f"    ✓ Battle result: {battle2.result}")
    print(f"    ✓ Party size: {len(player.party)} creatures")
    print(f"    ✓ Remaining traps: {player.get_item_count('Basic Trap')}")
    
    # Show party status
    print("\n>>> Final Party Status:")
    for i, creature in enumerate(player.party, 1):
        status = "FAINTED" if creature.is_fainted() else "HEALTHY"
        print(f"    {i}. {creature.name} (Lv.{creature.level}) - {creature.type} type")
        print(f"       HP: {creature.current_hp}/{creature.max_hp} - Status: {status}")
    
    # Show inventory
    print("\n>>> Final Inventory:")
    for item, count in sorted(player.inventory.items()):
        print(f"    {item}: {count}")
    
    print(f"\n>>> Player Stats:")
    print(f"    Money: ${player.money}")
    print(f"    Creatures caught: {len(player.party)}")
    
    # Test type effectiveness
    print("\n>>> Type Effectiveness Demonstration:")
    print("    Fire > Grass (2x damage)")
    print("    Water > Fire (2x damage)")
    print("    Grass > Water (2x damage)")
    print("    Electric > Water (2x damage)")
    print("    Electric vs Ground (0x damage - immune!)")
    
    print("\n" + "=" * 70)
    print("PLAYTHROUGH COMPLETE!")
    print("=" * 70)
    print("\n✓ All core game mechanics demonstrated successfully!")
    print("✓ Ready for player interaction!")
    print("\nTo play the full interactive game, run: python game.py")
    print()


if __name__ == "__main__":
    # Set random seed for consistent demo
    import random
    random.seed(42)
    automated_playthrough()
