import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const Ladder = () => {
    const [rankedLadder, setRankedLadder] = useState([]);
    const [platform, setPlatform] = useState('na1');
    const [region, setRegion] = useState('americas');
    const [displayRegion, setDisplayRegion] = useState('na')

    const [selectionUpdate, setSelectionUpdate] = useState('na1americas010')
    const [page, setPage] = useState(1)


    // UPDATE THIS SO IT WORKS FOR TIERS !!!!!!!!!!!!!!!!!! 
    const navigate = useNavigate()
    const params = useParams()

    useEffect(() => {
        getLeaderboard();
    }, [selectionUpdate, page]);

    async function getLeaderboard() {        
        try {
            let response = await axios.get(`http://localhost:8000/ladder/?&platform=${platform}&region=${region}&page=${params.pageNumber}`);
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
        setDisplayRegion(selectedPlatform.replace(/[0-9]+$/, ''))
        const newDisplayRegion = selectedPlatform.replace(/[0-9]+$/, '')
        navigate(`/ladder/${newDisplayRegion}/1`)

        }


    function setPrevPage(){
        navigate(`/ladder/${displayRegion}/${page-1}`)
        setPage ((prev) => page - 1)

    }

    function setNextPage(){
        navigate(`/ladder/${displayRegion}/${page+1}`)
        setPage ((prev) => page + 1)

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
                            {/* {index + 1 + start + '.'} <Link to={`/summoners/${displayRegion}/${player?.gameName}-${player?.tagLine}`}>{player?.gameName + ' #' + player?.tagLine}</Link> {player?.metadata?.tier} {player?.metadata?.leaguePoints} LP {wins}W {losses}L {winrate}% */}
                            {(index + 1) + (params.pageNumber * 10 - 10) + '.'} <Link to={`/summoners/${displayRegion}/${player?.gameName}-${player?.tagLine}`}>{player?.gameName + ' #' + player?.tagLine}</Link> {player?.metadata?.tier} {player?.metadata?.leaguePoints} LP {wins}W {losses}L {winrate}%
                        </span>
                    </div>
                );
            })}
            
            {/* If page is 1 do not show the prev button, and only show X (say 3) numbers of pages */}
            <button onClick={() => setPrevPage()}>Prev Page </button>
            <button onClick={() => setNextPage()}>Next Page </button>


        </>
    );
};

export default Ladder;