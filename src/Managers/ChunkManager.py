from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict
from characters.Enemy import Enemy
from arcade import TileMap, Sprite, SpriteList
from items.Item import Item


@dataclass
class Chunk:
    sprites: Dict[str, list] = field(
        default_factory=lambda: {
            "mineral": [],
            "interact": [],
            "floor": [],
            "copes": [],
            "objects": [],
            "items": [],
            "enemy": [],
        }
    )


class Chunk_Manager:
    def __init__(self, chunk_size_x: int, chunk_size_y: int) -> None:
        self.chunk_size_x = chunk_size_x
        self.chunk_size_y = chunk_size_y
        self.chunks: Dict[tuple[int, int], Chunk] = {}
        self.is_world_loaded = False

    @lru_cache(maxsize=100)
    def get_chunk_key(self, x: float, y: float) -> tuple[int, int]:
        return (int(x // self.chunk_size_x), int(y // self.chunk_size_y))

    def get_chunk(self, key: tuple[int, int]) -> Chunk:
        if key not in self.chunks:
            self.chunks[key] = Chunk()
        chunk = self.chunks[key]
        return chunk

    def get_nearby_chunks(self, center_key: tuple[int, int]):
        col, row = center_key
        return [
            (col + dx, row + dy)
            for dx in range(-1, 2)
            for dy in range(-1, 2)
            if (col + dx, row + dy) in self.chunks
        ]

    def update_enemy_key(self, enemy: Enemy, kill: bool = False):
        if kill:
            if enemy in self.chunks[enemy.chunk_key].sprites["enemy"]:
                self.chunks[enemy.chunk_key].sprites["enemy"].remove(enemy)
            return

        chunk_key = self.get_chunk_key(enemy.center_x, enemy.center_y)
        if enemy.chunk_key == chunk_key:
            return
        # Cambio de chunk al enemigo:
        self.chunks[enemy.chunk_key].sprites["enemy"].remove(enemy)
        chunk = self.get_chunk(chunk_key)
        chunk.sprites["enemy"].append(enemy)
        enemy.chunk_key = chunk_key

    def drop_item(self, item: Item):
        self.assign_sprite_chunk(item, "items")

    def load_world(
        self,
        tilemap: TileMap,
        ignored_layers: list[str] | None = None,
    ) -> None:
        """Función para cargar los tiles del tilemap en sus respectivos chunks"""
        for layer, sprite_list in tilemap.sprite_lists.items():
            if ignored_layers and layer.capitalize() in ignored_layers:
                continue
            layer_key = layer.lower()
            for sprite in sprite_list:
                key = self.get_chunk_key(sprite.center_x, sprite.center_y)

                chunk = self.get_chunk(key)
                if layer_key in chunk.sprites:
                    self.chunks[key].sprites[layer_key].append(sprite)
        self.is_world_loaded = True

    def assign_sprite_chunk(self, sprite: Sprite, sprite_type: str) -> None:
        """Se asigna una chunk_key a un sprite específico"""
        chunk_key = self.get_chunk_key(sprite.center_x, sprite.center_y)
        if hasattr(sprite, "chunk_key"):
            setattr(sprite, "chunk_key", chunk_key)
        chunk = self.get_chunk(chunk_key)
        if sprite_type in chunk.sprites:
            # Cargo el sprite en el chunk especificado
            self.chunks[chunk_key].sprites[sprite_type].append(sprite)

    def batch_assign_sprites(self, sprite_list: SpriteList, sprite_type: str):
        """Asignación de chunk_key a toda una SpriteList"""
        for sprite in sprite_list:
            self.assign_sprite_chunk(sprite, sprite_type)
