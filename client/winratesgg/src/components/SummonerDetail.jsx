import React from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'
import MatchHistory from './MatchHistory'

const SummonerDetail = () => {

    const params = useParams()

    const [summonerData, setSummonerData] = useState({})
    const [queueType, setQueueType] = useState("")
    const [queueSpecificGameCount, setQueueSpecificGameCount] = useState(0)
    const location = useLocation()
    const numberOfMatchesToAdd = 2


    // On URL change (clicking on Game Name hyperlink) re-fetch summoner data
    useEffect(() => {
        getSummonerData()
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
            if (specificQueue){
                setQueueSpecificGameCount(response.data.match_history.length)  
            }
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    // Get summoner data from Riot API, update db cache, including match details nested as json
    // async function getSummonerData(routeToRiot=false){
    //     try {
    //         let response = await axios.get(`http://127.0.0.1:8000/summoner-update/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}&routeToRiot=${routeToRiot}`)
    //         console.log(response.data)
    //         setSummonerData(response.data)
    //     } catch (error) {
    //         console.log({[error.response.request.status]: error.response.data})
    //     }
    // }
    // async function getSummonerData(routeToRiot=false){
    //     try {
    //         let response = await axios.get(`http://127.0.0.1:8000/summoner-data-external/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}&routeToRiot=${routeToRiot}`)
    //         console.log(response.data)
    //         setSummonerData(response.data)
    //     } catch (error) {
    //         console.log({[error.response.request.status]: error.response.data})
    //     }
    // }

    // Fetch additional games /w no filter, =false get from databse & no update, =true get from riot API & update databse
    async function getMoreMatchDetails(routeToRiot=false){
        const start = matchHistory?.length
        try {
            let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}&routeToRiot=${routeToRiot}&summonerId=${summonerData?.id}&start=${start}&count=${numberOfMatchesToAdd}`)
            let copyOfSummonerData = {...summonerData}
            copyOfSummonerData.match_details.json = response.data
            setSummonerData(copyOfSummonerData)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }


    // Fetch additional games of a specific type, queueId = game mode
    // routeToRiot=true will retrieve response directly from API, no database updates
    async function getMoreMatchDetailsQueueSpecific(queueId="", routeToRiot=false){
        const start = matchHistory?.length
        let queueUrlParameter = queueId ? `&queue=${queueId}` : ""
        console.log(queueUrlParameter)
        try {
            let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}${queueUrlParameter}&routeToRiot=${routeToRiot}&summonerId=${summonerData?.id}&start=${start}&count=${numberOfMatchesToAdd}`)
            console.log(response.data)
            let copyOfSummonerData = {...summonerData}
            let updatedMatchDetails = copyOfSummonerData.match_details.json.concat(response.data)
            copyOfSummonerData.match_details.json = updatedMatchDetails
            setSummonerData(copyOfSummonerData)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }


    // Get latest date for the summoner being viewed /w update button
    function forceUpdatePage(){
        getSummonerData(null, true)
    }
 ///// STOP HERE FOR TODAY. MAKE SURE TO COMMUNICATE BETWEEN CLIENT AND API THE CURRENT NUMBER OF GAMES FOR A SPECIFIC QUEUE, IF
 ///// THERE ARE CURRENTLY 2 GAMES AND WE REQUEST 7 BUT < 7 ARE RETURNED DO NOT SHOW BUTTON
 ///// ALSO MAKE SURE THIS WORKS WHEN SWITCHING BETWEEN QUEUES
 ///// TEST NAV'ING, MAKE LEADER BOARDS, STYLE, MVP
    function updateQueueType(queueId){
        setQueueType(queueId)
        setQueueSpecificGameCount(() => {
            // Filter the match history based on queueType
            const filteredMatchHistory = summonerData?.match_history?.filter((match) => {
                if (queueId === "") {
                    return true; // Keep all matches if queueType is empty
                } else {
                    console.log("here1", match?.queueId)
                    console.log("here1", queueType)
                    return String(match?.queueId) === String(queueId);
                }
            });
        
            // Return a new object with updated match_history
            return filteredMatchHistory?.length
        });
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

    // Isolate match history from summoner data
    let matchHistory = summonerData?.match_history?.filter((match) => {
        if(queueType === ""){
            return match
        } else if(String(match?.queueId) === String(queueType)){
            return match
        }
    })

    // When clicking on "All Queues" filter undo filtering and re-run fetch match details
    function undoFilterAndGetRecentMatchDetails(){
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
            <button onClick={()=>undoFilterAndGetRecentMatchDetails()}>All</button><button onClick={()=>updateQueueType(450)}>ARAM</button>
            <button onClick={()=>updateQueueType(420)}>Ranked Solo/Duo</button><button onClick={()=>updateQueueType(400)}>Normal</button><button onClick={()=>updateQueueType(490)}>Quick Play</button><button onClick={()=>updateQueueType(440)}>Flex</button>
            <button onClick={()=>updateQueueType(700)}>Clash</button><button onClick={()=>updateQueueType(1300)}>Nexus Blitz</button><button onClick={()=>updateQueueType(1700)}>Arena</button>
            <h1>{params.gameName} #{params.tagLine}</h1>
            <img width="75" height="75" alt="profile icon" src={process.env.PUBLIC_URL + `/assets/profile_icons/${summonerData?.profileIconId}.png`} /> 
            <h2>Ranked Solo Queue:</h2>
            {/* <img width="100" height="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank=${summonerOverview?.tier?.toLowerCase()}.png`} />  */}
            <img width="100" height="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank=${formatRank(summonerOverview)}.png`} /> 
            <plaintext>{summonerOverview?.tier} {summonerOverview?.rank} {summonerOverview?.leaguePoints} LP</plaintext>
            <plaintext>Wins: {summonerOverview?.wins} Losses:{summonerOverview?.losses}</plaintext>
            <plaintext>Win Rate {Math.round(summonerOverview?.wins/(summonerOverview?.wins + summonerOverview?.losses)*100)}%</plaintext>
            <plaintext>Last Updated {formatLastUpdateTime(summonerData?.updated_at)}</plaintext>
            <button onClick={()=>forceUpdatePage()}>Update</button>
            <MatchHistory matchHistory={matchHistory} setSummonerData={setSummonerData} summonerData={summonerData}/>
            {queueType ? 
                <button onClick={()=>getSummonerData(matchHistory?.length + 5, false, queueType)}>Fetch More Games (queue specific, remove this text)</button> :
                <button onClick={()=>getSummonerData(matchHistory?.length + 5, false)}>Fetch More Games (all, remove this text)</button>
            }            

            {/* {queueType && matchHistory?.length === summonerData?.max_display_length ?
                <button onClick={() => getSummonerData(matchHistory?.length + 5, false, queueType)}>Fetch More Games (queue specific, remove this text)</button> :
                (!queueType || matchHistory?.length === summonerData?.max_display_length) &&
                <button onClick={() => getSummonerData(matchHistory?.length + 5, false)}>Fetch More Games (all, remove this text)</button>
            } */}
        </>
    )
}

export default SummonerDetail

