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
