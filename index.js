const express = require('express')
const path = require('path')
const app = express()
const {PythonShell} = require('python-shell');
const cors = require('cors');

app.use(cors());
app.use(express.json())


let trenitaliaResultsMap = new Map();
let italoResultsMap = new Map();

app.get('/', (req,res) => {
//	res.sendFile(path.join(__dirname, 'index.html'))
	res.send("Hello World");
})

app.get('/try', (req,res) => {
	res.send("Other urls work as well");
})

async function pyrun(script, options){
	return new Promise((resolve, reject) => {
		try {
			PythonShell.run(script, options, (pyErr, pyResults)=>{
				if (pyErr){
					console.log('error while running '+script);
					reject(pyErr);
				}
				else resolve(pyResults?.length > 0 ? pyResults[0] : [])
			})
		} catch (e) {
			console.log(e.message)
			reject(e.message)
		}
	})
}

async function getTrainResults(script, options, map, mapId){
	let secondsSinceEpoch = getSecondsSinceEpoch()
	if (map.has(mapId) && (secondsSinceEpoch - map.get(mapId).requestTime < 600)){
		console.log('Found data in cache for '+script);
		// return {error: null, results: map.get(mapId).data}
		return map.get(mapId).data
	} else {
		try {
			let results = await pyrun(script, options);
			if (results.length === 0) throw Error('Found no trains on '+script+' for desired time\n');
			map.set(mapId, {requestTime: secondsSinceEpoch, data: results});
			// return {error: null, results}
			return results
		} catch (e) {
			console.log(e.message)
			// return {error: e.message, results: []}
			return []
		}
	}

}

function getSecondsSinceEpoch(){
	let curDate = new Date();
	return Math.floor(curDate.getTime()/1000)
}

function getScriptOptions(reqBody, type, company){
	let options = {mode: 'json'}
	const {origin, destination, dateTime, passengers} = reqBody;
	let [depDate, depTime] = dateTime.split(' ')
	depDate = depDate.replaceAll('/','-');
	if (type !== 'oneway'){
		const {returnDateTime} = reqBody;
		let [retDate, retTime] = dateTime.split(' ')
		retDate = retDate.replaceAll('/','-');
		if (type === 'outgoing'){
			options.args = [origin, destination, depDate, depTime, passengers, retDate, retTime];
		} else if (type === 'returning') {
			const {cookies} = reqBody;
			if (company === 'trenitalia'){
				const {goingoutId, cartId} = reqBody;
				options.args = [origin, destination, depDate, depTime, passengers, retDate, retTime, goingoutId, cartId, JSON.stringify(cookies)];
			} else {
				const {inputValue} = reqBody;
				options.args = [origin, destination, depDate, depTime, passengers, retDate, retTime, inputValue, JSON.stringify(cookies)];
			}
		}
	} else {
		options.args = [origin, destination, depDate, depTime, passengers]
	}
	return options
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
		res.json(combinedResults);
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
		console.log(origin, destination, dateTime, returnDateTime, passengers, goingoutId, cartId, JSON.stringify(cookies))
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
	
	res.json({error: "Too much data", results: []});
	// REMOVE THIS --------------------------------------------------------------===================================================
	const {origin, destination, dateTime, passengers} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');

	let options = {
		mode: 'json',
		args: [origin, destination, date, time, passengers]
	}

	let trenitaliaMapId = origin+destination+dateTime;
	let italoMapId = origin+destination+dateTime
	
	// 								CHECK SCRIPTS TO RUN
	let trenitaliaResult = getTrainResults('toneway.py', options, trenitaliaResultsMap, trenitaliaMapId);
	let italoResult = getTrainResults('ioneway.py', options, italoResultsMap, italoMapId);

	Promise.all([trenitaliaResult, italoResult])
		.then(results => {
			res.json({
				error: results[0].error + results[1].error,
				results: [...results[0].results, ...results[1].results]
			})
		})
		.catch(e => {
			console.log('Encountered an error while searching for one way results for both companies')
			console.log(e.message);
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

	let outgoingOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, returnDate, returnTime]
	}
	let returnOptions = {
		mode: 'json',
		args: [destination, origin, returnDate, returnTime, passengers]
	}

	// RUN SCRIPTS
	let trenitaliaOutgoing = pyrun('toutgoing.py', outgoingOptions)
	let italoOutgoing = pyrun('ioutgoing.py', outgoingOptions)
	let trenitaliaReturn = pyrun('toneway.py', returnOptions)
	let italoReturn = pyrun('ioneway.py', returnOptions)

	Promise.all([trenitaliaOutgoing, italoOutgoing, trenitaliaReturn, italoReturn])
		.then(results => {
			let resultValue = {
				error: results.map(result => result.error).join(''),
				results: {outgoing: [...results[0].results, ...results[1].results], returning: [...results[2].results, ...results[3].results]}, 
				metadata: {italo: {cookies: results[1].cookies}, trenitalia: {cookies: results[0].cookies, cartId: results[0].cartId}}
			}
			res.json(resultValue)	
		})
		.catch(e => {
			console.log('Encountered an error while looking for one way trips going out and back for both companies')
			console.log(e.message)
		})
})

