import './App.css';
import {useEffect, useState} from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate
  // Link
} from "react-router-dom";
import Home from './components/Home';
import SummonerDetail from './components/SummonerDetail';
import Header from './components/Header';
import Ladder from './components/Ladder';



function App() {

  const navigate = useNavigate()


  const [summonerSearchFormData, setSummonerSearchFormData] = useState({
      gameName: "",
      tagLine: "",
  })

  const [platform, setPlatform] = useState('na1');
  const [region, setRegion] = useState('americas');
  const [displayRegion, setDisplayRegion] = useState('na')
  // displayRegion is the colloquiial way players refer to 'region', it is actually platform without the integer



  function handleSummonerNameEntry(event){
    setSummonerSearchFormData({...summonerSearchFormData,
    [event.target.name]: event.target.value})
  }

  function handlePlatformSelection(event){
    const selectedPlatform = event.target.value
    const mapPlatormToRegion = {
        'na1': 'americas',
        'br1': 'americas',
        'euw1': 'europe',
        'kr': 'asia'         
    }
    const newRegion = mapPlatormToRegion[selectedPlatform]

    setPlatform(selectedPlatform)
    setRegion(newRegion)
    let platformIntegerCheck = selectedPlatform.charAt(selectedPlatform.length - 1) // Get last character from platform{
    if (isNaN(platformIntegerCheck)){ // If not a number i.e. 'RU' platform
      setDisplayRegion(selectedPlatform)
    } else if (!isNaN(platformIntegerCheck)) // Is a number i.e. 1 from 'KR1' platform
      setDisplayRegion(selectedPlatform.slice(0,-1)) // Remove the 1
  }


  function submitAndSearchSummoner(event){
    event.target.reset()
    event.preventDefault()
    navigate(`/summoners/${displayRegion}/${summonerSearchFormData.gameName}-${summonerSearchFormData.tagLine}`)
    setSummonerSearchFormData({
        gameName: "",
        tagLine: "",
    })
  }



  return (
      // <Router>
      <>
      <Header displayRegion={displayRegion} handleSummonerNameEntry={handleSummonerNameEntry} handlePlatformSelection={handlePlatformSelection} submitAndSearchSummoner={submitAndSearchSummoner}/>
        <Routes>
          <Route path="/" exact
            element={<Home handleSummonerNameEntry={handleSummonerNameEntry} handlePlatformSelection={handlePlatformSelection} submitAndSearchSummoner={submitAndSearchSummoner} platform={platform} region={region}/>}/>
          {/* <Route path="/summoners/:region/:platform/:gameName/:tagLine" */}
          {/* <Route path="/summoners/:displayRegion/:gameName-:tagLine" */}
          <Route path="/summoners/:displayRegion/:displayNameZipped"
            element={<SummonerDetail region={region} platform={platform}/>}/>
          <Route path="/ladder/:displayRegion/:pageNumber" 
            element={<Ladder/>}/>
        </Routes>
      </>
      // </Router>
  );
}

export default App;

