import numpy as np
from random import randint, random
import cv2
import time

# globális változók
font = cv2.FONT_HERSHEY_SIMPLEX
score = 0

# színek rögzítése a megjelenítéshez
BLACK = (0, 0, 0)
RED = (54, 67, 244)
PINK = (99, 30, 234)
PURPLE = (176, 39, 156)
DEEP_PURPLE = (183, 58, 103)
BLUE = (243, 150, 33)
TEAL = (136, 150, 0)
L_GREEN = (74, 195, 139)
GREEN = (80, 175, 60)
ORANGE = (0, 152, 255)
DEEP_ORANGE = (34, 87, 255)
BROWN = (72, 85, 121)


colour_dict = {
    0: BLACK,
    2: RED,
    4: PINK,
    8: PURPLE,
    16: DEEP_PURPLE,
    32: BLUE,
    64: TEAL,
    128: L_GREEN,
    256: GREEN,
    512: ORANGE,
    1024: DEEP_ORANGE,
    2048: BROWN,
}


def getColour(i):
    """A paraméterként átadott értékhez 
    tartozó színnel tér vissza"""
    return colour_dict[i]


class board_game_2048:
    """Osztály a játék meghívására"""

    def __init__(self):
        self.board = np.zeros((4, 4), dtype=np.int)
        self.game_over = False
        fill_cell(self.board)
        fill_cell(self.board)

    def move(self, direction):
        pass

    def is_game_over(self):
        """Vizsgálja, hogy van-e még lehetséges mozgás"""
        for i in range(0, 4 ** 2):
            if self.board[floor(i / 4)][i % 4] == 0:
                return False

        for i in range(0, 4):
            for j in range(0, 4 - 1):
                if self.board[i][j] == self.board[i][j + 1]:
                    return False
                elif self.board[j][i] == self.board[j + 1][i]:
                    return False
        return True


def floor(n):
    """Az is_game_over() metódus használja"""
    return int(n - (n % 1))


def fill_cell(board):
    """Random helyre számok beszúrása a táblára"""
    i, j = (board == 0).nonzero()
    if i.size != 0:
        rnd = randint(0, i.size - 1)
        board[i[rnd], j[rnd]] = 2 * ((random() > 0.9) + 1)


def move_left(col):
    """Elvégzi a mozgatás során az összevonásokat, 
    növeli a scoret"""
    global score
    new_col = np.zeros((4), dtype=col.dtype)
    j = 0
    previous = None
    for i in range(col.size):
        if col[i] != 0:  # a szám nullától különböző
            if previous == None:
                previous = col[i]
            else:
                if previous == col[i]:
                    new_col[j] = 2 * col[i]
                    score += col[i]
                    j += 1
                    previous = None
                else:
                    new_col[j] = previous
                    j += 1
                    previous = col[i]
    if previous != None:
        new_col[j] = previous
    return new_col


def move(board, direction):
    """Mozgatást végzi, megadott irányban"""
    # 0: bal, 1: fel, 2: jobb, 3: le

    rotated_board = np.rot90(board, direction)
    cols = [rotated_board[i, :] for i in range(4)]
    new_board = np.array([move_left(col) for col in cols])

    return np.rot90(new_board, -direction)


def main_loop(board, direction):
    """Meghívja a mozgató függvényt, vizsgálja, 
    hogy a mozgatás sikeres-e, cellát tölt"""
    new_board = move(board, direction)
    moved = False
    if (new_board == board).all():
        # move is invalid
        pass
    else:
        moved = True
        fill_cell(new_board)

    return new_board


def displayGame(board, cam):
    """Létrehozza az aktuális megjelenítendő framet"""
    global score

    # üres kép
    frame = 50 * np.ones(shape=[420, 600, 3], dtype=np.uint8)

    # játéktér
    for i in range(0, 4, 1):
        for j in range(0, 4, 1):
            cv2.rectangle(
                frame,
                (i * 80 + 20, j * 80 + 80),
                ((i + 1) * 80 + 20, (j + 1) * 80 + 80),
                getColour(board[j][i]),
                -1,
            )
            if board[j][i] != 0:
                text = str(board[j][i])
                textsize = cv2.getTextSize(text, font, 1, 1)[0]
                cv2.putText(
                    frame,
                    text,
                    (
                        int(i * 80 + 60 - textsize[0] / 2),
                        int(j * 80 + 120 + textsize[1] / 2),
                    ),
                    font,
                    1,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
    # kamera
    frame[0:320, 360:600] = cv2.resize(cam, (240, 320))

    # menü
    cv2.rectangle(frame, (360, 320), (600, 420), (0, 0, 0), -1)
    cv2.putText(
        frame, "'ESC'-exit", (370, 350), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA
    )
    cv2.putText(
        frame,
        "'c'-capture/reset",
        (370, 380),
        font,
        0.8,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame, "backround", (418, 400), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA
    )

    # score
    cv2.rectangle(frame, (20, 20), (340, 60), (0, 0, 0), -1)
    text = "Score: " + str(score)
    cv2.putText(
        frame, text, (30, 50), font, 0.8, (255, 255, 255), 1, cv2.LINE_AA,
    )
    return frame


def gameOverFrame(frame):
    """Ha véget ér a játék látrehozza a Game over framet"""
    # keret
    frame = cv2.blur(frame, (5, 5))
    cv2.rectangle(frame, (100, 100), (500, 320), (0, 0, 0), -1)
    cv2.rectangle(frame, (100, 100), (500, 320), (150, 150, 150), 10)

    # gameover
    text = "Game over!"
    textsize = cv2.getTextSize(text, font, 2, 3)[0]
    cv2.putText(
        frame,
        text,
        (300 - int(textsize[0] / 2), 165),
        font,
        2,
        (255, 255, 255),
        3,
        cv2.LINE_AA,
    )

    # score
    text = "Score:" + str(score)
    textsize = cv2.getTextSize(text, font, 1.25, 1)[0]
    cv2.putText(
        frame,
        text,
        (300 - int(textsize[0] / 2), 225),
        font,
        1.2,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    # restart
    text = "Press 'r' to restart!"
    textsize = cv2.getTextSize(text, font, 0.6, 1)[0]
    cv2.putText(
        frame,
        text,
        (300 - int(textsize[0] / 2), 270),
        font,
        0.6,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    # quit
    cv2.putText(
        frame, "'ESC'-Quit", (410, 310), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA
    )

    return frame


def displayIntro():
    # üres kép
    frame = 50 * np.ones(shape=[420, 600, 3], dtype=np.uint8)

    # cím
    text = "2048"
    textsize = cv2.getTextSize(text, font, 5, 15)[0]
    cv2.putText(
        frame,
        text,
        (300 - int(textsize[0] / 2), 200),
        font,
        5,
        (255, 255, 255),
        15,
        cv2.LINE_AA,
    )
    text = "Touchless Controll edition"
    textsize = cv2.getTextSize(text, font, 1, 2)[0]
    cv2.putText(
        frame,
        text,
        (300 - int(textsize[0] / 2), 240),
        font,
        1,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    # tovább
    text = "Press any key to continue..."
    textsize = cv2.getTextSize(text, font, 0.8, 1)[0]
    cv2.putText(
        frame,
        text,
        (300 - int(textsize[0] / 2), 340),
        font,
        0.8,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    # cred
    cv2.putText(
        frame,
        "Written by Balint Gyimes and Kristof Floch",
        (390, 410),
        font,
        0.3,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.imshow("2048", frame)
    cv2.waitKey(0)


# újraindításhoz
def resetScore():
    """Nulláza az elért pontokat"""
    global score
    score = 0
