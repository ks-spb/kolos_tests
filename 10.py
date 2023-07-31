from pyrect import PyRect

desktop = PyRect.getWindowsWithTitle('Program Manager')[0]
children = desktop.getChildren()

for child in children:
  if child.getClassName() == 'ShellDocObjectView':
    print(child.getWindowText())
    x, y, width, height = child.getRectangle()
    print(f'Координаты: {x}, {y}')