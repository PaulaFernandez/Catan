from game_state import GameState
import config

def play_game():
    game = GameState()

    while game.game_phase != config.PHASE_END_GAME:
        move = game.players[game.player_turn].ai.move(game)
        game.ai_do_move(move)

#play_game()
