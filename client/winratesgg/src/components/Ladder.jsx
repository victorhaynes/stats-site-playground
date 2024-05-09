import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Ladder = () => {
    const [rankedLadder, setRankedLadder] = useState([]);
    const [platform, setPlatform] = useState('na1');
    const [region, setRegion] = useState('americas');
    const [displayRegion, setDisplayRegion] = useState('na')
    const [selectionUpdate, setSelectionUpdate] = useState('na1americas')


    useEffect(() => {
        getLeaderboard();
    }, [selectionUpdate]);

    async function getLeaderboard() {        
        try {
            let response = await axios.get(`http://localhost:8000/ladder/?&platform=${platform}&region=${region}`);
            console.log(response.data);
            setRankedLadder(response.data);
        } catch (error) {
            console.log({ [error.response.request.status]: error.response.data });
        }
    }

    function updateSelection(platformChoice){

        const selectedPlatform = platformChoice
        const mapPlatormToRegion = {
            'na1': 'americas',
            'br1': 'americas',
            'euw1': 'europe',
            'kr': 'asia'     
        }
        const newRegion = mapPlatormToRegion[selectedPlatform]

        setPlatform(selectedPlatform)
        setRegion(newRegion)
        setSelectionUpdate(selectedPlatform+newRegion)
        let platformIntegerCheck = selectedPlatform.charAt(selectedPlatform.length - 1) // Get last character from platform{
        if (isNaN(platformIntegerCheck)){ // If not a number i.e. 'RU' platform
            setDisplayRegion(selectedPlatform)
        } else if (!isNaN(platformIntegerCheck)) // Is a number i.e. 1 from 'KR1' platform
            setDisplayRegion(selectedPlatform.slice(0,-1)) // Remove the 1
    }

    return (
        <>
            <button onClick={() => updateSelection('na1')} style={{ backgroundColor: platform === 'na1' ? 'lightblue' : 'white' }}>North America</button>
            <button onClick={() => updateSelection('br1')} style={{ backgroundColor: platform === 'br1' ? 'lightblue' : 'white' }}>Brazil</button>
            <button onClick={() => updateSelection('euw1')} style={{ backgroundColor: platform === 'euw1' ? 'lightblue' : 'white' }}>Europe West</button>

            {rankedLadder?.map((player, index) => { 
                let wins = player?.metadata?.wins;
                let losses = player?.metadata?.losses;
                let winrate = Math.round((wins / (wins + losses)) * 100);
                return (
                    <div key={index}>
                        <span>
                            {index + 1 + '.'} <Link to={`/summoners/${displayRegion}/${player?.gameName}-${player?.tagLine}`}>{player?.gameName + ' #' + player?.tagLine}</Link> {player?.metadata?.tier} {player?.metadata?.leaguePoints} LP {wins}W {losses}L {winrate}%
                        </span>
                    </div>
                );
            })}
        </>
    );
};

export default Ladder;