app.post('/bothReturns', (req,res) => { // needs to run 2 return requests, gets provided metadata
	const {origin, destination, dateTime, returnDateTime, passengers, cartId, trenitaliaCookies, italoCookies, trenitaliaId, italoInputValue} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/','-');
	
	// SET OPTIONS
	let trenitaliaOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, returnDate, returnTime, trenitaliaId, cartId, JSON.stringify(trenitaliaCookies)]
	}
	let italoOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, returnDate, returnTime, italoInputValue, JSON.stringify(italoCookies)]
	}
	// RUN SCRIPTS
	let trenitaliaResult = pyrun('treturn.py', trenitaliaOptions)
	let italoResult = pyrun('ireturn.py', italoOptions)

	Promise.all([trenitaliaResult, italoResult])
		.then(results => {
			res.json({
				error: results[0].error + results[1].error,
				results: [...results[0].results, ...results[1].results]
			})
		})
		.catch(e => {
			console.log('Encountered an error while looking for return trains for both companies')
			console.log(e.message);
		})
})

app.post('/outgoing', (req,res) => { // 2 requests that return metadata
	const {origin, destination, dateTime, returnDateTime, passengers} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/','-');
	
	// SET OPTIONS
	let options = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, returnDate, returnTime]
	}

	// RUN SCRIPTS
	let trenitaliaResult = pyrun('toutgoing.py', options)
	let italoResult = pyrun('ioutgoing.py', options)

	Promise.all([trenitaliaResult, italoResult])
		.then(results => {
			let resultValue = {
				error: results[0].error + results[1].error,
				results: [...results[0].results, ...results[1].results],
				metadata: {italoCookies: results[1].cookies, trenitaliaCookies: results[0].cookies, cartId: results[0].cartId}
			}
			res.json(resultValue)
		})
		.catch(e => {
			console.log('Encountered an error while searching for outgoing results')
			console.log(e.message)
		})
})

app.post('/return', async (req,res) => {
	const {company} = req.body;
	const {origin, destination, dateTime, returnDateTime, passengers, cookies} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/','-');
	let results, scriptName, options;

	if (company === 'italo'){
		const {inputValue} = req.body;
		options = {
			mode: 'json',
			args: [origin, destination, date, time, passengers, returnDate, returnTime, inputValue, JSON.stringify(cookies)]
		}
		scriptName = 'ireturn.py'
		results = await pyrun('ireturn.py', options)
	} else if (company === 'trenitalia') {
		const {cartId, goingoutId} = req.body;
		options = {
			mode: 'json',
			args: [origin, destination, date, time, passengers, returnDate, returnTime, goingoutId, cartId, JSON.stringify(cookies)]
		}
		console.log(options.args)
		scriptName = 'treturn.py'
	}
	try {
		results = await pyrun(scriptName, options)
		res.json(results)
	} catch(e) {
		console.log('While trying to find return trains I encountered an error')
		console.log(e.message)
	}
})

app.listen(3003, () => {
	console.log('Listening on port 3003')
})
