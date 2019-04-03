import sys
import pygame
import game_controller

pygame.init()

game_controller = game_controller.GameController()

clock = pygame.time.Clock()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game_controller.handle_mouse_button_down(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            game_controller.handle_mouse_button_up(event.pos, event.button)

    game_controller.check_state()

    time = clock.tick(15)
    pygame.display.update()
