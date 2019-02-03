from game_state import GameState
from game_memory import GameMemory
import config

def play_game():
    game = GameState()
    game_memory = GameMemory(game.uuid)

    while game.game_phase != config.PHASE_END_GAME:
        player_moving = game.get_player_moving()
        move, posterior_probs, nn_state, player_moving = game.players[player_moving].ai.move(game)
        if player_moving > -1:
            game_memory.add_to_memory_states(player_moving, nn_state, posterior_probs)
        game.ai_do_move(move)

    game_result = []
    for p in range(4):
        game_result.append(game.ai_get_result(p))
    game_memory.add_game_result(game_result)

    game_memory.dump_to_file()

config.WIN_POINTS = 3
agents = [1]
games_played = 0

while games_played < config.SELF_PLAY_BATCH_SIZE:
    try:
        play_game()
        games_played += 1
    except Exception as e:
        with open('log.txt', 'a') as output:
            output.write(e)
