[Run Instructions]
1. Install Panda3D (Tested to work on Version 1.8.1)
2. Set the "Run pacman" shortcut to Start In "%path to folder%\PacMan"
3. Set the "Run Pacman" shortcut to Target Panda3D's 1.8.1 Preinstlled Python + Task14.py (start python and run Task14.py, Note that Panda3D 1.8.1 Uses Python2.7)
3. Open Panda3D Config file \etc\Config.prc
4. Search and replace "audio-library-name p3openal_audio" to "audio-library-name p3fmod_audio"

[Controls]
Movement:
W - Move Up
A - Move Left
S - Move Down
D - Move Right

Camera:
Mouse LeftClick + Drag Up Down - Zoom In/Out
Mouse LeftClick + Drag Left Right - Pan Left/Right 
Mouse RightClick + Drag Up Down - Pan Up/Down
Mouse Middle Button + Drag - RotateCamera (not recommand to use)

[System]
F1 - Wireframe Mode
F2 - No Texture Mode
F3 - Debug Mode: shows hitbox and directional axis

Others:
P - Pause Game
Space - Respawn/Reset after death