from typing import Optional
import collections
import enum
import pprint
import random
import sys

class CellValue(enum.StrEnum):
    EMPTY = '-'
    X = 'X'
    O = 'O'

    def __repr__(self):
        return self.value


Cell = collections.namedtuple("Cell", ["x", "y"])


class Board:

    def __init__(self, n: int, m: int):
        self.n = n
        self.m = m
        self.board = [[CellValue.EMPTY] * n for _ in range(m)] 
        self.move_count = 0

    def __repr__(self):
        return "\n".join(" ".join(x) for x in self.board)

    def check_win(self, winlen: int,
                  lastmove: "Cell",
                  value: "CellValue") -> list[Optional["Cell"]]:
        # column
        directions = [ (0, 1), (1, 0), (1, 1), (-1, 1) ]

        for dx, dy in directions:
            count = 1

            nx = lastmove.x + dx
            ny = lastmove.y + dy
            while (0 <= nx < self.n and 0 <= ny < self.m and self.board[nx][ny] == value):
                count += 1
                nx += dx
                ny += dy

            nx = lastmove.x - dx
            ny = lastmove.y - dy
            while (0 <= nx < self.n and 0 <= ny < self.m and self.board[nx][ny] == value):
                count += 1
                nx -= dx
                ny -= dy

            if count >= winlen:
                return True
            
        return False

    def hasMoreMoves(self):
        return self.move_count <  self.n * self.m

    def new_move(self, cell: "Cell", value: "CellValue") -> bool:
        if (0 <= cell.x < self.n and 0 <= cell.y < self.m and 
            self.board[cell.x][cell.y] == CellValue.EMPTY):
            self.board[cell.x][cell.y] = value
            self.move_count += 1
            return True
        return False
        


class BasePlayer:

    def __init__(self, value: "CellValue"):
        self.value = value

    def make_move(self, board: "Board") -> "Cell":
        raise NotImplementedError


class ConsoleHumanPlayer(BasePlayer):

    def __init__(self, value: "CellValue"):
        super().__init__(value)

    def make_move(self, board: "Board") -> "Cell":
        move = None
        while move is None:
            print(f"What is your move? (Format: x, y)")
            user_input = input()
            coordinates = user_input.split(", ")
            if len(coordinates) != 2:
                print(f"Invalid move.")
                continue
            move = Cell(*map(int, coordinates))
            if not board.new_move(move, self.value):
                move = None
                continue
        return move


class RandomAIPlayer(BasePlayer):

    def __init__(self, value: "CellValue"):
        super().__init__(value)

    def make_move(self, board: Board) -> "Cell":
        move = None
        while move is None:
            x = random.randint(0, board.n)
            y = random.randint(0, board.m)
            move = Cell(x, y)
            if not board.new_move(move, self.value):
                move = None
                continue
        return move
    

class Game:

    def __init__(self, board: "Board", players: list["BasePlayer"], winlen: int):
        self.board = board
        self.players = players
        self.winlen = winlen

    def start_game(self):
        player_idx = 0
        moves = 0

        while moves < self.board.n * self.board.m:
            player = self.players[player_idx]
            print(f"It's {player.value}'s turn.")
            print(f"Current board:\n{self.board}")

            move = player.make_move(self.board)
            print(f"Player moved into {move.x}, {move.y}")

            if self.board.check_win(self.winlen, move, player.value):
                print(f"Player {player.value} won!")
                break

            player_idx = (player_idx + 1) % 2
            moves += 1

        if not self.board.hasMoreMoves():
            print("No more moves: it's a tie!")

        print(f"Final board:\n{self.board}")


def main(argv: list[str]):
    if len(argv) != 4:
        print(f"Usage: {argv[0]} row columns winlen, got {argv=}", file=sys.stderr)
        sys.exit(1)
    board = Board(int(argv[1]), int(argv[2]))
    players = [ConsoleHumanPlayer(CellValue.X), RandomAIPlayer(CellValue.O)]
    game = Game(board, players, int(argv[3]))
    game.start_game()


if __name__ == '__main__':
    main(sys.argv)
