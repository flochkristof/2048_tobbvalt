# 2048_tobbvalt
A BME "Többváltozós analízis mérnöki alkalmazásai" tárgyra készített projektünk repoja.

## Játék futtatása
A repo leszedése után telepíteni kell a szükséges  kiegészítő könytárakat (lásd: requirements.txt). Ha ez megvan a main.py file-t kell futtatni pythonnal. 

## Irányítás

A program lényege, hogy a játék vezérlése kvázi érintésmentes, a mozgatási parancsokat webkamera segítségével, mutogatással tudjuk bevinni. Mivel a kéz követését a kamera képből a háttér szűrésével érjük el, törekedni kell a lehető legstatikusabb háttérre. Ha ez megvan a ‘c’ billentyűvel lehet rögzíteni. Ha jól csináltuk a teljes kép elsötétül, viszont benyúlva a képbe a kezünk lenyomata tisztán láthatóvá válik, a kinyújtott ujjunk végére a program kék pöttyöket rajzol. Eztán a játékot a mutatóujjunk mozgatásával lehet irányítani. Fontos, hogy törekedi kell arra, hogy a vezérlő kéz végig a képben maradjon inkább az ujj  mozogjon. Mivel a rendszer csak a gyors swipe-okat detektálja, lassan nyugodtan lehet mozgatni a kezet nem fogja elrontani a játékot. Néha hirtelen fényviszony-változásnál hajlamos elveszteni a háttér beállítást ilyenkor a ‘c’ dombbal resetelhető a háttér.
