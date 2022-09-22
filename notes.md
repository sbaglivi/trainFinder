Per ogni treno voglio
- id (semplicita' nel differenziarli)
- Stazione partenza (? e' per 'sicurezza, in teoria in base alla ricerca che hai fatto dovrebbero essere scontate)
- Stazione arrivo (? e' per 'sicurezza, in teoria in base alla ricerca che hai fatto dovrebbero essere scontate)
- Orario partenza
- Orario arrivo
- Durata
- Vendibile (altrimenti ci fermiamo qui)
- Prezzo minimo young
- Prezzo minimo senior
- Prezzo minimo adulto
- Prezzo minimo silenzio ? (non so se ne vale la pena, lo controllo sia per adulti che per giovani?)

Cominciamo con quelli sicuri, da dove li prendo:
- id: solution.id
- orario p: solution.departureTime
- orario a: solution.arrivalTime
- durata: solution.duration
- vendibile: solution.status

Ora i complicati. Se riesco a renderlo completamente flat bene, altrimenti con una funzione. 
Itero fino a che ho prezzi per tutti e 3 E standard e standard area silenzio non sono stati controllati.

standard area silenzio potrebbe non esserci? nel caso seguo il solito ordine standard > premium ecc finche' non ho trovato i 3 prezzi

devo controllare se il treno e' vendibile

seguo l'ordine che mi do, itero su tutti i servizi, 
 se trovo quello che cerco lo controllo e poi lo tolgo dalla lista di quelli da controllare
 se non lo trovo alla fine del ciclo lo rimuovo e guardo quello dopo
appena ho tutti i prezzi stacco? se sono ordinati correttamente funziona, l'eccezione e' se 
non trovo tutti i prezzi, in quel caso stacco se ho controllato tutti i servizi => devo tenere traccia dei servizi che ho gia' controllato

potrei accontentarmi di guardare alcune categorie e arrendermi se dopo quelle non ho trovato i risultati:
itero su servizi, cerco priority[0], 
 la trovo -> controllo, prendo i prezzi disponibili e poi la rimuovo da priority
 non la trovo -> la rimuovo da priority
se priority e' vuoto o ho trovato tutti i prezzi fine.

priorityOrder = ['STANDARD', 'STANDARD AREA SILENZIO', 'PREMIUM', 'BUSINESS', 'BUSINESS AREA SILENZIO'] 
while (priorityOrder.length > 0 && !allPricesFound){
	for (let service of obj.grids[0].services){
		if (service.name == priorityOrder[0]){
			if offer.name == 'YOUNG'){}	
			else if offer.name == 'SENIOR'){}	
			else {}
			break;
	priorityOrder.shift()




Invece di semplicemente iterare posso scegliere l'ordine in cui voglio guardarli (standard, standard area silenzio, premium)
 Itero su non solution, obj.grids[0].services
non sono certo che siano sempre ordinati, se lo sono il primo dovrebbe essere standard e quindi la versione piu' economica. 
Se e' vendibile, itero su questa.offers, controllo se vendibile e se lo e' aggiorno il prezzo minimo del biglietto della categoria relativa
(se name == 'YOUNG' e' giovani, "SENIOR" senior, altrimenti e' per adulti)
Se la prima categoria controllata e' stata la standard E ho valori per tutte e 3 le categorie posso rompere il ciclo e passare alla
soluzione successiva.


---

Nuovo ostacolo: quando selezioni piu' passeggeri trenitalia non differenzia tra 'young', senior e adult
In pratica: i valori che trovo valgono gia' per il prezzo totale del viaggio, diventa solo piu' difficie
calcolare il vero prezzo totale ? 
in pratica se prezzo adulto < prezzo giovane / vecchio gia' pronto
 se > bisogna fare proporzione di es. 1 ad 1 giov 1 vecc
 min ad 100
 min giov 90
 min vecc 75
 lui mi fa vedere 300 adulto
 270 giov
 225 vecch
 io faccio adulti/passeggeritotali * adulto + giov/passT * min(adulto/giov) e senior/passT * min(senior/adulto) 

Presenta un potenziale problema se l'offerta adulto e' riservata a piu' persone che comprano quella stessa offerta
e i 'non-adulti' finiscono per acquistare offerte individuali perche' a prezzo minore quindi il prezzo del singolo 
adulto si alza. Realisticamente pero' credo che non dovrebbe succedere molto spesso perche' accade solo se:
- c'e' un'offerta di gruppo E
- l'offerta di gruppo costa piu' dell'offerta individuale senior / young


---
interfaccia per ritorno e funzionamento

- se data di ritorno viene riempita -> checkbox che rinuncia a offerte a&r per vedere subito i ritorni: faccio semplicemente 2 richieste di viaggi di andata
- senza checkbox faccio solo le richieste per il viaggio di andata MA
   - devo cambiare i file usati per la richiesta per mandare indietro non solo i dati relativi ai viaggi ma anche il cartId o altri metadata che serviranno nella richiesta successiva
- quando utente clicca 2 volte o preme un pulsante ecc su un'opzione di andata effettuo una ricerca per viaggi di ritorno sullo stesso operatore, vincolata all'andata con quell'opzione
  l'utente puo' selezionare come viaggi di andata al massimo 2 opzioni: 1 per operatore. A quel punto nei viaggi di ritorno verranno mostrate le soluzioni di a&r abbinate a d ognuna delle 2,
  magari colorate con lo stesso colore del viaggio di andata relativo
- l'interfaccia si dimezza in larghezza se ho dei risultati per il ritorno

Il problema di questa soluzione e' che finche' l'utente non sceglie un'opzione per azienda non vede tutte le possibili opzioni di ritorno E le opzioni di ritorno che vede sono associate a opzioni
di andata diversa, non sa se puo' 'mischiare' andata con un'azienda e ritorno con un'altra finche' non verifica autonomamente

(per ottimizzazione a qualche punto potrei cominciare a salvare tutti i viaggi nella cache di js e poi spedire all'applicazione solo una parte filtrata - tipo stesso giorno- per poter accedere alla cache anche in caso 
di ricerche simili ma non identiche)


From react:
submit -> some value to deduce whether it wants to find a return
(case in which doesn't care about offers (prob no one) just make 2 requests and go about your day) -> even this gets a bit messy where for the results I'm showing I need to remember if the user doesn't care about it and if it changes just
the departure date for example I should not query the return values again
I think my current map will keep doing its job for this situation, whereas I need another map in case the values are conditioned on roundtrip

displayedValues: trenitalia: cartId, values, errors, italo: cartId?, values, errors
user makes going out and back request wants rt offers:
- display results for both italo and trenitalia, save cartId and whatever else on the front end
- user double clicks one of the going out -> make return request with necessary data and display them
- user double clicks another of same company -> new return request that replaces the old data from same cmopany
- user double clicks going out from other company -> new return request that adds to values of other company
- user changes going out date -> everything needs to be redone
- user changes coming back date -> going out trips stay the same but new requests for the return based on the trips he had selected 

Return trips shown need to be specific to a company AND to the id of the train going out I need to save this data so that if he just changes coming back date I already have it to make new request

user makes only going out request:
 - serve it and fuck off
 - if he adds a return value, wouldn't I want to keep the cartId return in case just to be ready for it rather than making 2 of those?
user makes going 

---


Which scripts do I need:
trenitalia:
- only outgoing, doesn't return metadata    oneway. 	returns only array
- outgoing, returns metadata  				outgoing	returns object with array and metadata
- return, provided metadata					return		returns only array

italo:
- only outgoing, doesn't return metadata
- outgoing, returns metadata
- return, provided metadata

