import express from 'express';
import path from 'path';
import { PythonShell } from 'python-shell';
import cors from 'cors';
import fs from 'fs';

const app = express();
app.use(cors());
app.use(express.json())

export type Train = {
	id: string,
	departureTime: string,
	arrivalTime: string,
	duration: string,
	company: 'italo' | 'trenitalia',
	inputValue: string | undefined,
	young: string | undefined,
	senior: string | undefined,
	adult: string | undefined,
	minPrice: number, // one way, but need to change the name on back end to be able toc change this one
	minOnewayPrice: number | undefined,
	minRoundtripPrice: number | undefined,
	minIndividualPrice: number,
	totPrice: number
}



let trenitaliaResultsMap = new Map();
let italoResultsMap = new Map();

app.get('/', (req, res) => {
	//	res.sendFile(path.join(__dirname, 'index.html'))
	res.send("Hello World");
})

app.get('/try', (req, res) => {
	res.send("Other urls work as well");
})

function logToFile(text: string) {
	fs.writeFile(path.join(__dirname, "log.txt"), text + '\n', { 'flag': 'a' }, err => {
		if (err) throw err;
	});
}

type ScriptOptions = {
	mode: "json",
	args: any[]
}

async function pyrun(script: string, options: ScriptOptions) {
	return new Promise((resolve, reject) => {
		try {
			fs.writeFile(path.join(__dirname, "log.txt"), path.join(__dirname, script) + '\n', { 'flag': 'a' }, err => {
				if (err) throw err;
			});
			PythonShell.run(path.join(__dirname, script), options, (pyErr, pyResults) => {
				if (pyErr) {
					console.log('error while running ' + script);
					logToFile('Error:' + pyErr)
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

async function getTrainResults(script: string, options: ScriptOptions, map, mapId) {
	let secondsSinceEpoch = getSecondsSinceEpoch()
	if (map.has(mapId) && (secondsSinceEpoch - map.get(mapId).requestTime < 600)) {
		console.log('Found data in cache for ' + script);
		// return {error: null, results: map.get(mapId).data}
		return map.get(mapId).data
	} else {
		try {
			let results = await pyrun(script, options) as Train[];
			if (results.length === 0) throw Error('Found no trains on ' + script + ' for desired time\n');
			map.set(mapId, { requestTime: secondsSinceEpoch, data: results });
			// return {error: null, results}
			return results
		} catch (e) {
			console.log(e.message)
			// return {error: e.message, results: []}
			return []
		}
	}

}

function getSecondsSinceEpoch() {
	let curDate = new Date();
	return Math.floor(curDate.getTime() / 1000)
}

type RequestBody = {
	origin: string,
	destination: string,
	dateTime: string,
	passengers: string,
	returnDateTime?: string
	goingoutId?: string,
	cookies?: {},
	cartId?: string,
	inputValue?: string
}

function getScriptOptions(reqBody: RequestBody, type: 'oneway' | 'outgoing' | 'returning', company: 'italo' | 'trenitalia') {
	let mode = 'json', args;
	const { origin, destination, dateTime, passengers } = reqBody;
	let [depDate, depTime] = dateTime.split(' ')
	// depDate = depDate.replaceAll('/','-'); typescript error: replaceAll does not exist on type string
	depDate = depDate.split('/').join('-');
	if (type !== 'oneway') {
		const { returnDateTime } = reqBody;
		let [retDate, retTime] = returnDateTime.split(' ')
		retDate = retDate.split('/').join('-');
		if (type === 'outgoing') {
			args = [origin, destination, depDate, depTime, passengers, retDate, retTime];
		} else if (type === 'returning') {
			const { cookies } = reqBody;
			if (company === 'trenitalia') {
				const { goingoutId, cartId } = reqBody;
				args = [origin, destination, depDate, depTime, passengers, retDate, retTime, goingoutId, cartId, JSON.stringify(cookies)];
			} else {
				const { inputValue } = reqBody;
				args = [origin, destination, depDate, depTime, passengers, retDate, retTime, inputValue, JSON.stringify(cookies)];
			}
		}
	} else {
		args = [origin, destination, depDate, depTime, passengers]
	}
	return { mode, args }
}

app.post('/return', async (req, res) => {
	const { company } = req.body;
	const { origin, destination, dateTime, returnDateTime, passengers, cookies } = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/', '-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/', '-');
	let results, scriptName, options;

	if (company === 'italo') {
		const { inputValue } = req.body;
		options = {
			mode: 'json',
			args: [origin, destination, date, time, passengers, returnDate, returnTime, inputValue, JSON.stringify(cookies)]
		}
		scriptName = 'ireturn.py'
		results = await pyrun('ireturn.py', options)
	} else if (company === 'trenitalia') {
		const { cartId, goingoutId } = req.body;
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
	} catch (e) {
		console.log('While trying to find return trains I encountered an error')
		console.log(e.message)
	}
})


app.post('/outgoingOnly', async (req, res) => { // 2 simple requests, return only results

	const { origin, destination, dateTime, passengers } = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/', '-');

	let options: ScriptOptions = {
		mode: "json",
		args: [origin, destination, date, time, passengers]
	}

	let trenitaliaMapId = origin + destination + dateTime;
	let italoMapId = origin + destination + dateTime

	// 								CHECK SCRIPTS TO RUN
	let trenitaliaResult = getTrainResults('toneway.py', options, trenitaliaResultsMap, trenitaliaMapId);
	let italoResult = getTrainResults('ioneway.py', options, italoResultsMap, italoMapId);

	Promise.all([trenitaliaResult, italoResult])
		.then(results => {
			fs.writeFile(path.join(__dirname, "log.txt"), JSON.stringify(results) + '\n', { 'flag': 'a' }, err => {
				if (err) throw err;
			});
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

app.post('/allNoOffers', (req, res) => { // need to run 2 outgoing requests that return metadata (1 italo 1 tren), then another 2 simple reqs (just results)
	const { origin, destination, dateTime, returnDateTime, passengers } = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/', '-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/', '-');

	let outgoingOptions: ScriptOptions = {
		mode: "json",
		args: [origin, destination, date, time, passengers, returnDate, returnTime]
	}
	let returnOptions: ScriptOptions = {
		mode: 'json',
		args: [destination, origin, returnDate, returnTime, passengers]
	}

	// RUN SCRIPTS
	let trenitaliaOutgoing = pyrun('toutgoing.py', outgoingOptions)
	let italoOutgoing = pyrun('ioutgoing.py', outgoingOptions)
	let trenitaliaReturn = pyrun('toneway.py', returnOptions)
	let italoReturn = pyrun('ioneway.py', returnOptions)

	Promise.all([trenitaliaOutgoing, italoOutgoing, trenitaliaReturn, italoReturn])
		.then((results: [TrenitaliaOutgoingResult, ItaloOutgoingResult, returnResult, returnResult]) => {
			let resultValue = {
				error: results.map(result => result.error).join(''),
				results: { outgoing: [...results[0].results, ...results[1].results], returning: [...results[2].results, ...results[3].results] },
				metadata: { italo: { cookies: results[1].cookies }, trenitalia: { cookies: results[0].cookies, cartId: results[0].cartId } }
			}
			res.json(resultValue)
		})
		.catch(e => {
			console.log('Encountered an error while looking for one way trips going out and back for both companies')
			console.log(e.message)
		})
})

type returnResult = {
	error: string,
	results: Train[]
}

type outgoingResult = {
	error: string,
	results: Train[],
	cookies: {}
}

type TrenitaliaMetadata = {
	cartId: string,
	goingoutId: string,
}

type ItaloMetadata = {
	inputValue: string
}

type TrenitaliaOutgoingResult = outgoingResult & TrenitaliaMetadata;
type ItaloOutgoingResult = outgoingResult & ItaloMetadata;

app.post('/outgoing', (req, res) => { // 2 requests that return metadata
	const { origin, destination, dateTime, returnDateTime, passengers } = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/', '-');
	let [returnDate, returnTime] = returnDateTime.split(' ');
	returnDate = returnDate.replaceAll('/', '-');

	// SET OPTIONS
	let options: ScriptOptions = {
		mode: 'json',
		args: [origin, destination, date, time, passengers, returnDate, returnTime]
	}

	// RUN SCRIPTS
	let trenitaliaResult = pyrun('toutgoing.py', options)
	let italoResult = pyrun('ioutgoing.py', options)

	Promise.all([trenitaliaResult, italoResult])
		.then((results: [TrenitaliaOutgoingResult, ItaloOutgoingResult]) => {
			let resultValue = {
				error: results[0].error + results[1].error,
				results: [...results[0].results, ...results[1].results],
				metadata: { italoCookies: results[1].cookies, trenitaliaCookies: results[0].cookies, cartId: results[0].cartId }
			}
			res.json(resultValue)
		})
		.catch(e => {
			console.log('Encountered an error while searching for outgoing results')
			console.log(e.message)
		})
})

app.listen(3003, () => {
	console.log('Listening on port 3003')
})
