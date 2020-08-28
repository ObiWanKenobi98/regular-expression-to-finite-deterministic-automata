In implementarea temei am pastrat fisierele propuse in schelet si am tratat doar prelucrarea regex-urilor
din forma de TDA. Pentru aceasta, am folosit 3 transformari. In fisierul regular_expression.py am
implementat transformarea din regex in expresie regulata (pentru majoritatea cazurilor a fost necesara
doar o transpunere din tipul de regex in tipul de expresie regulata corespunzatoare; pentru cazuri mai
complexe, am apelat recursiv pe terminii regex-urilor functia definita, iar in cazul RANGE, am tratat
individual fiecare caz - minim, maxim, sau interval de aparitii). In fisierul nfa.py am implementat 
transformarea din expresie regulata intr-un automat finit nedeterminist(similar cu prima transformare,
in mare parte am folosit substitutii textuale, apeland recursiv sau facand reuniune/ concatenare acolo
unde era cazul). In fisierul dfa.py am implementat transformarea dintr-un automat finit nedeterminist 
intr-unul determinist (am mai definit o functie auxiliara, pentru calcularea inchiderii epsilon a unei 
stari dintr-un afn, folosind o coada in care introduc doar stari accesibile prin tranzitii epsilon care
nu se afla deja in inchiderea epsilon a starii curente, similar cu algoritmul BFS de parcurgere a grafurilor; 
pentru transformarea propriu-zisa, am eliminat toate tranzitiile epsilon si am folosit algoritmul studiat
la curs/ seminar, transformand multimea de stari intr-o multime care are elemente ce sunt la randul lor
multimi de stari din automatul nedeterminist). In fisierul main.py am apelat succesiv aceste transformari 
pentru fiecare TDA si am simulat executia automatului determinist generat in urma transformarilor de mai 
sus, consumand cate o litera din fiecare cuvant si efectuand tranzitiile necesare. Mentionez ca functia de
tranzitie generata pentru automatul finit determinist nu este totala, dar am acoperit cazurile in care s-ar
ajunge in sink state in cadrul simularii: daca o tranzitie nu exista pe simbolul curent, inseamna ca automatul
nu poate ajunge intr-o stare finala pentru acest cuvant, deci nu il accepta (nu mai trebuie simulata toata
executia automatului pentru cuvantul curent). 