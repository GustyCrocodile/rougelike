import pygame
import weapon
import constants
import math

class Character():
    def __init__(self, x, y, health, mob_animations, char_type, boss, size):
        self.char_type = char_type
        self.boss = boss
        self.score = 0
        self.flip = False
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.action = 0  # 0: idle; 1: run
        self.running = False
        self.health = health
        self.alive = True
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.last_attack = pygame.time.get_ticks()
        self.stunned = False

        self.image = self.animation_list[self.action][self.frame_index]
        if char_type == 0:
            self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * size, constants.TILE_SIZE * size)
        else:
            self.rect = pygame.Rect(0, 0, (constants.ENEMY_TILE_X * size ), (constants.ENEMY_TILE_Y * size))
            # self.rect 
        self.rect.center = (x, y)

    def move(self, dx, dy, obstacle_tiles, exit_tile=None):
        screen_scroll = [0, 0]
        level_complete = False
        self.running = False

        if dx != 0 or dy != 0:
            self.running = True
        
        mouse_pos = pygame.mouse.get_pos()  
        if mouse_pos[0] < self.rect.centerx:
             self.flip = True
        if mouse_pos[0] > self.rect.centerx:
            self.flip = False

        # control diagonal speed
        if dx != 0 and dy != 0:
            dx = dx * (math.sqrt(2)/(2))
            dy = dy * (math.sqrt(2)/(2))
        
        # check for collision with map in x direction
        self.rect.x += dx
        for obstacle in obstacle_tiles:
            # check for collisions
            if obstacle[1].colliderect(self.rect):
                # check which side
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right
    
        # check for collision with map in y direction
        self.rect.y += dy
        for obstacle in obstacle_tiles:
            # check for collisions
            if obstacle[1].colliderect(self.rect):
                # check which side
                if dy > 0:
                    self.rect.bottom = obstacle[1].top
                if dy < 0:
                    self.rect.top = obstacle[1].bottom

        # logic applicable to player
        if self.char_type == 0:
            # check collision with the exit ladder
            if exit_tile[1].colliderect(self.rect):
                # ensure that the player is on the center of the ladder
                exit_dist = math.sqrt(((self.rect.centerx - exit_tile[1].centerx) ** 2) + ((self.rect.centery - exit_tile[1].centery )** 2))
                if exit_dist < 25:
                    level_complete = True
            # update scroll
            # move camer right and left
            if self.rect.right > (constants.SCREEN_WIDTH - constants.SCROLL_THRESH):
                screen_scroll[0] = (constants.SCREEN_WIDTH - constants.SCROLL_THRESH) - self.rect.right
                self.rect.right = constants.SCREEN_WIDTH - constants.SCROLL_THRESH
            if self.rect.left < constants.SCROLL_THRESH:
                screen_scroll[0] = constants.SCROLL_THRESH - self.rect.left
                self.rect.left = constants.SCROLL_THRESH

            # move camer right and left
            if self.rect.bottom > (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH):
                screen_scroll[1] = (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH) - self.rect.bottom
                self.rect.bottom = constants.SCREEN_HEIGHT - constants.SCROLL_THRESH
            if self.rect.top < constants.SCROLL_THRESH:
                screen_scroll[1] = constants.SCROLL_THRESH - self.rect.top
                self.rect.top = constants.SCROLL_THRESH


        return screen_scroll, level_complete

    def ai(self, player, obstacle_tiles, screen_scroll, fireball_image):
        """
        Reposition mobs based on screen scroll
        """
        clipped_line = ()
        stunned_cooldown = 100
        ai_dx = 0
        ai_dy = 0
        fireball = None

        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # create a line of sight from the enemy to the player
        line_of_sight = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
        # check if line of sight passes through an obstacle
        for obstacle in obstacle_tiles:
            if obstacle[1].clipline(line_of_sight):
                clipped_line = obstacle[1].clipline(line_of_sight)

        # check distance to player
        dist = math.sqrt(((self.rect.centerx - player.rect.centerx) ** 2) + ((self.rect.centery - player.rect.centery) ** 2))
        if not clipped_line and dist > constants.RANGE:
            if self.rect.centerx > player.rect.centerx:
                ai_dx = -constants.ENEMY_SPEED
            if self.rect.centerx < player.rect.centerx:
                ai_dx = constants.ENEMY_SPEED
            if self.rect.centery > player.rect.centery:
                ai_dy = -constants.ENEMY_SPEED
            if self.rect.centery < player.rect.centery:
                ai_dy = constants.ENEMY_SPEED
        
        if self.alive:
            if not clipped_line and not self.stunned:
                # move towards player 
                self.move(ai_dx, ai_dy, obstacle_tiles)
                # attack player
                if not dist < constants.ATTACK_RANGE and player.hit == False and not clipped_line:
                    player.health -= constants.ENEMY_MELEE_DMG
                    player.hit = True
                    player.last_hit = pygame.time.get_ticks()
                # boss enemy shoot fireballs
                fireball_cooldown = 700
                if self.boss:
                    if dist < 500:
                        if pygame.time.get_ticks() - self.last_attack >= fireball_cooldown:
                            fireball = weapon.Fireball(fireball_image, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
                            self.last_attack = pygame.time.get_ticks()
        # check if hit
        if self.hit == True:
            self.update_action(2)
            self.hit = False
            self.last_hit = pygame.time.get_ticks()
            self.stunned = True
            self.running = False
        
        if (pygame.time.get_ticks() - self.last_hit > stunned_cooldown):
            self.stunned = False
        
        if ai_dx < 0:
             self.flip = True
        if ai_dx > 0:
            self.flip = False

        return fireball

    def update(self):
        # check if char has died
        if self.health <= 0:
            self.health = 0
            self.alive = False

        # timer to reset player taking a hit
        hit_cooldown = 1000
        if self.char_type == 0:
            if self.hit == True and (pygame.time.get_ticks() - self.last_hit > hit_cooldown):
                self.hit = False
       
        # check what action player is performing
        if self.running == True:
            self.update_action(1) # 1: run
        else:
            self.update_action(0) # 0: idle
        
        if self.stunned == True:
            self.update_action(2)

        animation_cooldown = 110
        # handle animation
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if animation has finished
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the action is different
        if new_action != self.action:
            self.action = new_action
            # update animation settings (frame)
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        if self.alive:
            flipped_image = pygame.transform.flip(self.image, self.flip, False)
            if self.char_type == 0:
                surface.blit(flipped_image, (self.rect.x - constants.SCALE*constants.PLAYER_OFFSET_X, self.rect.y - constants.SCALE*constants.PLAYER_OFFSET_Y))
            else:    
                surface.blit(flipped_image, self.rect)
            pygame.draw.rect(surface, constants.RED, self.rect, 1)