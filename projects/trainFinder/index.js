const express = require('express')
const path = require('path')
const app = express()
const {PythonShell} = require('python-shell');

app.use(express.json())

app.get('/', (req,res) => {
	res.sendFile(path.join(__dirname, 'index.html'))
})


app.post('/run', (req,res) => {
	const {origin, destination, dateTime} = req.body;
	let [date, time] = dateTime.split(' ');
	date = date.replaceAll('/','-');
	
	let options = {
		mode: 'json',
		//args: ['milanoCentrale', 'salerno', '13-10-22', '15']
		args: [origin, destination, date, time]
	}

	PythonShell.run('main.py', options, (err, result) => {
		if (err) {
			console.log(err)
			return
		}
		console.log(result)
	})

	res.send(JSON.stringify({message: 'data received!'}));
})

app.listen(3003, () => {
	console.log('Listening on port 3003')
})
