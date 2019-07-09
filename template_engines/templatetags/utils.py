def resize(width, height):
    ratio = min(16697 / width, 28815 / height)
    return width * ratio, height * ratio
