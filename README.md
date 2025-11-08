# Car Racing Game

Welcome to the **Car Racing Game**, a thrilling and immersive racing experience where you can test your driving skills against AI-controlled NPC cars. This game features realistic physics, dynamic lighting, and challenging tracks to keep you engaged.

## Screenshot

![image info](./screenshot.png)

## Features

- **Realistic Car Physics**: Experience authentic car handling and physics.
- **Dynamic Lighting**: Enjoy visually stunning graphics with dynamic lighting effects.
- **Challenging Tracks**: Race on multiple tracks with varying difficulty levels.
- **AI-Controlled NPC Cars**: Compete against intelligent NPC cars with adaptive behavior.
- **Traffic Light System**: Navigate through intersections with working traffic lights.
- **Customizable Cars**: Modify car appearance and performance.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
   
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python app.py
   ```
2. Use the arrow keys to control your car:
   - **Up Arrow**: Accelerate
   - **Down Arrow**: Brake/Reverse
   - **Left Arrow**: Steer Left
   - **Right Arrow**: Steer Right
3. Avoid collisions and try to finish the race as quickly as possible.

## File Structure

- `app.py`: Main entry point for the game.
- `classes/`: Contains all the core game logic and classes.
  - `car.py`: Handles car rendering and behavior.
  - `game.py`: Manages the game loop and overall logic.
  - `track.py`: Defines the racing tracks.
  - `lighting.py`: Implements dynamic lighting effects.
  - `physics.py`: Handles car physics and collisions.
  - `loading_screen.py`: Displays the loading screen.
- `requirements.txt`: Lists all the dependencies required to run the game.
- `extra/`: Contains test files for various game components.

## Contributing

Contributions are welcome! If you'd like to improve the game, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Special thanks to all contributors and testers.
- Inspired by classic racing games and modern simulation techniques.


Enjoy the race and may the best driver win!
