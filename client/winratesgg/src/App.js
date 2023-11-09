import './App.css';
import {useState} from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  // Link
} from "react-router-dom";
import Home from './components/Home';
import SummonerDetail from './components/SummonerDetail';



function App() {

  const [summonerSearchFormData, setSummonerSearchFormData] = useState({
      platform: "",
      gameName: "",
      tagLine: "",
      region: ""
  })

  function handleSummonerSearchChange(event){
    setSummonerSearchFormData({...summonerSearchFormData,
    [event.target.name]: event.target.value})
  }

  return (
    <Router>
      <Routes>
        <Route path="/" exact
          element={<Home handleSummonerSearchChange={handleSummonerSearchChange} summonerSearchFormData={summonerSearchFormData} setSummonerSearchFormData={setSummonerSearchFormData}/>}/>
        <Route path="/summoners/:platform/:gameName/:tagLine"
          element={<SummonerDetail summonerSearchFormData={summonerSearchFormData}/>}/>
      </Routes>
    </Router>
  );
}

export default App;
