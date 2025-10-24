import arcade
from DataManager import get_path, texture_manager
from Constants import Assets


# Clase para controlar la ui del personaje por separado
class PlayerUI:
    _instance = None
    _initialized = False
    MAX_LEVEL = 5

    def __new__(cls, *args, **kwargs) -> "PlayerUI":
        if not cls._instance:
            cls._instance = super().__new__(cls)
        if "experience" in kwargs:
            cls._instance.setup_lifes(kwargs["experience"])
        return cls._instance

    def __init__(self, experience: int, *args, **kwargs) -> None:
        if self._initialized:
            return
        self.attack_sprite = arcade.Sprite(get_path("attack_bar.png"), scale=1)
        self.defence_sprite = arcade.Sprite(get_path("defence_bar.png"), scale=1)
        self.experience_sprite = arcade.Sprite(get_path("experience.png"), scale=3)
        self.experience_text = arcade.Text(
            text=str(experience),
            font_size=24,
            x=0,
            y=0,
            color=arcade.color.WHITE,
            font_name=Assets.FONT_NAME,
        )
        self.sprite_list = arcade.SpriteList()
        self.lifes_list = arcade.SpriteList()
        self.sprite_list.append(self.attack_sprite)
        self.sprite_list.append(self.defence_sprite)
        self.sprite_list.append(self.experience_sprite)
        self._initialized = True

    def update_attack(self, value: int):
        if value > self.MAX_LEVEL:
            return
        antique_left = self.attack_sprite.left
        self.attack_sprite.width = value * 30
        self.attack_sprite.left = antique_left

    def update_defence(self, value: int):
        if value > self.MAX_LEVEL:
            return
        antique_left = self.defence_sprite.left
        self.defence_sprite.width = value * 30
        self.defence_sprite.left = antique_left

    def setup_lifes(self, healt: float):
        texture = texture_manager.load_or_get_texture(get_path("full_heart.png"))
        self.lifes_list.clear()
        hearts = healt / 20
        mid_heart = hearts - int(hearts)
        center_x = 0
        for _ in range(int(hearts)):
            temp = arcade.Sprite(texture, scale=3)
            center_x += temp.width + 10
            temp.center_x = center_x
            self.lifes_list.append(temp)

        if mid_heart:
            texture = texture_manager.load_or_get_texture(get_path("half_heart.png"))
            temp = arcade.Sprite(texture, scale=3)
            center_x += temp.width + 10
            temp.center_x = center_x
            self.lifes_list.append(temp)

        for _ in range(int(5 - hearts)):
            texture = texture_manager.load_or_get_texture(get_path("empty_heart.png"))
            temp = arcade.Sprite(texture, scale=3)
            center_x += temp.width + 10
            temp.center_x = center_x
            self.lifes_list.append(temp)

    def update_lifes(self, healt: float) -> None:
        # Remuevo los corazones sobrantes
        total_hearts = len(self.lifes_list)
        full_hearts = int(healt / 20)
        remainder = healt % 20
        for i in range(total_hearts):
            if i < full_hearts:
                continue
            if i < full_hearts + int(remainder / 10):
                texture = texture_manager.load_or_get_texture(
                    get_path("half_heart.png")
                )
            else:
                texture = texture_manager.load_or_get_texture(
                    get_path("empty_heart.png")
                )
            self.lifes_list[i].texture = texture

    def setup_ui_position(self, window_width: int, window_height: int):
        # Primer configuro el center_y de los stats
        lenght = len(self.lifes_list)
        left = self.lifes_list[0].center_x - (self.lifes_list[0].width * 0.5)
        self.attack_sprite.center_y = window_height - 70
        self.attack_sprite.left = left
        self.defence_sprite.center_y = window_height - 90
        self.defence_sprite.left = left

        self.experience_sprite.center_x = window_width - 100
        self.experience_sprite.center_y = window_height - 40
        self.experience_text.x = self.experience_sprite.left - 30
        self.experience_text.y = window_height - 50

        # Configuro el center_y de los corazones
        for i in range(lenght):
            if i < lenght:
                self.lifes_list[i].center_y = window_height - 30

    def draw(self) -> None:
        self.sprite_list.draw(pixelated=True)
        self.lifes_list.draw(pixelated=True)
        self.experience_text.draw()
