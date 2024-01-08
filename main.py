import pygame
import csv
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World
from button import Button

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

# create clock for maintaining frame rate
clock = pygame.time.Clock()


# define game vars
level = 1
total_levels = 10
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0, 0]

# define player movement vars
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# define font
font = pygame.font.Font("assets/fonts/not_jam.ttf", 20)
title_font = pygame.font.Font("assets/fonts/not_jam.ttf", 48)
 
def scale_img(image, scale):
    """
    helper function to scale image
    """
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))

# create a new cursor
pygame.mouse.set_visible(False)
cursor_img = scale_img(pygame.image.load("assets/images/crosshair.png").convert_alpha(), constants.CROSSHAIR_SCALE)
cursor_rect = cursor_img.get_rect()

# load music
# pygame.mixer.music.load("assets/audio/music.wav")
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1, 0.0, 5000)
shot_fx = pygame.mixer.Sound("assets/audio/shotgun2.wav")
shot_fx.set_volume(0.4)
hit_fx = pygame.mixer.Sound("assets/audio/hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)
hurt_fx = pygame.mixer.Sound("assets/audio/hurt.wav")
hurt_fx.set_volume(0.3)
fireball_fx = pygame.mixer.Sound("assets/audio/fireball.wav")
fireball_fx.set_volume(0.3)

# load button images
restart_img = scale_img(pygame.image.load("assets/images/buttons/restart.png").convert_alpha(), constants.BUTTON_SCALE)
start_img = scale_img(pygame.image.load("assets/images/buttons/start.png").convert_alpha(), constants.BUTTON_SCALE)
exit_img = scale_img(pygame.image.load("assets/images/buttons/quit.png").convert_alpha(), constants.BUTTON_SCALE)
resume_img = scale_img(pygame.image.load("assets/images/buttons/resume.png").convert_alpha(), constants.BUTTON_SCALE)

# load hearth images
health_images = []
for x in range(10):
    img = scale_img(pygame.image.load(f"assets/images/health/{x}.png").convert_alpha(), constants.HEALTH_SCALE)
    health_images.append(img)

# heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
# heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
# heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

# load coin images
coin_images = []
for x in range(4):
    img = scale_img(pygame.image.load(f"assets/images/items/coin_{x}.png").convert_alpha(), constants.ITEM_SCALE)
    coin_images.append(img)

# load potion image
medkit = scale_img(pygame.image.load("assets/images/items/medkit.png").convert_alpha(), constants.MEDKIT_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(medkit)

# load weapon images
shotgun_image = scale_img(pygame.image.load("assets/images/weapons/shotgun.png").convert_alpha(), constants.WEAPON_SCALE)
slug_image = scale_img(pygame.image.load("assets/images/weapons/slug.png").convert_alpha(), constants.SLUG_SCALE)
fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)

# load tilemap images
tile_list = []
for x in range(constants.TILE_TYPES):
    tile_image = pygame.image.load(f"assets/images/tiles/tile_{x}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    tile_list.append(tile_image)

# load character images
mob_animations = []
mob_types = ["bandit", "blue", "green", "red", "yellow"]

animation_types = ["idle", "run", "hit"]
for mob in mob_types:
    # load images
    animation_list = []
    frames = 4
    for animation in animation_types:
        if animation == "run":
            frames = 6
        elif animation == "idle":
            frames = 4
        elif animation == "hit":
            frames = 2
        temp_list = []
        for i in range(frames):
            img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            img = scale_img(img, constants.SCALE)
            temp_list.append(img)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)

# create empty tile list
world_data = []
for rows in range(constants.ROWS):
    r = [0] * constants.COLS
    world_data.append(r)

# load in level data and create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)


world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)


def draw_text(text, font, text_col, x, y):
    """
    Function for outputting text onto the screen
    """
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_info(health_images):
    """
    Function for displaying game info
    """
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50))

    # Have to Redo this
    # lives draw
    rounded_health = round(player.health/10)
    if rounded_health == 10:
        rounded_health -= 1
    screen.blit(health_images[rounded_health], (20, 0))
  
    # level
    draw_text("LEVEL: " + str(level), font, constants.WHITE, (constants.SCREEN_WIDTH / 2) - 35, 15)

    # show score
    draw_text(f"x{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 150, 15)


def reset_level():
    """Function reset level"""
    damage_text_group.empty()
    slug_group.empty()
    item_group.empty()
    fireball_group.empty()

    # create empty tile list
    data = []
    for rows in range(constants.ROWS):
        r = [-1] * constants.COLS
        data.append(r)
    return data


class DamageText(pygame.sprite.Sprite):
    """
    Damage text class
    """
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(str(damage), True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # repo based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # move dmg txt up
        self.rect.y -= 1
        # del the counter after a few seconds
        self.counter += 1
        if self.counter > 30:
            self.kill()


class ScreeFade():
    """Class for handling screen fade"""
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0 
    
    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1: # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (constants.SCREEN_WIDTH // 2 + self.fade_counter, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, constants.SCREEN_HEIGHT // 2 + self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        elif self.direction == 2: # vertical screen fade
            pygame.draw.rect(screen, self.colour, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= constants.SCREEN_WIDTH:
            fade_complete = True
        
        return fade_complete

# create player
# player = Character(400, 300, 30, mob_animations, 0)
player = world.player

# create players weapon
gun = Weapon(shotgun_image, slug_image)

# extract enemies from word data
enemy_list = world.character_list

# sprite groups
damage_text_group = pygame.sprite.Group()
slug_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 180, 25, 0, coin_images, True)
item_group.add(score_coin)
# add the items from the level data
for item in world.item_list:
    item_group.add(item)

# create screen fades
intro_fade = ScreeFade(1, constants.BLACK, 8)
death_fade = ScreeFade(2, constants.BLACK, 6)

# create button
start_button = Button(constants.SCREEN_WIDTH // 2 - 150, constants.SCREEN_HEIGHT // 2 - 50, start_img)
exit_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 + 50, exit_img)
restart_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 50, restart_img)
resume_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 20, resume_img)

