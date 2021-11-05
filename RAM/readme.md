#Interpret RAM stroje

## Podpora instrukcí

Interpret podporuje instrukce RAM stroje popsaného 
v kapitole 2.5 knihy *Průvodce labyrintem algoritmů*
[https://knihy.nic.cz/files/edice/pruvodce_labyrintem_algoritmu.pdf](Průvodce labyrintem algoritmů).

## Rozšíření

### Substituce

V textu lze využít jednoduchých textových substitucí. Jakýkoliv výskyt
textu ve tvaru `{identifier}`, kde `identifier` je posloupnost libovolných
znaků kromě znaku `}` je nahražen substitučním řetězcem. 
V aktuální verzi je možno substituční řetězce definovat jen na 
příkazovém řádku při spuštění interpretu. To dále omezuje znaky použitelné
v identifikátoru (doporučeny jsou jen ASCII písmena).

Substituce slouží primárně k nastavení vstupních parametrů kódu například
rozměrů polí (hodnoty nelze číst za běhu RAM programů) 
nebo počátečních hodnot. Ve většině případů se tak jedná o celočíselné
literály.

Příklad:

`M := {x}`

Do registru M se vloží číslo representované substitučním řetězcem `x`.

### Pragmata

Pragmata jsou příkazy, které umožnují manipulovat s RAM strojem nad rámec
jeho instrukcí. Primárně slouží k ladění programů.

Pragmata se v programu uvádějí s prefixem `$`, aby se odlišili od instrukcí.
Před makry nelze uvádět návěští.

Vykonání pragmat se nezapočítává do čítače prováděných instrukcí ani se
nezapočítává do přístupů k paměti.

#### `print` pragma

Makro `print` vypisuje obsah paměti.

```
'$print' addr-spec [ ',' addr-spec]*
        addr-spec :: address | range
        address :: RE: -?[0-9]+
        number :: RE: -?[0-9]+
        range :: address ':' address [':' number]
```

Lze vypisovat jednotlivé adresy nebo celé rozsahy adres.
Rozsahy se uvádejí ve tvaru `dolní-mez : horní-mez` resp.
s nepovinným krokem `dolní-mez : horní-mez : krok`. 
Dolní mez je zahrnuta vždy, horní vyjde-li krok (u kroku 1
nebo -1 tedy vždy).

Příklad:

`$print -1:-26:-1,0:40`

Vypíše adresy -1 až -26 (tj. pojmenované registry) v opačném gardu
a pak pamětové buňky 0 až 40 (včetně).

#### `init` pragma

Toto pragma slouží k inicializaci pamětí. Paměť lze inicializovat
fixní hodnotou, sekvencí čísel nebo náhodnou hodnotou.

```
'$init' '['start-address']' value-specifier['*'repeat] [',' value-specifier['*'repeat]]*
    start-address:: RE: -?[0-9]+
    repeat:: RE: [0-9]+
    value-specifier: int_literal | range | random_value | fixed_random_value
    int_literal:: RE: -?[0-9]+
    range:: int_literal ':' int_literal [':' int_literal]  = values from range (Python semantics)
    random_value :: '@' range = random value from range (in repeat every value is new random)
    fixed_random_value ::  '@@' random value from range (fixed random value is repeated)
```
Příklad:

`$init -26 0*26,0:10*2,@0:10*10`

Počínaje adresou -26 je:
* 26 paměťových buněk vyplněno hodnotou 0 (což je původní stav)
* 20 paměťových buněk je vyplněno dvakrát opakovanou posloupností 0..9
* 10 paměťových buněk je vyplněno náhodnými hodnotami z rozsahu 0 až 9

## Spuštění interpretu 

`python rami.py [-h] [-d {step}] [-c] [-s SUBSTITUTE] filename`

* `filename` : jméno zdrojového kódu s instrukcemi pro RAM stroj
* `-d step` : zapíná trasování kódu (je vypsána každá provedená instrukce)
* `-c` : výpis čítače provedených instrukcí
* `-s SUBSTITUCE` :  zavádí substituční řetězce ve tvaru
  `klíč=hodnota[,...]*` např. -s n=5,m=6

Interpret využívá až na jedinou výjimku jen standardní knihovny. Tou
výjimkou je modul `parsy`.

Instalace modulu je standardní:

`pip install parsy`

