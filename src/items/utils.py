from PIL import Image
from arcade import Texture

white_cache: dict[str, Texture] = {}


def create_white_texture(texture_path: str):
    global white_cache
    if texture_path in white_cache:
        return white_cache[texture_path]

    try:
        image = Image.open(texture_path)
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        data = image.getdata()
        new_data = []
        for item in data:
            # Si el pixel es transparente mantenerlo asi
            if item[3] == 0:  # El item 3 el alpha channel
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((255, 255, 255, item[3]))
        white_image = Image.new("RGBA", image.size)
        white_image.putdata(new_data)
        return Texture(white_image)
    except Exception as e:
        print(f"Error crendo la trextura blanca para el item : {texture_path}")
        print(e)
        return None