run = True
while run:

    # framerate
    clock.tick(constants.FPS)
    if start_game == False:
        screen.fill(constants.MENU_BG)
        draw_text("Sandpit Shootout", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 250, 400)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    elif level == total_levels:
        screen.fill(constants.MENU_BG)
        draw_text("Sandpit Shootout", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 250, 100)
        draw_text("Victory", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 125, 200)
        draw_text(f"Coins collected: {player.score}", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 300, 300)
        if restart_button.draw(screen):
            death_fade.fade_counter = 0
            level = 1
            start_intro = True
            world_data = reset_level()
            # load in level data and create world
            with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                for x, row in enumerate(reader):
                    for y, tile in enumerate(row):
                        world_data[x][y] = int(tile)
            world = World()
            world.process_data(world_data, tile_list, item_images, mob_animations)
            player = world.player
            player.score = 0
            enemy_list = world.character_list
            score_coin = Item(constants.SCREEN_WIDTH - 100, 23, 0, coin_images, True)
            item_group.add(score_coin)
            # add the items from the level data
            for item in world.item_list:
                item_group.add(item)
        if exit_button.draw(screen):
            run = False
    else:
        if pause_game == True:
            screen.fill(constants.MENU_BG)
            draw_text("Sandpit Shootout", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 250, 200)
            draw_text("*PAUSED*", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 125, 300)

            if resume_button.draw(screen):
                pause_game = False
            if exit_button.draw(screen):
                run = False
        else:
            screen.fill(constants.BG)
            
            if player.alive:    
                # calculate player movement
                dx = 0
                dy = 0
                if moving_right == True:
                    dx = constants.SPEED
                if moving_left == True:
                    dx = -constants.SPEED
                if moving_up == True:
                    dy = -constants.SPEED
                if moving_down == True:
                    dy = constants.SPEED

                # move player
                screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)
                
                # update all objects
                world.update(screen_scroll)
                for enemy in enemy_list:
                    fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
                    if fireball:
                        fireball_group.add(fireball)
                        fireball_fx.play()
                    if enemy.alive:
                        enemy.update()
                    if enemy.alive == False and enemy.char_type != 0:
                        del enemy
                player.update()
                slug = gun.update(player)
                if slug:
                    slug_group.add(slug)
                    shot_fx.play()
                
                for slug in slug_group:
                    damage, damage_pos = slug.update(screen_scroll, world.obstacle_tiles, enemy_list)
                    if damage:
                        damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
                        damage_text_group.add(damage_text)
                        hit_fx.play()
                for fireball in fireball_group:
                    hit = fireball.update(screen_scroll, player, world.obstacle_tiles)
                    if hit:
                        hurt_fx.play()
                damage_text_group.update()
                item_group.update(screen_scroll, player, coin_fx, heal_fx) 
                # fireball_group.update(screen_scroll, player, world.obstacle_tiles)

            # draw player on screen
            world.draw(screen)
            for enemy in enemy_list:
                enemy.draw(screen)
                # print(enemy.type)
            player.draw(screen)
            gun.draw(screen)
            for slug in slug_group:
                slug.draw(screen)
            for fireball in fireball_group:
                fireball.draw(screen)
            damage_text_group.draw(screen)
            item_group.draw(screen)
            draw_info(health_images)
            score_coin.draw(screen)


            # check level complete
            if level_complete == True:
                start_intro = True
                level += 1
                world_data = reset_level()
                # load in level data and create world
                with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                world.process_data(world_data, tile_list, item_images, mob_animations)
                temp_hp = player.health
                temp_score = player.score
                player = world.player
                player.health = temp_hp
                player.score = temp_score
                enemy_list = world.character_list
                score_coin = Item(constants.SCREEN_WIDTH - 100, 23, 0, coin_images, True)
                item_group.add(score_coin)
                # add the items from the level data
                for item in world.item_list:
                    item_group.add(item)

            # show intro
            if start_intro == True:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            # show death screen
            if player.alive == False:
                if death_fade.fade():
                    draw_text("Game Over", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 200, 200)
                    draw_text(f"Score: {player.score}", title_font, constants.WHITE, constants.SCREEN_WIDTH // 2 - 150, 300)

                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        level = 1
                        start_intro = True
                        world_data = reset_level()
                        # load in level data and create world
                        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        world.process_data(world_data, tile_list, item_images, mob_animations)
                        player = world.player
                        player.score = 0
                        enemy_list = world.character_list
                        score_coin = Item(constants.SCREEN_WIDTH - 100, 23, 0, coin_images, True)
                        item_group.add(score_coin)
                        # add the items from the level data
                        for item in world.item_list:
                            item_group.add(item)
                    if exit_button.draw(screen):
                        run = False

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # take keyboard pressses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_ESCAPE:
                if pause_game == False:
                    pause_game = True
                else:
                    pause_game = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False

    cursor_rect.center = pygame.mouse.get_pos()  # update position 
    screen.blit(cursor_img, cursor_rect)


    pygame.display.update()

pygame.quit()