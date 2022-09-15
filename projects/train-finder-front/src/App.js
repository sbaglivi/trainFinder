import {useState} from 'react';
import parse from 'date-fns/parse';
// import format from 'date-fns/format'; usage format(date, dateTimeFormat)


function App() {
	const [formData, setFormData] = useState({origin: '', destination: '', dateTime: '', passenger: 'all'});
	const dateTimeFormat = "dd/MM/yy HH";
	const onSubmit = async e => {
		e.preventDefault();
		if (Object.keys(formData).some(k => !formData[k])){
			console.log(formData);
			console.log('At least one of the form fields is falsy, check the object above for more info');
			return;
		}
		//let formattedDateTime = `${String(dateTime.getDate()).padStart(2,'0')}-${String(dateTime.getMonth()+1).padStart(2,'0')}-${String(dateTime.getFullYear()).slice(-2)} ${dateTime.getHours().toString().padStart(2,'0')}`;
		let response = await fetch('/run', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json'
			},
			body: JSON.stringify(formData)
		})
		if (!response.ok){
			console.log('Response was not ok while submitting');
			return
		}
		let content = await response.json();
		console.log(content)
	}
	const onChange = e => {
		const name = e.target.name
		setFormData(formData => ({...formData, [name]: e.target.value}))
	}
	const referenceDate = new Date();
	referenceDate.setHours(referenceDate.getHours()+1, 0, 0, 0);
	const onBlur = event => {
		try {
			console.log(event.target.value)
			let parsedDate = parse(event.target.value, dateTimeFormat, referenceDate)
			if (parsedDate < referenceDate) throw Error("Parsed date is before current date and time") 
			if (isNaN(parsedDate)) throw Error("Invalid date");
		} catch (err) {
			console.log(err);
			console.log(`Error while parsing date: ${event.target.value}.`);
			setFormData(formData => ({...formData, dateTime: ''}));
			return;
		}
	}
  return (
    <div className="App">
	  <form action='/run' method='POST' onSubmit={onSubmit}>
	  	<input type='text' placeholder='Origin' name='origin' value={formData.origin} onChange={onChange}/>
	  	<input type='text' placeholder='Destination' name='destination' value={formData.destination} onChange={onChange} />
	  <input type='text' placeholder='dd/mm/yy hh' name='dateTime' value={formData.dateTime} onBlur={onBlur} onChange={onChange} />
	  <select name='passenger' value={formData.passenger} onChange={onChange} >
	  	<option value='all'>All</option>
	  	<option value='young'>Young</option>
	  	<option value='senior'>Senior</option>
	  	<option value='adult'>Adult</option>
	  </select>
	  <button>Search trains</button>
	  </form>
    </div>
  );
}

export default App;
