import React from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'
import MatchHistory from './MatchHistory'
import Loading from './Loading'
import Error from './Error'

const SummonerDetail = ({region, platform, globallyUpdateDisplayedRegion}) => {

    const params = useParams()
    const displayRegion = params.displayRegion
    const displayName = params.displayNameZipped
    const [gameName, tagLine] = displayName.split("-")


    const [summonerData, setSummonerData] = useState({})
    const [queueType, setQueueType] = useState("")
    const [showFetchButtonForQueueType, setShowFetchButtonForQueueType] = useState(true)
    const [showFetchButtonForAllGames, setShowFetchButtonForAllGames] = useState(true)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(false)
    const location = useLocation()

    // introduce a sub-loading component. For only when part of a page loading, in this case the match history?
    // or just conditionally render the match history all together?

    // On URL change (clicking on Game Name hyperlink) re-fetch summoner data
    useEffect(() => {
        getSummonerData()
        setShowFetchButtonForQueueType(true)
        setShowFetchButtonForAllGames(true)
    },[location.pathname])


    // Get summoner data from db cache, including match details nested as json
    async function getSummonerData(queryLimit=null, update=false, specificQueue=false){
        setLoading(true)
        const displayedRegion = params.displayRegion
        const mapDisplayedToRegionToVerboseRegion = {
            'na': 'americas',
            'br': 'americas',
            'euw': 'europe',
            'kr': 'asia'     
        }
        const newRegion = mapDisplayedToRegionToVerboseRegion[displayedRegion]

        const mapDisplayedRegionToPlatform = {
            'na': 'na1',
            'br': 'br1',
            'euw': 'euw1',
            'kr': 'kr'     
        }
        const newPlatform = mapDisplayedRegionToPlatform[displayedRegion]


        // let url = `http://127.0.0.1:8000/summoner/?region=${region}&platform=${platform}&gameName=${gameName}&tagLine=${tagLine}`
        let url = `http://127.0.0.1/api/summoner/?region=${newRegion}&platform=${newPlatform}&gameName=${gameName}&tagLine=${tagLine}` // port :8000 is factored out, NGINX will route from default port 80 to appropriate server
        
        url += queryLimit ? `&limit=${queryLimit}` : ''
        url += update ? `&update=${update}` : ''
        url += specificQueue ? `&queueId=${specificQueue}` : ''

        try {
            let response = await axios.get(url)
            console.log(response.data)
            setSummonerData(response.data)
            globallyUpdateDisplayedRegion(newPlatform)
            setLoading(false)
            setError(false)
            if (!specificQueue && response.data.match_history.length < queryLimit){
                setShowFetchButtonForAllGames(false)
            } else if (specificQueue && response.data.match_history.length < queryLimit){
                setShowFetchButtonForQueueType(false)
            }
        } catch (error) {
            // console.log({[error.response.request.status]: error.response.data})
            console.log(error.response.data)
            setLoading(false)
            if (error.response.status == 500){
                setError({"message": error.response.data, status_code: error.response.status})
            } else {
                setError({...error.response.data, status_code: error.response.status})
            }
        }
    }

    // Upon rendering this page update state at App level using the params
    // This is necessary so a user can enter the app through a direct summoner profile page
    // without setting state in the search form



    // Get latest update for the summoner being viewed /w update button
    function forceUpdatePage(){
        getSummonerData(null, true)
    }

    ///// STOP HERE FOR TODAY. MAKE SURE TO COMMUNICATE BETWEEN CLIENT AND API THE CURRENT NUMBER OF GAMES FOR A SPECIFIC QUEUE, IF
    ///// THERE ARE CURRENTLY 2 GAMES AND WE REQUEST 7 BUT < 7 ARE RETURNED DO NOT SHOW BUTTON TO ASK FOR MORE
    ///// ALSO MAKE SURE THIS WORKS WHEN SWITCHING BETWEEN QUEUES
    ///// TEST NAV'ING, MAKE LEADER BOARDS, STYLE, MVP
    // MIGHT BE BUGGY WHEN GOING FROM NORMAL TO ARENA BACK TO NORMAL?
    // THIS MIGHT ACTUALLY BE WORKING CORRECTLY, THERE'S ONLY SO MANY NORMAL AND ARENA GAMES FOR MY OWN PUUID
    function updateQueueFilterAndGetRecentMatchDetails(queueId){
        setQueueType(queueId)
        setShowFetchButtonForQueueType(true)
        if (queueId){
            getSummonerData(3, false, queueId) // IN PROD THIS SHOULD BE SAME AS DEFAULT ALL GAMES AMOUNT 
        }
    }

    // Calculate and display time since last update
    function formatLastUpdateTime(timestamp){
        const currentTime = new Date();
        const targetTime = new Date(timestamp);
        if (!timestamp || (isNaN(targetTime.getTime()))) return ': Unknown.';

        const difference = currentTime - targetTime;
    
        // Convert milliseconds to seconds
        const seconds = Math.floor(difference / 1000);
    
        // Define time units in seconds
        const minute = 60;
        const hour = minute * 60;
        const day = hour * 24;
        const month = day * 30; // Approximate
        const year = day * 365; // Approximate
    
        if (seconds < minute) {
            return `A Moment Ago`;
        } else if (seconds < hour) {
        const minutes = Math.floor(seconds / minute);
            return `${minutes} Minute${minutes !== 1 ? 's' : ''} ago`;
        } else if (seconds < day) {
        const hours = Math.floor(seconds / hour);
            return `${hours} Hour${hours !== 1 ? 's' : ''} ago`;
        } else if (seconds < month) {
        const days = Math.floor(seconds / day);
            return `${days} Day${days !== 1 ? 's' : ''} ago`;
        } else if (seconds < year) {
        const months = Math.floor(seconds / month);
            return `${months} Month${months !== 1 ? 's' : ''} ago`;
        } else {
        const years = Math.floor(seconds / year);
            return `${years} Year${years !== 1 ? 's' : ''} ago`;
        }
  }


    // Isolate the summoner overview from summoner data, handle index error if nothing is there
    let summonerOverview = {}
    try {
        summonerOverview = summonerData?.overviews[0]?.metadata
        } catch (error){
        summonerOverview = {}
    }

    // Isolate match history from summoner data ---- IS THIS NEEDED ANYMORE IF I AM RE FETCHING QUEUE DATA INSTEAD OF FILTERING IT?
    // Isolate match history from summoner data ---- IS THIS NEEDED ANYMORE IF I AM RE FETCHING QUEUE DATA INSTEAD OF FILTERING IT?
    // Isolate match history from summoner data ---- IS THIS NEEDED ANYMORE IF I AM RE FETCHING QUEUE DATA INSTEAD OF FILTERING IT?
    // SHOULD I JUST PASS THE SUMMONERDATA.MATCH_HISTORY DIRECTLY INSTEAD?
    // let matchHistory = summonerData?.match_history?.filter((match) => {
    //     if(queueType === ""){
    //         return match
    //     } else if(String(match?.queueId) === String(queueType)){
    //         return match
    //     }
    // })

    let matchHistory = summonerData?.match_history

    // When clicking on "All Queues" filter undo filtering and re-run fetch match details
    function undoQueueFilterAndGetRecentMatchDetails(){
        setQueueType("")
        getSummonerData(false)
    }

    function formatRank(summonerOverview){
        const capitalizedFirstLetter = summonerOverview?.tier?.charAt(0)?.toUpperCase()
        const remainingLetters = summonerOverview?.tier?.slice(1).toLowerCase()
        return capitalizedFirstLetter + remainingLetters
    }


    return (
        <>
            { loading ? <Loading/> : 
              error ? <Error error={error}/> :
                <>
                    <button onClick={()=>undoQueueFilterAndGetRecentMatchDetails()}>All</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(450)}>ARAM</button>
                    <button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(420)}>Ranked Solo/Duo</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(400)}>Normal</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(490)}>Quick Play</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(440)}>Flex</button>
                    <button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(700)}>Clash</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(1300)}>Nexus Blitz</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(1700)}>Arena</button>
                    <h1>{gameName} #{tagLine}</h1>
                    <img width="75" height="75" alt="profile icon" src={process.env.PUBLIC_URL + `/assets/profile_icons/${summonerData?.profileIconId}.png`} /> 
                    <h2>Ranked Solo Queue:</h2>
                    <img width="100" height="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank=${formatRank(summonerOverview)}.png`} /> 
                    <plaintext>{summonerOverview?.tier} {summonerOverview?.rank} {summonerOverview?.leaguePoints} LP</plaintext>
                    <plaintext>Wins: {summonerOverview?.wins} Losses:{summonerOverview?.losses}</plaintext>
                    <plaintext>Win Rate {Math.round(summonerOverview?.wins/(summonerOverview?.wins + summonerOverview?.losses)*100)}%</plaintext>
                    <plaintext>Last Updated {formatLastUpdateTime(summonerData?.updated_at)}</plaintext>
                    <button onClick={()=>forceUpdatePage()}>Update</button>
                    <MatchHistory matchHistory={matchHistory} setSummonerData={setSummonerData} summonerData={summonerData}/>
                    {queueType && showFetchButtonForQueueType ? 
                        <button onClick={()=>getSummonerData(matchHistory?.length + 3, false, queueType)}>Fetch More Games (queue specific, remove this text)</button> : 
                        <>queue button hiiding (delete this)</>
                    }
                    {!queueType && showFetchButtonForAllGames ? 
                        <button onClick={()=>getSummonerData(matchHistory?.length + 3, false)}>Fetch More Games (all, remove this text)</button> :
                        <>all button hiding (delete this)</>
                    }           
                </>
            }
    </>
    )
}

export default SummonerDetail

