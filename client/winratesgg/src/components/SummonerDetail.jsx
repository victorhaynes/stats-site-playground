import React from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'
import MatchHistory from './MatchHistory'

const SummonerDetail = () => {

    const params = useParams()

    const [summonerData, setSummonerData] = useState({})
    const [queueType, setQueueType] = useState("")
    const location = useLocation()
    const numberOfMatchesToAdd = 2


    // On URL change (clicking on Game Name hyperlink) re-fetch summoner data
    useEffect(() => {
        getSummonerData()
    },[location.pathname])


    // Get summoner data from db cache, including match details nested as json
    async function getSummonerData(limit=null, update=false){
        let url = `http://127.0.0.1:8000/summoner/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}`
        
        url += limit ? `&limit=${limit}` : '';
        url += update ? `&update=${update}` : '';

        try {
            let response = await axios.get(url)
            console.log(response.data)
            setSummonerData(response.data)
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
        getSummonerData(true)
    }


    // Calculate and display time since last update
    function formatLastUpdateTime(summonerOverview){
        let lastUpdatedText = "time unknown"
        try {
            let lastUpdated = summonerOverview?.overviews[0]?.updated_at
            console.log(lastUpdated)
            let yearUpdated = lastUpdated.split("-")[0]
            let monthUpdated = lastUpdated.split("-")[1]
            let dayUpdated = lastUpdated.split("-")[2].split("T")[0]
            let hoursMinsSeconds = lastUpdated.split("T")[1].split(":")
            let hoursUpdated = hoursMinsSeconds[0]
            let minutesUpdated = hoursMinsSeconds[1]
            let secondsUpdated = hoursMinsSeconds[2].split(".")[0]

            let now = new Date();
            let currentDay = String(now.getDate()).padStart(2, '0');
            let currentMonth = String(now.getMonth() + 1).padStart(2, '0'); //January is 0!
            let currentYear = now.getFullYear();
            let currentHours = now.getHours();
            let currentMinutes = now.getMinutes();
            let currentSeconds = now.getSeconds();

            let elapsedYears = currentYear - yearUpdated
            let elapsedMonths = currentMonth - monthUpdated
            let elapsedDays = currentDay - dayUpdated
            let elapsedHours = currentHours - hoursUpdated
            let elapsedMinutes = currentMinutes - minutesUpdated
            let elapsedSeconds = currentSeconds - secondsUpdated

            if (elapsedYears){
                lastUpdatedText = `${elapsedYears} year(s) ago`
            } else if (elapsedMonths){
                lastUpdatedText = `${elapsedMonths} months(s) ago`
            } else if (parseInt(elapsedDays)*24 + elapsedHours >= 24) {
                lastUpdatedText = `${elapsedDays} days(s) ago`
            } else if (parseInt(elapsedHours)*60 + elapsedMinutes >= 60){
                lastUpdatedText = `${elapsedHours} hours(s) ago`
                console.log("ONE")
            } else if (parseInt(elapsedMinutes)*60 + elapsedSeconds >= 60){
            lastUpdatedText = `${elapsedMinutes} minutes(s) ago`
            } else if (elapsedSeconds > 0){
                lastUpdatedText = `${elapsedSeconds} seconds(s) ago`
            } else if (parseInt(elapsedSeconds) === 0){
                console.log(lastUpdatedText)
                lastUpdatedText = 'just now'
                console.log(lastUpdatedText)
            }

        } catch (error){
            return lastUpdatedText
        }
        return lastUpdatedText
    }

    // Isolate the summoner overview from summoner data, handle index error if nothing is there
    let summonerOverview = {}
    try {
        summonerOverview = summonerData?.overviews[0]?.metadata
        } catch (error){
        summonerOverview = {}
    }
    console.log("OVERVIEW:", summonerOverview)

    // Isolate the updated_at field from summoner data.summoner overview, handle index error if nothing is there
    let lastUpdated = ""
    try {
        lastUpdated = summonerData?.overviews[0]?.updated_at
    } catch (error){
        lastUpdated = "Unknown"
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
        getMoreMatchDetails(false)
    }

    function formatRank(summonerOverview){
        const capitalizedFirstLetter = summonerOverview?.tier?.charAt(0)?.toUpperCase()
        const remainingLetters = summonerOverview?.tier?.slice(1).toLowerCase()
        console.log(1, capitalizedFirstLetter)
        console.log(2, remainingLetters)
        return capitalizedFirstLetter + remainingLetters

    }


    return (
        <>
            <button onClick={()=>undoFilterAndGetRecentMatchDetails()}>All</button><button onClick={()=>setQueueType(450)}>ARAM</button>
            <button onClick={()=>setQueueType(420)}>Ranked Solo/Duo</button><button onClick={()=>setQueueType(400)}>Normal</button><button onClick={()=>setQueueType(490)}>Quick Play</button><button onClick={()=>setQueueType(440)}>Flex</button>
            <button onClick={()=>setQueueType(700)}>Clash</button><button onClick={()=>setQueueType(1300)}>Nexus Blitz</button><button onClick={()=>setQueueType(1700)}>Arena</button>
            <h1>{params.gameName} #{params.tagLine}</h1>
            <img width="75" height="75" alt="profile icon" src={process.env.PUBLIC_URL + `/assets/profile_icons/${summonerData?.profileIconId}.png`} /> 
            <h2>Ranked Solo Queue:</h2>
            {/* <img width="100" height="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank=${summonerOverview?.tier?.toLowerCase()}.png`} />  */}
            <img width="100" height="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank=${formatRank(summonerOverview)}.png`} /> 
            <plaintext>{summonerOverview?.tier} {summonerOverview?.rank} {summonerOverview?.leaguePoints} LP</plaintext>
            <plaintext>Wins: {summonerOverview?.wins} Losses:{summonerOverview?.losses}</plaintext>
            <plaintext>Win Rate {Math.round(summonerOverview?.wins/(summonerOverview?.wins + summonerOverview?.losses)*100)}%</plaintext>
            {/* <plaintext>Last Updated {formatLastUpdateTime(summonerOverview)}</plaintext> */}
            <plaintext>Last Updated {lastUpdated}</plaintext>
            <button onClick={()=>forceUpdatePage()}>Update</button>
            <MatchHistory matchHistory={matchHistory} setSummonerData={setSummonerData} summonerData={summonerData}/>
            {queueType? <button onClick={()=>getMoreMatchDetailsQueueSpecific(queueType, true)}>Fetch More Games (specific, remove this text)</button> :
            <button onClick={()=>getMoreMatchDetails(true)}>Fetch More Games (all, remove this text)</button>}
        </>
    )
}

export default SummonerDetail

