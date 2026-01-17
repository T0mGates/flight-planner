import './App.css'
import { useQuery } from '@tanstack/react-query';
import Map from './Map.tsx'
import FlightInfoCard from './FlightInfoCard.tsx'

const fetchFlights = async () => {
  const response = await fetch('http://127.0.0.1:8000/flights');
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
};

function App() {
  // 2. Use the hook with refetchInterval
  const { data, isLoading, error } = useQuery({
    queryKey: ['flights'],
    queryFn: fetchFlights,
    refetchInterval: 10000, // 10 seconds in milliseconds
  });

  if (isLoading) return <div>Loading flights...</div>;
  if (error) return <div>Error loading flight data!</div>;


  return (
    <>
      <div className="card flex flex-row gap-2 justify-center">
        <Map flights={Object.values(data)} />
        <div className="w-100">
          <FlightInfoCard flights={Object.values(data)} />
        </div>
      </div>
    </>
  )
}

export default App
