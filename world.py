# import pygame
from items import Item
from character import Character
import constants


class World():
    def __init__(self):
        self.map_tiles = []
        self.obstacle_tiles = []
        self.exit_tile = None
        self.item_list = []
        self.player = None
        self.character_list = []

    def process_data(self, data, tile_list, item_images, mob_animations):
        self.level_length = len(data)
        # itirate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                image = tile_list[tile]
                image_rect = image.get_rect()
                image_x = x * constants.TILE_SIZE
                image_y = y * constants.TILE_SIZE
                image_rect.center = (image_x, image_y)
                tile_data = [image, image_rect, image_x, image_y]
                
                if tile <= 18:
                    self.obstacle_tiles.append(tile_data)
                elif tile == 21:
                    self.exit_tile = tile_data
                elif tile == 29:
                    coin = Item(image_x, image_y, 0, item_images[0])
                    self.item_list.append(coin)
                    tile_data[0] = tile_list[19]
                elif tile == 28:
                    medkit = Item(image_x, image_y, 1, [item_images[1]])
                    self.item_list.append(medkit)
                    tile_data[0] = tile_list[19]
                elif tile == 23:
                    player = Character(image_x, image_y, 100, mob_animations, 0, False, 1)
                    self.player = player
                    tile_data[0] = tile_list[19]               
                elif tile >= 24 and tile <= 27:
                    enemy = Character(image_x, image_y, 100, mob_animations, tile - 23, True, 2.5)
                    self.character_list.append(enemy)
                    tile_data[0] = tile_list[19]
                # add image data to main tiles list
                if tile >= 0:
                    self.map_tiles.append(tile_data)

    def update(self, screen_scroll):
        for tile in self.map_tiles:
            tile[2] += screen_scroll[0]
            tile[3] += screen_scroll[1]
            tile[1].center = (tile[2], tile[3])

    def draw(self, surface):
        for tile in self.map_tiles:
            surface.blit(tile[0], tile[1]) # 0: image; 1: rect