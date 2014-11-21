#!/usr/bin/python
import os
import math
import pygame
import tmx

data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data')


def get_texture(name):
    return pygame.image.load(os.path.join(data_path, 'textures', name))


def main():
    world_map = tmx.tmxreader.TileMapParser().parse_decode(os.path.join(data_path, 'test.tmx'))

    pygame.init()
    pygame.display.set_caption('test2allien, use arrow keys')
    pygame.display.set_icon(get_texture('tank-48.png'))
    screen_width = min(1024, world_map.pixel_width)
    screen_height = min(768, world_map.pixel_height)
    screen = pygame.display.set_mode((screen_width, screen_height))

    resources = tmx.helperspygame.ResourceLoaderPygame()
    resources.load(world_map)
    assert world_map.orientation == "orthogonal"
    renderer = tmx.helperspygame.RendererPygame()

    hero_pos_x = screen_width
    hero_pos_y = screen_height
    hero = create_hero(hero_pos_x, hero_pos_y)

    hero_width = hero.rect.width
    hero_height = 5

    cam_world_pos_x = hero.rect.centerx
    cam_world_pos_y = hero.rect.centery

    renderer.set_camera_position_and_size(cam_world_pos_x, cam_world_pos_y, screen_width, screen_height)

    sprite_layers = tmx.helperspygame.get_layers_from_map(resources)
    sprite_layers = [layer for layer in sprite_layers if not layer.is_object_group]
    sprite_layers[1].add_sprite(hero)

    clock = pygame.time.Clock()
    running = True
    speed = 0.075

    pygame.time.set_timer(pygame.USEREVENT, 1000)

    while running:
        dt = clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                print("fps: ", clock.get_fps())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        direction_x = pygame.key.get_pressed()[pygame.K_RIGHT] - pygame.key.get_pressed()[pygame.K_LEFT]
        direction_y = pygame.key.get_pressed()[pygame.K_DOWN]  - pygame.key.get_pressed()[pygame.K_UP]

        # make sure the hero moves with same speed in all directions (diagonal!)
        dir_len = math.hypot(direction_x, direction_y)
        dir_len = dir_len if dir_len else 1.0

        # update position
        step_x = speed * dt * direction_x / dir_len
        step_y = speed * dt * direction_y / dir_len
        step_x, step_y = check_collision(hero_pos_x, hero_pos_y, step_x, step_y, hero_width, hero_height,
                                         sprite_layers[3])
        hero_pos_x += step_x
        hero_pos_y += step_y
        hero.rect.midbottom = (hero_pos_x, hero_pos_y)

        renderer.set_camera_position(hero.rect.centerx, hero.rect.centery)

        screen.fill((0, 0, 0))

        for sprite_layer in sprite_layers:
            if sprite_layer.is_object_group:
                continue
            else:
                renderer.render_layer(screen, sprite_layer)

        pygame.display.flip()


def create_hero(start_pos_x, start_pos_y):
    image = get_texture('tank-64.png')
    rect = image.get_rect()
    rect.midbottom = (start_pos_x, start_pos_y)
    return tmx.helperspygame.SpriteLayer.Sprite(image, rect)


#  -----------------------------------------------------------------------------

# unused in this demo, just here to show how you could check for collision!
def is_walkable(pos_x, pos_y, coll_layer):
    """
    Just checks if a position in world coordinates is walkable.
    """
    tile_x = int(pos_x // coll_layer.tilewidth)
    tile_y = int(pos_y // coll_layer.tileheight)

    if coll_layer.content2D[tile_y][tile_x] is None:
        return True
    return False


#  -----------------------------------------------------------------------------

def check_collision(hero_pos_x, hero_pos_y, step_x, step_y, \
                    hero_width, hero_height, coll_layer):
    """
    Checks collision of the hero against the world. Its not the best way to
    handle collision detection but for this demo it is good enough.

    :Returns: steps to add to heros current position.
    """
    # create hero rect
    hero_rect = pygame.Rect(0, 0, hero_width, hero_height)
    hero_rect.midbottom = (hero_pos_x, hero_pos_y)

    # find the tile location of the hero
    tile_x = int((hero_pos_x) // coll_layer.tilewidth)
    tile_y = int((hero_pos_y) // coll_layer.tileheight)

    # find the tiles around the hero and extract their rects for collision
    tile_rects = []
    for diry in (-1, 0, 1):
        for dirx in (-1, 0, 1):
            if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                tile_rects.append(coll_layer.content2D[tile_y + diry][tile_x + dirx].rect)

    # save the original steps and return them if not canceled
    res_step_x = step_x
    res_step_y = step_y

    # x direction, floor or ceil depending on the sign of the step
    step_x = special_round(step_x)

    # detect a collision and dont move in x direction if colliding
    if hero_rect.move(step_x, 0).collidelist(tile_rects) > -1:
        res_step_x = 0

    # y direction, floor or ceil depending on the sign of the step
    step_y = special_round(step_y)

    # detect a collision and dont move in y direction if colliding
    if hero_rect.move(0, step_y).collidelist(tile_rects) > -1:
        res_step_y = 0

    # return the step the hero should do
    return res_step_x, res_step_y


#  -----------------------------------------------------------------------------

def special_round(value):
    """
    For negative numbers it returns the value floored,
    for positive numbers it returns the value ceiled.
    """
    # same as:  math.copysign(math.ceil(abs(x)), x)
    # OR:
    # ## versus this, which could save many function calls
    # import math
    # ceil_or_floor = { True : math.ceil, False : math.floor, }
    # # usage
    # x = floor_or_ceil[val<0.0](val)

    if value < 0:
        return math.floor(value)
    return math.ceil(value)

#  -----------------------------------------------------------------------------

if __name__ == '__main__':
    main()


