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

  // if(localStorage.getItem('platform') && localStorage.getItem('region') && localStorage.getItem('displayRegion')){
  //   const [platform, setPlatform] = useState(localStorage.getItem('platform'))
  //   const [region, setRegion] = useState(localStorage.getItem('region'))
  //   const [displayRegion, setDisplayRegion] = useState(localStorage.getItem('displayRegion')) 
  // } else {


  const [platform, setPlatform] = useState('');
  const [region, setRegion] = useState('');
  const [displayRegion, setDisplayRegion] = useState('')
  // displayRegion is the colloquiial way players refer to 'region', it is actually platform without the integer


  useEffect( () => { // If these values are previously saved to local storage, get & save to state
    const storedPlatform = localStorage.getItem('platform')
    const storedRegion = localStorage.getItem('region')
    const storedDisplayRegion = localStorage.getItem('displayRegion')

    if (storedPlatform && storedRegion && storedDisplayRegion){
      setPlatform(localStorage.getItem('platform'))
      setRegion(localStorage.getItem('region'))
      setDisplayRegion(localStorage.getItem('displayRegion'))
    }
  }, [])

  function handleSummonerNameEntry(event){
    setSummonerSearchFormData({...summonerSearchFormData,
    [event.target.name]: event.target.value})
  }

  function globallyUpdateDisplayedRegion(currentPlatform){
    const selectedPlatform = currentPlatform
    const mapPlatormToRegion = {
        'na1': 'americas',
        'br1': 'americas',
        'euw1': 'europe',
        'kr': 'asia'         
    }
    const newRegion = mapPlatormToRegion[selectedPlatform]

    setPlatform(selectedPlatform)
    setRegion(newRegion)
    setDisplayRegion(selectedPlatform.replace(/[0-9]+$/, '')) // Remove trailing zeros

    localStorage.setItem('platform', selectedPlatform);
    localStorage.setItem('region', newRegion);
    localStorage.setItem('displayRegion', selectedPlatform.replace(/[0-9]+$/, ''));
  }
  
  function handlePlatformSelection(event){
    const selectedPlatform = event.target.value
    globallyUpdateDisplayedRegion(selectedPlatform)
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
            element={<SummonerDetail region={region} platform={platform} globallyUpdateDisplayedRegion={globallyUpdateDisplayedRegion}/>}/>
          <Route path="/ladder/:displayRegion/:pageNumber" 
            element={<Ladder globallyUpdateDisplayedRegion={globallyUpdateDisplayedRegion}/>}/>
        </Routes>
      </>
      // </Router>
  );
}

export default App;