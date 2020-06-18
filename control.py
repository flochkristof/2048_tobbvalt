import cv2
import numpy as np

# globális változók
coordinates = []
mem = 99
reset = 0


def filter_backround(backround, frame):
    """Paraméterként megkapja az aktiális képkockát és 
    az előre rögzített hátteret, kiemeli a különbséget"""

    # két bemeneti képkocka különbsége
    frame = cv2.absdiff(backround, frame)

    # formázás
    ret, thresh = cv2.threshold(frame, 10, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.erode(thresh, kernel, iterations=3)
    thresh = cv2.dilate(thresh, kernel, iterations=10)

    return thresh


def crop_roi(frame):
    """A kamera által rögzített frame számunkra lényeges részét vágja ki"""

    # méretek lekérdezése
    h, w, _ = frame.shape

    # kivágás
    roi = frame[0 : int(0.8 * h), int(0.5 * w) : w]

    return cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)


def centerpoint(frame):
    """A kép súlypontját határozza meg"""

    # opencv beépített függvényéből kinyerhető az x, y koordináta
    M = cv2.moments(frame)
    if M["m00"] != 0:
        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])
        return x, y
    else:
        return None


def farthest(deflects, contour, center):
    """Megkeresi a középponttól legmesszebb levő convexity deflect-et, 
    ennek koordinátáival tér vissza"""

    if center is not None and deflects is not None:
        # pontok meghatározása
        d = deflects[:, 0][:, 0]
        cx, cy = center
        x = np.array(contour[d][:, 0][:, 0], dtype=np.float)
        y = np.array(contour[d][:, 0][:, 1], dtype=np.float)

        # tavolság számítása
        dx = cv2.pow(cv2.subtract(x, center[0]), 2)
        dy = cv2.pow(cv2.subtract(y, center[1]), 2)
        distance = cv2.sqrt(cv2.add(dx, dy))

        # visszatérés a legmesszebbi ponttal
        max_distance = np.argmax(distance)
        if max_distance < len(d):
            f_deflect = d[max_distance]
            return tuple(contour[d[max_distance]][0])
        else:
            return None
    else:
        return None


def fingertip(frame):
    """Az aktuális képkockán látható kéz mutatóujjának koordinátáit határozza meg"""

    # a legnagyobb kontúrvonal meghatározása
    contours, hierarchy = cv2.findContours(
        frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    max_contour = max(contours, key=cv2.contourArea, default=None)

    # a súlypont
    center = centerpoint(frame)

    if max_contour is not None:

        # a kontúr legtávolabbi pontja a súlyponttól
        hull = cv2.convexHull(max_contour, returnPoints=False)
        deflects = cv2.convexityDefects(max_contour, hull)

        return farthest(deflects, max_contour, center)

    else:
        return None


def displayDots(frame):
    """Kirajzolja az ujjhegy pályáját az eltárolt koordinátákból"""
    frame = cv2.merge((frame, frame, frame))
    for i in range(len(coordinates)):
        cv2.circle(frame, coordinates[i], 10, [255, 0, 0], -1)
    return frame


def directions(point):
    """Rögzíti az átadott koordinátákat meghatározza belőlük a mozgás irányát, kiadja a parancsot billentyűzetre"""

    # szükséges, hogy egymás után ne hívódjon meg többször ugyanaz az irány
    global mem
    global reset

    # ha a program talál pontot azt egy listában rögzíti
    if point is not None:
        if len(coordinates) < 20:
            coordinates.append(point)
        else:
            # mindig fix 20 elemű a lista, a 20 legfrissebb elemmel
            coordinates.pop(0)
            coordinates.append(point)

            # kis idő elteltével lehessen egymás után ugyanazt az irányt hívni
            reset += 1
            if reset > 150:
                mem = 99
                reset = 0

            # koordinátát kettébontva 2 csoportba meghatározhatók a csoportok súlypontjai
            Ax = 0
            Ay = 0
            Bx = 0
            By = 0
            for i in range(0, 10, 1):
                Ax += coordinates[i][0] / 10
                Ay += coordinates[i][1] / 10
            for i in range(10, 20, 1):
                Bx += coordinates[i][0] / 10
                By += coordinates[i][1] / 10

            # a súlypontokból pedig már számolható az elmozdulás
            dx = Bx - Ax
            dy = By - Ay

            # kritikus határ ami felett az elmozdulás irányát vizsgáljuk
            if np.sqrt(dx ** 2 + dy ** 2) > 50:

                # vízszintes mozgás a dominánsabb
                if abs(dx) >= abs(dy):
                    if (dx >= 0) and (mem != 2):
                        # print("jobbra")
                        mem = 2
                        return 2

                    elif (dx < 0) and (mem != 0):
                        # print("balra")
                        mem = 0
                        return 0

                # függőleges mozgás dominál
                else:
                    if (dy >= 0) and (mem != 3):
                        # print("le")
                        mem = 3
                        return 3

                    elif (dy < 0) and (mem != 1):
                        # print("fel")
                        mem = 1
                        return 1
    return None
