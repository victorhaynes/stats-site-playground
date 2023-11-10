import './App.css';
import {useEffect, useState} from 'react';
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
  })

  const [region, setRegion] = useState("")
  
  function convertPlatformToRegion(){
    let re = ""
    if ({...summonerSearchFormData}.platform === "na1" || {...summonerSearchFormData}.platform === "oc1"){
      re = "americas"
    } else if ({...summonerSearchFormData}.platform === "kr" || {...summonerSearchFormData}.platform === "jp1"){
      re = "asia"
    } else if ({...summonerSearchFormData}.platform === "euw1" || {...summonerSearchFormData}.platform === "eun1"){
      re = "europe"
    } else {
      re = ""
    }
    return re
  }

  useEffect(()=>{
    setRegion(convertPlatformToRegion())
  },[summonerSearchFormData])

  function handleSummonerSearchChange(event){
    setSummonerSearchFormData({...summonerSearchFormData,
    [event.target.name]: event.target.value})
  }

  return (
    <Router>
      <Routes>
        <Route path="/" exact
          element={<Home handleSummonerSearchChange={handleSummonerSearchChange} summonerSearchFormData={summonerSearchFormData} setSummonerSearchFormData={setSummonerSearchFormData} region={region}/>}/>
        <Route path="/summoners/:region/:platform/:gameName/:tagLine"
          element={<SummonerDetail summonerSearchFormData={summonerSearchFormData}/>}/>
      </Routes>
    </Router>
  );
}

export default App;
