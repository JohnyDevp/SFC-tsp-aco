## Autor

Jméno: Jan Holáň \
Mail: xholan11@stud.fit.vutbr.cz

## Popis

Tento projekt se zaměřuje na implementaci řešení problému TSP (Travelling Salesman Problem - problém obchodního cestujícího) pomocí algoritmu ACS (Ant Colony System), spadající pod rodinu optimalizačních algoritmů Ant Colony Optimization (ACO). Zajištěno je jak použití z příkazové řádky, tak ovládání skrz grafické uživatelské rozhraní.

## Soubory

-   **data** - adresář testovacími a ukázkovými daty. Soubory se stejným názvem, lišící se pouze v obsažení slova _edge_ nebo _node_, mohou být použity zároveň.
-   **src** - adresář se zdrojovými soubory
    -   **gui** - adresář s implementací grafického rozhranní (controller _řídí_ mainwindow)
    -   **acs** - knihovna implementující algoritmus pro problém TSP (Travelling Salesman Problem) řešený pomocí ACS (Ant Colony System)
    -   acstsp.py - skript pro použití knihovny _acs_ z příkazové řádky
    -   acstspgui.py - skript pro použití knihovny _acs_ skrz grafické rozhranní
-   install.sh - skript pro instalaci závislostí, nutných pro spuštění výše zmíněných skriptů a knihovny
-   install.sh - skript pro otestování funkčnosti knihovny _acs_ a skriptu _acstsp.py_ na dvou bězích algoritmu ACS
-   readme.md

## Zdroje

[https://people.idsia.ch/~luca/acs-ec97.pdf](https://people.idsia.ch/~luca/acs-ec97.pdf)
