import SearchForm from './SearchForm.jsx';
import ResultsList from './ResultsList.jsx';
import {useState} from 'react';

const App = () => {
	const [results, setResults] = useState({error: '', results: []});
	const reorderResults = newResults => {
		setResults(oldResults => ({...oldResults, results: newResults}));
	}
	const onClick = async () => {
		let response = await fetch('/dev', {
			method: 'POST',
			headers: {
				'Accept': 'application/json'
			}
		});
		if(!response.ok){
			console.log('response from /dev was not ok');
			return;
		}
		let data = await response.json();
		let parsedData = JSON.parse(data);
		console.log(parsedData);
		console.log(typeof parsedData);
		setResults(parsedData);
	}

	return (
		<div>
			<SearchForm setResults={setResults}/>
			{results.error ? <p>{results?.error}</p> : null}
			{results?.results ? <ResultsList results={results.results} reorderResults={reorderResults}/> : null}
		</div>
	)
}

export default App;
