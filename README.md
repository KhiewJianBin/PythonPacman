# PythonPacman

  Course Assignment Project in Singapore Polytechnic.

  Pacman recreation using Panda3D & Box2D for Collisions

  <img src="https://user-images.githubusercontent.com/5699978/192647030-2154d9d2-641b-4e59-ae2b-6afded882a38.png" width="500">

# Install
  No Installation Required. Just Git clone or direct download

## Usage
1. Install [Panda3D](https://github.com/KhiewJianBin/PythonPacman/blob/main/Redist/Panda3D-1.8.1.exe) in Redist
2. Fix Audio Bug: Open Panda3D Config file in  {panda root}\etc\Config.prc
3. Search and replace "audio-library-name p3openal_audio" to "audio-library-name p3fmod_audio"
4. Run [Task14.py](https://github.com/KhiewJianBin/PythonPacman/blob/main/PacMan/Task14.py) in Panda3Ds' preinstlal python(python 2.7) using CLI

## Instructions

### System Controls

```
F1 - Wireframe Mode
F2 - No Texture Mode
F3 - Debug Mode: shows hitbox and directional axis
```

### Player Controls

```
W - Move Up
A - Move Left
S - Move Down
D - Move Right
```
### Player Controls

```
Mouse LeftClick + Drag Up Down - Zoom In/Out
Mouse LeftClick + Drag Left Right - Pan Left/Right 
Mouse RightClick + Drag Up Down - Pan Up/Down
Mouse Middle Button + Drag - RotateCamera (not recommand to use)
```


## Bugs
- Game loads on start and Camera Controls are active while on main menu

## Notes
- Other versions of python might not work properly

## Dev Notes
- Movement of Player & Ghost is done using Box2D which introduce floating point positions
- Converts floating point position to Grid based Maze coordinates is tricky with floating point precisions
- Movement thoughout the maze is also affected
- <details>
    <summary>Ghost AI is done using FSM</summary>

    <img src="https://user-images.githubusercontent.com/5699978/192647085-1b9e1339-dc36-4111-b85f-fdd3b763926a.jpg" width="500">

  </details>
