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
			else resolve(pyResults[0])
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

app.post('/run', async (req,res) => {

	const {origin, destination, dateTime} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');

	let trenitaliaOptions = {
		mode: 'json',
		args: [origin, destination, date, time]
	}
	let passengers = '100'
	let italoOptions = {
		mode: 'json',
		args: [origin, destination, date, passengers]
	}

	let trenitaliaMapId = origin+destination+dateTime;
	let italoMapId = origin+destination+date;
	
	let trenitaliaResult = getTrainResults('main.py',trenitaliaOptions, trenitaliaResultsMap, trenitaliaMapId);
	let italoResult = getTrainResults('italoRequest.py',italoOptions, italoResultsMap, italoMapId);

	Promise.all([trenitaliaResult, italoResult]).then(results => {
		console.log(results)
		let combinedResults = results.reduce((a,b)=> ({error: a.error+b.error, results: [...a.results, ...b.results]}))
		res.json(JSON.stringify(combinedResults));
	})
	/*
	let curDate = new Date();
	let errorText = ''
	let allResults = []
	if (trenitaliaResultsMap.has(trenitaliaMapId) && (Math.floor(curDate.getTime()/1000) - trenitaliaResultsMap.get(trenitaliaMapId).requestTime < 600)){
		allResults = [...allResults, ...trenitaliaResultsMap.get(trenitaliaMapId).data]
		console.log('Found data in trenitalia cache!');
	} else {
		try {
			let trenitaliaResults = await pyrun('main.py', trenitaliaOptions);
			if (trenitaliaResults.length === 0) errorText += 'Found no trains on trenitalia for desired time\n';
			allResults = [...allResults, ...trenitaliaResults]
			trenitaliaResultsMap.set(trenitaliaMapId, {requestTime: Math.floor(curDate.getTime()/1000), data: trenitaliaResults});
		} catch (e) {
			errorText += e.message
		}
	}
	if (italoResultsMap.has(italoMapId) && (Math.floor(curDate.getTime()/1000) - italoResultsMap.get(italoMapId).requestTime < 600)){
		allResults = [...allResults, ...italoResultsMap.get(italoMapId).data]
		console.log('Found data in italo cache!');
	} else {
		try {
			let italoResults = await pyrun('italoRequest.py', italoOptions);
			if (italoResults.length === 0) errorText += 'Found no trains on italo for desired time\n';
			allResults = [...allResults, ...italoResults]
			italoResultsMap.set(italoMapId, {requestTime: Math.floor(curDate.getTime()/1000), data: italoResults});
		} catch (e) {
			errorText += e.message
		}
	}
	res.json(JSON.stringify({error: errorText, results: allResults}));
	*/
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
