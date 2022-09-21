const express = require('express')
const path = require('path')
const app = express()
const {PythonShell} = require('python-shell');

app.use(express.json())

let trenitaliaResultsMap = new Map();
let italoResultsMap = new Map();

app.get('/', (req,res) => {
	res.sendFile(path.join(__dirname, 'index.html'))
})

async function pyrun(script, options){
	return new Promise((resolve, reject) => {
		PythonShell.run(script, options, (pyErr, pyResults)=>{
			if (pyErr){
				console.log('error while running '+script);
				reject(pyErr);
			}
			else resolve(pyResults?.length > 0 ? pyResults[0] : [])

		})
	})
}

async function getTrainResults(script, options, map, mapId){
	let secondsSinceEpoch = getSecondsSinceEpoch()
	if (map.has(mapId) && (secondsSinceEpoch - map.get(mapId).requestTime < 600)){
		console.log('Found data in cache for '+script);
		return {error: null, results: map.get(mapId).data}
	} else {
		try {
			let results = await pyrun(script, options);
			if (results.length === 0) throw Error('Found no trains on '+script+' for desired time\n');
			map.set(mapId, {requestTime: secondsSinceEpoch, data: results});
			return {error: null, results}
		} catch (e) {
			return {error: e.message, results: []}
		}
	}

}

function getSecondsSinceEpoch(){
	let curDate = new Date();
	return Math.floor(curDate.getTime()/1000)
}

app.post('/aera', async (req,res) => {
	const {origin, destination, dateTime, returnDateTime, passengers} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	let [retDate, retTime] = returnDateTime.split(' ');
	retDate = retDate.replaceAll('/','-');
	let options = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, retDate, retTime]
	}
	let results = await pyrun('tara.py', options)
	console.log(results)
	res.json(JSON.stringify(results))
	// let trenitaliaResult = getTrainResults('main.py',trenitaliaOptions, trenitaliaResultsMap, trenitaliaMapId);
	// let italoResult = getTrainResults('italoRequest.py',italoOptions, italoResultsMap, italoMapId);
	// Promise.all([trenitaliaResult, italoResult]).then(results => {
	// 	let combinedResults = results.reduce((a,b)=> ({error: a.error + b.error, results: [...a.results, ...b.results]}))
	// 	res.json(JSON.stringify(combinedResults));
	// })
})
app.post('/aerr', async (req,res) => {
	const {origin, destination, dateTime, returnDateTime, passengers, goingoutId, cartId, cookies, company} = req.body;
	let [depDate, depTime] = dateTime.split(' ');
	depDate = depDate.replaceAll('/','-')
	let [retDate, retTime] = returnDateTime.split(' ');
	retDate = retDate.replaceAll('/','-')
	if (company !== 'trenitalia' && company !== 'italo') return;
	let results, options;
	if (company === 'trenitalia'){
		options = {
			mode: 'json',
			args: [origin, destination, depDate, depTime, retDate, retTime, passengers, goingoutId, cartId, JSON.stringify(cookies)]
		}
		console.log(origin, destination, dateTime, returnDateTime, passengers, goingoutId, cartId, cookies)
		let scriptResult = await pyrun('temp.py', options)
		console.log(scriptResult)
		results = {message: 'everything went well!'}
		// runscript iwth data and then send it back
		//results = await pyrun('scriptname', options)
	} else {
		let options = {
			mode: 'json',
			args: [origin, destination, date, time, passengers]
		}
		results = await pyrun('scriptname', options)
	}
	// it's italo
	res.send(JSON.stringify(results));


})

app.post('/run', async (req,res) => {

	// solo andata -> solito
	// anche ritorno, no offerte -> faccio 2 query consecutive per gruppo
	// per quelle sopra posso usare solita mappa

	// anche ritorno, con offerte -> una sola query ma mando indietro anche cartid ecc

	const {origin, destination, dateTime, returnDateTime, passengers} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');

	let trenitaliaOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers]
	}
	let italoOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers]
	}

	let trenitaliaMapId = origin+destination+dateTime;
	let italoMapId = origin+destination+dateTime
	
	let trenitaliaResult = getTrainResults('main.py',trenitaliaOptions, trenitaliaResultsMap, trenitaliaMapId);
	let italoResult = getTrainResults('italoRequest.py',italoOptions, italoResultsMap, italoMapId);

	Promise.all([trenitaliaResult, italoResult]).then(results => {
		let combinedResults = results.reduce((a,b)=> ({error: a.error + b.error, results: [...a.results, ...b.results]}))
		res.json(JSON.stringify(combinedResults));
	})
})


app.post('/dev', (req,res) => {
	let data = [
		{
			"solution.departureTime": "2022-09-22T15:10:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T20:10:00.000+02:00",
			"solution.duration": "5h 00min",
			"young": 72.1,
			"senior": 72.1,
			"adult": 77.9
		},
		{
			"solution.departureTime": "2022-09-22T15:25:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T20:03:00.000+02:00",
			"solution.duration": "4h 38min",
			"young": 61.8,
			"senior": 61.8,
			"adult": 71.9
		},
		{
			"solution.departureTime": "2022-09-22T16:10:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T21:13:00.000+02:00",
			"solution.duration": "5h 03min",
			"young": 72.1,
			"senior": 72.1,
			"adult": 71.9
		},
		{
			"solution.departureTime": "2022-09-22T17:10:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T22:12:00.000+02:00",
			"solution.duration": "5h 02min",
			"young": 72.1,
			"senior": 72.1,
			"adult": 71.9
		},
		{
			"solution.departureTime": "2022-09-22T17:58:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T22:33:00.000+02:00",
			"solution.duration": "4h 35min",
			"young": 61.8,
			"senior": 61.8,
			"adult": 71.9
		},
		{
			"solution.departureTime": "2022-09-22T18:10:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T23:12:00.000+02:00",
			"solution.duration": "5h 02min",
			"young": 61.8,
			"senior": 61.8,
			"adult": 71.9
		},
		{
			"solution.departureTime": "2022-09-22T18:30:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T23:03:00.000+02:00",
			"solution.duration": "4h 33min",
			"young": 61.8,
			"senior": 61.8,
			"adult": 71.9
		},
		{
			"solution.departureTime": "2022-09-22T19:00:00.000+02:00",
			"solution.arrivalTime": "2022-09-22T23:28:00.000+02:00",
			"solution.duration": "4h 28min",
			"young": 82.4,
			"senior": 82.4,
			"adult": 77.9
		},
		{
			"solution.departureTime": "2022-09-23T05:10:00.000+02:00",
			"solution.arrivalTime": "2022-09-23T10:28:00.000+02:00",
			"solution.duration": "5h 18min",
			"young": 61.8,
			"senior": 61.8,
			"adult": 65.9
		},
		{
			"solution.departureTime": "2022-09-23T06:00:00.000+02:00",
			"solution.arrivalTime": "2022-09-23T10:33:00.000+02:00",
			"solution.duration": "4h 33min",
			"young": 61.8,
			"senior": 61.8,
			"adult": 65.9
		}
	]
	res.json(JSON.stringify(data));

})

app.listen(3003, () => {
	console.log('Listening on port 3003')
})
