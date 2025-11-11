# Trapper-Mastering

A game similar to Pokemon Blue, Red, and Yellow but instead of a county, it is a whole state sized area and use traps to help catch creatures.

## Overview

Trapper-Mastering is a turn-based creature-catching RPG inspired by the classic Pokemon games. Explore a state-sized region, catch wild creatures using traps, battle other creatures, and build your ultimate team!

## Features

- **Creature System**: Catch and train creatures with different types (Fire, Water, Grass, Electric, Rock, Ground, Flying, Normal)
- **Type Advantages**: Strategic type-based combat system similar to Pokemon
- **Turn-Based Battles**: Classic turn-based combat with moves, items, and tactics
- **Trap System**: Use different types of traps to catch wild creatures (Basic Trap, Super Trap, Ultra Trap)
- **Party Management**: Build a team of up to 6 creatures
- **Multiple Locations**: Travel between different areas with varying wild creature encounter rates
- **Inventory System**: Manage traps, healing items, and other supplies
- **Save/Load**: Save your progress and continue your adventure later

## Installation

### Requirements
- Python 3.7 or higher

### Setup

1. Clone this repository:
```bash
git clone https://github.com/BusyStas/Trapper-Mastering.git
cd Trapper-Mastering
```

2. (Optional) Install pygame if you want future graphics support:
```bash
pip install -r requirements.txt
```

## How to Play

### Starting the Game

Run the game using Python:
```bash
python game.py
```

### Game Flow

1. **Choose Your Starter**: Select one of three starter creatures:
   - **Flamepup** (Fire type) - Balanced attacker with fire moves
   - **Aquatail** (Water type) - Defensive specialist with water moves
   - **Leafsprout** (Grass type) - HP tank with grass moves

2. **Main Menu Options**:
   - **View Party**: Check your creatures' stats, HP, and moves
   - **Check Inventory**: See your traps, potions, and other items
   - **Travel**: Move between different locations
   - **Look for Wild Creatures**: Search for creatures to catch or battle
   - **Heal Creatures**: Restore your team's HP (free in Starting Town, costs money elsewhere)
   - **Save Game**: Save your progress
   - **Quit**: Exit the game

3. **Battles**:
   - **Fight**: Attack with your creature's moves
   - **Use Trap**: Attempt to catch the wild creature (works better on weakened creatures)
   - **Use Item**: Heal your creature during battle
   - **Run**: Attempt to flee from battle

### Type Effectiveness Chart

- **Fire** > Grass (2x damage)
- **Water** > Fire, Ground, Rock (2x damage)
- **Grass** > Water, Ground, Rock (2x damage)
- **Electric** > Water, Flying (2x damage)
- **Electric** cannot damage Ground types (0x damage)

### Tips

- Weaken wild creatures before trying to catch them - lower HP increases catch rate
- Use type advantages to deal more damage in battles
- Keep healing items in your inventory for tough battles
- Explore different locations to find different types of creatures
- Save your game regularly!

## Game Structure

The game consists of several Python modules:

- `game.py` - Main game loop and menu system
- `creature.py` - Creature classes, types, and move system
- `player.py` - Player, inventory, and party management
- `battle.py` - Turn-based battle system
- `test_game.py` - Unit tests for game functionality

## Testing

Run the test suite to verify game functionality:
```bash
python -m unittest test_game.py
```

## Future Enhancements

- Graphical user interface using pygame
- More creatures and evolutions
- Trainer battles
- Multiple save slots
- Creature leveling and stat growth
- More moves and abilities
- Additional locations and areas
- Quest system
- Online trading and battles

## License

This project is open source and available for educational purposes.

## Credits

Inspired by Pokemon Blue, Red, and Yellow by Game Freak and Nintendo.
