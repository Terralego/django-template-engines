from io import BytesIO

from PIL import Image


def resize(bimage, width, height, odt=True):
    if not width and not height:
        buffer = BytesIO(bimage)
        with Image.open(buffer) as img_reader:
            width, height = img_reader.size
            if odt:
                ratio = min(16697 / width, 28815 / height)
            else:
                ratio = min(6120130 / width, 9251950 / height)
            return int(width * ratio), int(height * ratio)
    return width, height
