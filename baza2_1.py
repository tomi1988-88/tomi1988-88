import datetime
from ast import literal_eval
import pywebio
from pywebio.input import *
from pywebio.output import *
import os


tagi = []
with open("p/Tagi_1.txt", "r", encoding="utf") as f:
    for i in f.readlines():
        if "\n" in i:
            tagi.append(i[0:-1])
        else:
            tagi.append(i)

with open("p/slownik_tekst.txt", "r", encoding="utf") as file:            
    zawartosc = file.read()
    baza = literal_eval(zawartosc)


slownik_tagi = {}                           ### sluży do późniejszego wybierania tagów przy wyszukiwaniu

for t in tagi:
    lista_kluczy = set()
    for k, val in baza.items():
        if t in val[6]:
            lista_kluczy.add(k)
    slownik_tagi[t] = lista_kluczy


for k in baza.keys():                       ### przekształcenie listy tagów w bazie do pojedynczego stringa
    baza[k][6] = ", ".join(baza[k][6])


belka_wynik = baza[0].copy()            ## wywalam pierwszy wpis zawierający opis kolumn
baza.pop(0)

# print(belka_wynik)
# print(baza)

pywebio.session.set_env(output_max_width='10000px')         ## powiększa okno wyświetlania

def sprawdzenie_czy_tagi_nie_sa_podwojone(w):
    for i in w["Pomijane_tagi"]:
        if i in w["Wybrane_tagi"]:
            return ("Pomijane_tagi", "Niepoprawne kryteria - wybrany co najmniej jeden ten sam tag w Kryteriach wyszukiwania i Tagach do pominięcia")


def wysz():
    wyszukiwanie = input_group("Wyszukiwarka DOZIK",
                               [select("Wybierz słowa kluczowe",
                                                      name="Wybrane_tagi",
                                                      options=list(slownik_tagi.keys()),
                                                      multiple=True,
                                                      required=True
                                                             ),
                               checkbox("",
                                                      name="Wysz_zawezone",
                                                      options=["Wyszukiwanie zawężone"]
                                         ),
                               select("Słowa kluczowe, które chcemy pominąć w wyszukiwaniu",
                                                      name="Pomijane_tagi",
                                                      options=list(slownik_tagi.keys()),
                                                      multiple=True
                                        ),
                               actions('', [
                                   {'label': 'Wyszukaj', 'value': 'submit'},
                                   {'label': 'Reset kryteriów', 'type': 'reset'},
                                             ],
                                       name='action',
                                       help_text="""
                                                Jeżeli "Wyszukaj" nie działa to znaczy, że co najmniej jeden tag wybrany do wyszukiwania pokrywa się z tagiem, który chcemy pominąć.
                                                \n
                                                "Reset kryteriów" działa, lecz niestety pozostawia wcześniej zaznaczone kryteria :( (po rozwinięciu lista jest pusta)
                                                Wyszukiwanie zawężone zwraca tylko wyniki, w których występują wszystkie podane tagi łącznie :)
                                                """)],
                               validate=sprawdzenie_czy_tagi_nie_sa_podwojone
                        )


    print(wyszukiwanie["Wysz_zawezone"])
    print(wyszukiwanie["Pomijane_tagi"])

    wyszukane_klucze = set()

    for t in wyszukiwanie["Wybrane_tagi"]:
        wyszukane_klucze = wyszukane_klucze.union(slownik_tagi.get(t))


    wyszukany_slownik = {}

    if wyszukiwanie["Wysz_zawezone"]:

        for k, val in baza.items():
            temp = val[6].split(", ")
            if all(item in temp for item in wyszukiwanie["Wybrane_tagi"]):
                wyszukany_slownik[k] = val


    else:
        for t in list(wyszukane_klucze):
            wyszukany_slownik[t] = baza[t]

    print(wyszukany_slownik)


    tabela_wynikow = []

    if wyszukiwanie["Pomijane_tagi"]:
        for k, val in wyszukany_slownik.items():
            temp = val[6].split(", ")
            if any(item in temp for item in wyszukiwanie["Pomijane_tagi"]):
                continue
            else:
                tabela_wynikow.append(val)

    else:
        for k, val in wyszukany_slownik.items():

            tabela_wynikow.append(val)

    tabela_wynikow.sort(key=lambda x: datetime.datetime.strptime(x[0], "%d.%m.%Y"))                     ## rozstrzygnięcia ułożone chronologicznie

    print(tabela_wynikow)

    def czyszczenie():
        pywebio.output.clear()
        wysz()

    put_html("<center><b>Wyniki wyszukiwania</b></center>")

    put_buttons([{"label": "Nowe reguły wyszukiwania", "value": 0}, {"label": "Powrót do poprzedniej strony","value": 0, "color": "success"}], onclick=[wysz, czyszczenie])

    ### DODAĆ INFO JAKIE TAGI ZOSTAŁY WYKORZYSTANE
    put_html("<b>Wyszukiwanie dokonane wg kyteriów:</b>")
    put_html("<b>Tagi wybrane: </b>" + ", ".join(wyszukiwanie["Wybrane_tagi"]))
    put_html("<b>Wyszukiwanie zawężone: </b>" + str(bool(wyszukiwanie["Wysz_zawezone"])))
    put_html("<b>Tagi pomijane: </b>" + ", ".join(wyszukiwanie["Pomijane_tagi"]) )
    put_html("<b>Liczba znalezionych rekordów: </b>" + str(len(tabela_wynikow)))


    def durne_pilik(strink):
        if ".doc" in strink or ".pdf" in strink:
            doc_pdf = open(os.path.abspath("w/"+strink), "rb").read()
            return [put_file(strink, doc_pdf, strink[-4:])]
        else:
            return ["brak pliku"]

    for i in tabela_wynikow:

        put_table([
                    belka_wynik[:7]+belka_wynik[10:],
                    i[:7] + i[10:13] + durne_pilik(i[13]) + durne_pilik(i[14]),           # TypeError: a bytes-like object is required, not 'str', albo spróbować wstawić button i funkcję lambda?
                    [put_html("<b>"+belka_wynik[7]+"</b>"), span(i[7], col=11)],
                    [put_html("<b>"+belka_wynik[8]+"</b>"), span(i[8], col=11)],
                    [put_html("<b>"+belka_wynik[9]+"</b>"), span(i[9], col=11)]
        ])


wysz()
