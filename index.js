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
	let trenitaliaOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, retDate, retTime]
	}
	let italoOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, retDate, retTime]
	}
	let trenitaliaResults = pyrun('tara.py', trenitaliaOptions) // shape : {data: array, cartId: str, cookies: object}
	let italoResults = pyrun('iar.py', italoOptions) // shape {data: array, cookies: object}
	Promise.all([trenitaliaResults, italoResults]).then(results => {
		let combinedResults = {results: [...results[0].data, ...results[1].data], cartId: results[0].cartId, trenitaliaCookies: results[0].cookies, italoCookies: results[1].cookies}
		// let combinedResults = results.reduce((a,b)=> ({error: a.error + b.error, results: [...a.results, ...b.results]}))
		res.json(JSON.stringify(combinedResults));
	})
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
		results = await pyrun('tarr.py', options)
		// console.log(results)
	} else if (company === 'italo') {
		options = {
			mode: 'json',
			args: [origin, destination, depDate, depTime, retDate, retTime, passengers, goingoutId, JSON.stringify(cookies)]
		}
		results = await pyrun('iar2.py', options)
		console.log(results)
	}
	// it's italo
	res.send(JSON.stringify(results));


})

app.post('/outgoingOnly', async (req,res) => { // 2 simple requests, return only results
	const {origin, destination, dateTime, passengers} = req.body;
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
	
	// 								CHECK SCRIPTS TO RUN
	// let trenitaliaResult = getTrainResults('main.py',trenitaliaOptions, trenitaliaResultsMap, trenitaliaMapId);
	// let italoResult = getTrainResults('italoRequest.py',italoOptions, italoResultsMap, italoMapId);

	Promise.all([trenitaliaResult, italoResult]).then(results => {
		res.json(JSON.stringify([...trenitaliaResult, ...italoResult]))
	})
	/*
	Promise.all([trenitaliaResult, italoResult]).then(results => {
		let combinedResults = results.reduce((a,b)=> ({error: a.error + b.error, results: [...a.results, ...b.results]}))
		res.json(JSON.stringify(combinedResults));
	})
	*/
})

app.post('/allNoOffers', (req,res) => { // need to run 2 outgoing requests that return metadata (1 italo 1 tren), then another 2 simple reqs (just results)
	const {origin, destination, dateTime, returnDateTime, passengers} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/','-');

	let trenitaliaOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers]
	}
	let italoOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers]
	}

	// RUN SCRIPTS

	Promise.all([trenitaliaResult, italoResult, trenitaliaNoMetadata, italoNoMetadata]).then(results => {
		let resultValue = {
			results: {outgoing: [...trenitaliaResult.results, ...italoResult.results], returning: [...trenitaliaNoMetadata, ...italoNoMetadata]}, 
			metadata: {italoCookies: italoResult.cookies, trenitaliaCookies: trenitaliaResult.cookies, cartId: trenitaliaResult.cartid}
		}
		res.json(JSON.stringify(resultValue))	
	})

})

app.post('/bothReturns', (req,res) => { // needs to run 2 return requests, gets provided metadata
	const {origin, destination, dateTime, returnDateTime, passengers, cartId, trenitaliaCookies, italoCookies, trenitaliaId, italoInputValue} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/','-');
	
	// SET OPTIONS

	// RUN SCRIPTS

	Promise.all([trenitaliaResult, italoResult]).then(results => {
		res.json(JSON.stringify([...trenitaliaResult, italoResult]))
	})
})

app.post('/outgoing', (req,res) => { // 2 requests that return metadata
	const {origin, destination, dateTime, returnDateTime, passengers, cartId, trenitaliaCookies, italoCookies, trenitaliaId, italoInputValue} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/','-');
	
	// SET OPTIONS

	// RUN SCRIPTS

	Promise.all([trenitaliaResult, italoResult]).then(results => {
		let resultValue = {
			results: {outgoing: [...trenitaliaResult.results, ...italoResult.results]}, 
			metadata: {italoCookies: italoResult.cookies, trenitaliaCookies: trenitaliaResult.cookies, cartId: trenitaliaResult.cartid}
		}
		res.json(JSON.stringify(resultValue))
	})
})


app.listen(3003, () => {
	console.log('Listening on port 3003')
})
