import React from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'
import MatchHistory from '../client/winratesgg/src/components/MatchHistory'

const SummonerDetail = () => {

    const params = useParams()

    const [summonerData, setSummonerData] = useState({})
    const [queueType, setQueueType] = useState("")
    const [showFetchButtonForQueueType, setShowFetchButtonForQueueType] = useState(true)
    const [showFetchButtonForAllGames, setShowFetchButtonForAllGames] = useState(true)
    const location = useLocation()


    // On URL change (clicking on Game Name hyperlink) re-fetch summoner data
    useEffect(() => {
        getSummonerData()
        setShowFetchButtonForQueueType(true)
        setShowFetchButtonForAllGames(true)
    },[location.pathname])


    // Get summoner data from db cache, including match details nested as json
    async function getSummonerData(queryLimit=null, update=false, specificQueue=false){
        let url = `http://127.0.0.1:8000/summoner/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}`
        
        url += queryLimit ? `&limit=${queryLimit}` : ''
        url += update ? `&update=${update}` : ''
        url += specificQueue ? `&queueId=${specificQueue}` : ''

        try {
            let response = await axios.get(url)
            console.log(response.data)
            setSummonerData(response.data)
            if (!specificQueue && response.data.match_history.length < queryLimit){
                setShowFetchButtonForAllGames(false)
            } else if (specificQueue && response.data.match_history.length < queryLimit){
                setShowFetchButtonForQueueType(false)
            }
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }


    // Get latest date for the summoner being viewed /w update button
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
            <button onClick={()=>undoQueueFilterAndGetRecentMatchDetails()}>All</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(450)}>ARAM</button>
            <button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(420)}>Ranked Solo/Duo</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(400)}>Normal</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(490)}>Quick Play</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(440)}>Flex</button>
            <button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(700)}>Clash</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(1300)}>Nexus Blitz</button><button onClick={()=>updateQueueFilterAndGetRecentMatchDetails(1700)}>Arena</button>
            <h1>{params.gameName} #{params.tagLine}</h1>
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
    )
}

export default SummonerDetail