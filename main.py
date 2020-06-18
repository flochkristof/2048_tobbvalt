import numpy as np
import cv2
from control import *
from game import *


def main():

    # intro
    displayIntro()

    # játék létrehozása
    game = board_game_2048()

    # kezdetben nincs rögzítve a háttér amivel a kép szűrését végezzük
    backround_captured = False
    score = 0

    # webkamera rögzítése
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while not game.is_game_over():
        # beolvasás képkockántként, tükrözés, croppolás
        ret, cam_frame = cam.read()
        cam_frame = cv2.flip(cam_frame, 1)
        roi = crop_roi(cam_frame)

        # ha már rögzítésre került a háttér ez az ág fut le
        if backround_captured:
            # háttér kiszűrése
            hand_cam = filter_backround(roi, backround)

            # a mutatóujj koordinájái
            point = fingertip(hand_cam)

            # mogzás
            d = directions(point)
            if d is not None:
                game.board = main_loop(game.board, d)

            # pontok rajzolása ujjhegyre
            hand_cam = displayDots(hand_cam)

            # megjelenítés
            frame = displayGame(game.board, hand_cam)
            cv2.imshow("2048", frame)

        # még nincs rögzítve háttér
        else:
            merged = cv2.merge((roi, roi, roi))
            frame = displayGame(game.board, merged)
            cv2.imshow("2048", frame)

        # billenytűparancsok
        k = cv2.waitKey(10)
        # kilépés
        if k == 27:
            break
        # háttér rögzítése
        elif k == ord("c"):
            backround = roi
            backround_captured = True

    # gamover felirat
    frame = gameOverFrame(frame)
    cv2.imshow("2048", frame)

    # kilépő menü
    while 1:
        k = cv2.waitKey(0)
        if k == ord("r"):
            resetScore()
            main()
            break
        elif k == 27:
            cam.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
