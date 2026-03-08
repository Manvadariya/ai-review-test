# Pygame Todo App

Simple desktop todo app built with Python and Pygame.

## Install

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Features

- Add tasks from the input field
- Select tasks with the mouse or arrow keys
- Toggle completion with the `Toggle` button or the space bar
- Delete tasks with the `Delete` button or the delete key
- Persist tasks to `todos.json` automatically

## Run

```powershell
.venv\Scripts\python.exe main.py
```

## Test

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests
```