# Pokročilé  datové struktury a algoritmy

## Základní zdroje informací

Základním zdrojem informací je následující kniha (dále jen PLA):

MAREŠ, Martin a Tomáš VALLA. Průvodce labyrintem algoritmů. Praha: CZ.NIC, z.s.p.o., 2017. CZ.NIC. ISBN 978-80-88-168-19-5.

Knihu najdere v elektronické podobě na https://knihy.nic.cz/ a je k dispozici i v tištěné verzi za cca 280 Kč.

## Asymptotická složitost (Landauovy asymptotické notace), princip lokality

PLA: kapitola 2, viz také  https://cw.fel.cvut.cz/b182/_media/courses/b6b36dsa/dsa-3-slozitostalgoritmu.pdf, přehled jednotlivých typických i exotických tříd nabízí https://en.wikipedia.org/wiki/Time_complexity.

**důležité**: rozlišení mezí $0$, $\Omega$ a $\Theta$ notací: nejdůležitější je $\Theta$ notace, ale její odvození není pro některé algoritmy snadné či 
dokonce možné, využívá se tedy nejrestriktivnější dokazatelný horní odhad tj, $O$, v praxi 
se tento zápis uplatňuje i v případě, že existuje i odhad třídy $\Theta$, (v LPA se však využívá přesnější $\Theta$))

výpočetní model RAM, nastudujte a vyzkoušejte v praxi
(viz https://github.com/Jiri-Fiser/Pokrocile-datove-struktury-a-algoritmy/RAM)

**úkol:** vytvořte a odlaďte program pro některý triviální algoritmus pro vyhledávání a třídění pro RAM, a prakticky ověřte, že má předpokládanou časovou složitost

rozlišení mezi časovou složitostí pro nejlepší, průměrný a nejhorší případ (vstupu), prakticky osvětlit například na třídících a vyhledávacích algoritmech
(pozor nezaměňovat s horním a dolním odhadem)

pojem amortizovaná časová složitost (nafukovací pole, kapitola 9.1)

časová složitost rekurzivních algoritmů (PLA 10.4) = doporučuji až po seznámení se s rekurzivními algoritmy

problém mezipamětí (keší) a principu lokality není v LPA diskutován: je nutné znát funkci mezipamětí (proč fungují) a jak jsou závislé na tzv. lokalitě programu
(pojmy cache hit, cache miss, hit rate/ratio). Podívejte se především na https://en.wikipedia.org/wiki/Locality_of_reference.

## Datové  struktury:  základní principy, lineární datové struktury, hashovací tabulky (hashovací funkce), řídká pole

Při popisu je důležité pochopit, že datové struktury je vhodné popisovat jako tzv. abstraktní datové typy, tj. zaměřit se primárně na popis rozhraní tj. funkcí, které nad datovými strukturami pracují (včetně časové resp. prostorové složitosti). Abstraktní datové typy se podobají OOP třídám (ty jen rozšiřují jejich sémantiku). V rámci tohoto kutu je však nutné znát jejich implementaci (platí i pro další dvě kapitoly)

**Doporučuji proto vyzkoušet si implementaci hlavních datových struktur v podobě OOP tříd v Pythonu.**

* nafukovací pole (PLA 9.1), frota a zásobník (4.1) zkuste implementaci, problematická je především implementace fronty (klíčová je zde implementace tzv. cyklické fronty, viz opora)
* hashovací tabulky (11.3, 11.4)

v PLA nejsou detailně zpracovány spojové seznamy (jednosměrná a obousměrný) a representace řídkých polí

* spojové seznamy a jejich implementace viz opora
* řídká pole především matice viz anglická wikipedie (https://en.wikipedia.org/wiki/Sparse_matrix) a jejich implementace ve SciPy (důležité je znát výhody a nevýhody jednotlivých implementací)

## Datové struktury: stromové struktury (binární uspořádané stromy, haldy), vyvažování stromů 

* haldy (PLA 4.2), lineární representace (je nutné prakticky vyzkoušet)
* binární uspořádané stromy (PLA 8.1) = základní operace (klíčové je ne zcela triviální mazání uzlů)
* AVL stromy (PLA 8.2)

## Datové struktury: grafy (binomiální haldy, ohodnocené grafy)
* grafy: representace a základní operace nad nimi (PLA 5.1 až 5.8), klíčové je prohledávání do šířky a hloubky, pro porovnání viz https://networkx.org/
* ohodnocené grafy: 6.1, 6.2, 6.4 (representace, ohodnocení cest)
* binomiální: 18.1-18.2.

## Zpracování textů (suffix trees, string distance, approximate pattern matching)
 -- základní definice viz PLA 13 (zkuste implementovat jden z algoritmů v Pythonu)
 
 implementace regulárních výrazů viz například: https://swtch.com/~rsc/regexp/regexp1.html



