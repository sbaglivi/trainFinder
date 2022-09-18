import {useState} from 'react';
import departureTimeSort from './departureTimeSort.js';

const ResultsList = ({results, reorderResults}) => {
	let [sortOrder, setSortOrder] = useState({by: 'departureTime', asc: 1});
	let [showMore, setShowMore] = useState('none')
	const toggleShowMore = () => {
		setShowMore(oldVal => oldVal === 'none' ? 'table-cell' : 'none')
	}
	const sortResults = key => {
		updateSortOrder(key);
		applySortOrder()
		console.log(sortOrder)
	}
	const updateSortOrder = (key) => {
		if (sortOrder.by === key){
			setSortOrder(oldOrder => ({...oldOrder, asc: -1*oldOrder.asc}))
		} else {
			setSortOrder({by: key, asc: 1});
		}
	}
	const departureSort = str => {
		let departureRe = /(\d+)(?:\/)(\d+)(?: )(\d+)(?::)(\d+)/
		let match = str.match(departureRe)
		let newStr = match[2]+match[1]+match[3]+match[4];
		return newStr
	}
	const applySortOrder = () => {
		let newOrder;
		switch(sortOrder.by){
			case 'departureTime':
				newOrder = results;
				reorderResults(newOrder.sort((a,b) => departureTimeSort(a,b,sortOrder.asc)));
				break;
			default:
				return;
		}
	}
	return (
		<table>
		<thead>
			<tr>
				<th onClick={() => sortResults('departureTime')} >Departure</th>
				<th>Arrival</th>
				<th>Duration</th>
				<th>Prezzo Minimo</th>
				<th>Company <span style={{display: showMore === 'table-cell' ? 'none' : 'inline'}} onClick={toggleShowMore}>&#8594;</span></th>
				<th style={{display: showMore}}>Single</th>
				<th style={{display: showMore}}>Adult</th>
				<th style={{display: showMore}}>Young</th>
				<th style={{display: showMore}}>Senior<span onClick={toggleShowMore}>&#8592;</span></th>
			</tr>
		</thead>
			<tbody>
				{results.map(result => 
					<tr key={result.id}>
						<td>{result.departureTime}</td>
						<td>{result.arrivalTime}</td>
						<td>{result.duration}</td>
						<td>{result.minPrice}</td>
						<td>{result.company}</td>
						<td style={{display: showMore}} >{result.minIndividualPrice}</td>
						<td style={{display: showMore}} >{result.young}</td>
						<td style={{display: showMore}} >{result.senior}</td>
						<td style={{display: showMore}} >{result.adult}</td>
					</tr>	
				)}
			</tbody>
		</table>
	)
}

export default ResultsList;
