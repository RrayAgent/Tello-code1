import pygame


def init():
    pygame.init()
    win = pygame.display.set_mode((400, 400))


def get_keys(key):
    ans = False
    for eva in pygame.event.get():
        pass
    key_input = pygame.key.get_pressed()
    my_key = getattr(pygame, 'K_{}'.format(key))
    if key_input[my_key]:
        ans = True
    pygame.display.update()
    return ans
