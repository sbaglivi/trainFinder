import {useState} from 'react';
import parse from 'date-fns/parse';
import Fuse from 'fuse.js';
import './form.css';
import format from 'date-fns/format'; //usage format(date, dateTimeFormat)
import departureTimeSort from './departureTimeSort.js';


const SearchForm = ({setResults}) => {
	const [formData, setFormData] = useState({origin: '', destination: '', dateTime: '', passengers: '100'});
	const [searchResults, setSearchResults] = useState([]);
	const [ulOffsetLeft, setUlOffsetLeft] = useState(0);
	const stationNameToCamelcase = str => {
		let newStr = str.replaceAll(' ','');
		newStr = newStr.charAt(0).toLowerCase() + newStr.slice(1);
		return newStr
	}
	const onSubmit = async e => {
		e.preventDefault();
		validateDateTime(formData.dateTime)
		if (Object.keys(formData).some(k => !formData[k])){
			console.log(formData);
			console.log('At least one of the form fields is falsy, check the object above for more info');
			return;
		}
		if (!acceptedStations.includes(formData.origin)){
			let possibleResults = fuse.search(formData.origin).map(result => result.item)
			if (possibleResults.length === 0){
				console.log('No station found that matches '+formData.origin);
				setFormData(oldData => ({...oldData, origin: ''}))
				return;
			}
			setFormData(oldData => ({...oldData, origin: possibleResults[0]}))
		}
		if (!acceptedStations.includes(formData.destination)){
			let possibleResults = fuse.search(formData.destination).map(result => result.item)
			if (possibleResults.length === 0){
				console.log('No station found that matches '+formData.destination);
				setFormData(oldData => ({...oldData, destination: ''}))
				return;
			}
			setFormData(oldData => ({...oldData, destination: possibleResults[0]}))
		}
		if (formData.origin === formData.destination){
			console.log('Origin and destination cannot be the same.');
			return;
		}
		//let formattedDateTime = `${String(dateTime.getDate()).padStart(2,'0')}-${String(dateTime.getMonth()+1).padStart(2,'0')}-${String(dateTime.getFullYear()).slice(-2)} ${dateTime.getHours().toString().padStart(2,'0')}`;
		let formattedData = {...formData, origin: stationNameToCamelcase(formData.origin), destination: stationNameToCamelcase(formData.destination)}
		let response = await fetch('/run', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json'
			},
			body: JSON.stringify(formattedData)
		})
		if (!response.ok){
			console.log('Response was not ok while submitting');
			return
		}
		let content = await response.json();
		content = JSON.parse(content);
		console.log(content)
		content.results.sort((a,b) => departureTimeSort(a,b,1));
		// this was necessary cause pandas was exporting as json and then I was encoding to json on top of that for error message
		// setResults({error: content.error, results: JSON.parse(content.results)}) 
		setResults(content)
	}
	const onChange = e => {
		const name = e.target.name
		setFormData(formData => ({...formData, [name]: e.target.value}))
	}
	const referenceDate = new Date();
	referenceDate.setHours(referenceDate.getHours()+1, 0, 0, 0);
	function validateDateTime(str, fieldName){
		const possibleDateTimeFormats = ["dd/MM/yy HH", "dd/MM/yy"]
		let errorText = ''
		for (let possibleFormat of possibleDateTimeFormats){
			try {
				let parsedDate = parse(str, possibleFormat, referenceDate)
				if (isNaN(parsedDate)) throw Error("Invalid date");
				if (possibleFormat === 'dd/MM/yy'){
					if (format(parsedDate, 'dd/MM/yy') === format(referenceDate, 'dd/MM/yy')) parsedDate.setHours(referenceDate.getHours())
					else parsedDate.setHours('08');
				}
				if (parsedDate < referenceDate) throw Error("Parsed date is before current date and time")
				setFormData(formData => ({...formData, [fieldName]: format(parsedDate, 'dd/MM/yy HH')}));
				return
			} catch (err) {
				errorText += `Error: ${err.message} while parsing date: ${str} with format ${possibleFormat}\n`;
			}
		}
		console.log(errorText)
		setFormData(formData => ({...formData, [fieldName]: ''}));
	}

	const onBlur = event => {
		validateDateTime(event.target.value, event.target.name)
	} 
	const acceptedStations = ['Milano Centrale', 'Milano Garibaldi', 'Reggio Emilia', 'Bologna', 'Firenze', 'Roma Termini', 'Roma Tiburtina', 'Napoli Centrale', 'Napoli Afragola', 'Salerno', 'Vallo della Lucania'];
	const fuse = new Fuse(acceptedStations, {includeScore: true});
	const stationOnChange = e => {
		setFormData(formData => ({...formData, [e.target.name]: e.target.value}));
		setSearchResults(fuse.search(e.target.value).map(result => result.item)) //.filter(item => e.target.name === 'origin' ? item !== formData.destination : item !== formData.origin));
	}
	const onKeyDown = e => {
		if (e.key === 'Enter' || e.key === 'Tab'){
			if (searchResults.length > 0){
				if (e.key === 'Enter') e.preventDefault();
				setFormData(formData => ({...formData, [e.target.name]: searchResults[0]}))
				setSearchResults([]);
			}
		}
	}
	let ulShown = searchResults.length > 0 ? 'block' : 'none';
	const onFocus = e => {
		const {target: {name}} = e;
		setSearchResults(fuse.search(formData[name]).map(result => result.item)) //.filter(item => item !== (name === 'origin' ? formData.destination : formData.origin)))
		const leftOffset = e.target.getBoundingClientRect().left;
		console.log(leftOffset);
		setUlOffsetLeft(leftOffset);

	}
  return (
	  <form action='/run' method='POST' onSubmit={onSubmit}>
	  <ul style={{display: ulShown, left: `${ulOffsetLeft}px`}}>
		{searchResults.map((result,index) => <li key={index}>{result}</li>)}
	  </ul>
	  	<input type='text' placeholder='Origin' name='origin' value={formData.origin} onChange={stationOnChange} onKeyDown={onKeyDown} onBlur={() => setSearchResults([])} onFocus={onFocus} />
	  	<input type='text' placeholder='Destination' name='destination' value={formData.destination} onChange={stationOnChange} onBlur={() => setSearchResults([])} onKeyDown={onKeyDown} onFocus={onFocus}/>
	  <input type='text' placeholder='dd/mm/yy hh' name='dateTime' value={formData.dateTime} onBlur={onBlur} onChange={onChange} />
	  <input type='text' pattern="[1-9][0-9]{2}|[0-9][1-9][0-9]|[0-9]{2}[1-9]" minlength="3" maxlength="3" placeholder='ASY' name='passengers' 
	  title="3 numbers from 0 to 9 that describe respectively the number of adult, senior and young passengers. (At least one needs to be different from 0)" onChange={onChange} 
	  value={formData.passengers}/>

	  <button>Search trains</button>
	  </form>
  );
}

export default SearchForm;
