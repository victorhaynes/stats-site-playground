import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const Ladder = ({globallyUpdateDisplayedRegion}) => {
    const params = useParams()
    const location = useLocation()

    const [rankedLadder, setRankedLadder] = useState([]);
    // const [displayRegion, setDisplayRegion] = useState(params.displayRegion)



    // UPDATE THIS SO IT WORKS FOR TIERS !!!!!!!!!!!!!!!!!! 
    const navigate = useNavigate()

    useEffect(() => {
        getLeaderboard();
    // }, [displayRegion, location.pathname]);
    }, [location.pathname]);


async function getLeaderboard() {        
        try {
            const displayedRegion = params.displayRegion
            const mapDisplayedToRegionToVerboseRegion = {
                'na': 'americas',
                'br': 'americas',
                'euw': 'europe',
                'kr': 'asia'     
            }
            let newRegion = mapDisplayedToRegionToVerboseRegion[displayedRegion]

            const mapDisplayedRegionToPlatform = {
                'na': 'na1',
                'br': 'br1',
                'euw': 'euw1',
                'kr': 'kr'     
            }
            const newPlatform = mapDisplayedRegionToPlatform[displayedRegion]

            let response = await axios.get(`http://localhost:8000/ladder/?&platform=${newPlatform}&region=${newRegion}&page=${params.pageNumber}`);
            console.log(response.data);
            localStorage.setItem('platform', newPlatform);
            localStorage.setItem('region', newRegion);
            localStorage.setItem('displayRegion', displayedRegion) 
            setRankedLadder(response.data);
            globallyUpdateDisplayedRegion(newPlatform)
        } catch (error) {
            console.log({ [error.response.request.status]: error.response.data });
        }
    }

    function updateSelection(platformChoice){

        const selectedPlatform = platformChoice
        // const mapPlatormToRegion = {
        //     'na1': 'americas',
        //     'br1': 'americas',
        //     'euw1': 'europe',
        //     'kr': 'asia'     
        // }
        const mapDisplayedToRegionToVerboseRegion = {
            'na': 'americas',
            'br': 'americas',
            'euw': 'europe',
            'kr': 'asia'     
        }
        let newRegion = mapDisplayedToRegionToVerboseRegion[params.displayRegion]


        const newDisplayRegion = selectedPlatform.replace(/[0-9]+$/, '') // Remove trailing numbers from Platform
        localStorage.setItem('platform', platformChoice);
        localStorage.setItem('region', newRegion);
        localStorage.setItem('displayRegion', newDisplayRegion)
        navigate(`/ladder/${newDisplayRegion}/1`)

        }


    function setPrevPage(){
        navigate(`/ladder/${params.displayRegion}/${parseInt(params.pageNumber)-1}`)

    }

    function setNextPage(){
        navigate(`/ladder/${params.displayRegion}/${parseInt(params.pageNumber)+1}`)

    }


    return (
        <>
            <button onClick={() => updateSelection('na1')} style={{ backgroundColor: params.displayRegion === 'na' ? 'lightblue' : 'white' }}>North America</button>
            <button onClick={() => updateSelection('br1')} style={{ backgroundColor: params.displayRegion === 'br' ? 'lightblue' : 'white' }}>Brazil</button>
            <button onClick={() => updateSelection('euw1')} style={{ backgroundColor: params.displayRegion === 'euw' ? 'lightblue' : 'white' }}>Europe West</button>

            {rankedLadder?.map((player, index) => { 
                let wins = player?.metadata?.wins;
                let losses = player?.metadata?.losses;
                let winrate = Math.round((wins / (wins + losses)) * 100);
                return (
                    <div key={index}>
                        <span>
                            {(index + 1) + (params.pageNumber * 10 - 10) + '.'} <Link to={`/summoners/${params.displayRegion}/${player?.gameName}-${player?.tagLine}`}>{player?.gameName + ' #' + player?.tagLine}</Link> {player?.metadata?.tier} {player?.metadata?.leaguePoints} LP {wins}W {losses}L {winrate}%
                        </span>
                    </div>
                );
            })}

            {/* If page is 1 do not show the prev button, and only show X (say 3) numbers of pages */}
            { parseInt(params.pageNumber) !== 1 ? 
                <button onClick={() => setPrevPage()}>Prev Page </button> :
                null
            }
            { parseInt(params.pageNumber) !== 3 ?
                <button onClick={() => setNextPage()}>Next Page </button> :
                null
            }


        </>
    );
};

export default Ladder;