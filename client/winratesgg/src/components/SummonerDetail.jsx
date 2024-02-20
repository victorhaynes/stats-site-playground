import React from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'
import MatchHistory from './MatchHistory'

const SummonerDetail = () => {

    const params = useParams()



    // const [summonerOverviewz, setSummonerOverview] = useState({})
    // const [matchHistoryz, setMatchHistory] = useState([])


    const [summonerData, setSummonerData] = useState({})
    const [riotAPIstartIndex, setRiotAPIstartIndex] = useState(0)
    const [numberOfMatchesToAdd, setNumberOfMatchesToAdd] = useState(2) // SET TO 15 in PRODUCTION
    const [queueType, setQueueType] = useState("")
    const location = useLocation()

    useEffect(() => {
        getSummonerData()
    },[location.pathname])


    async function getSummonerData(routeToRiot=false){
        // setQueueType("")
        try {
            let response = await axios.get(`http://127.0.0.1:8000/summoner-data-external/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}&routeToRiot=${routeToRiot}`)
            console.log(response.data)
            setSummonerData(response.data)
            setRiotAPIstartIndex(response.data.match_details.json.length)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    // WORK ON THIS ----------------- MAKE A PIECE OF STATE THAT IS THE LENGTH OF THE MATCH HISTORY ARRAY
    // WHEN USER WANTS MORE HISTORY ADD A BUTTON THAT WILL SEND A REQUEST AND INCLUDE THE COUNTER, SUCCESSFUL RESPONSE INCREMENT COUNTER, KEEP APPENDING TO HISTORY
    async function getMoreMatchDetails(routeToRiot=false){
        // let startIndex = start? start : matchHistory?.length
        const start = matchHistory?.length
        console.log(start)
        // let queueUrlParameter = queueId ? `&queue=${queueId}` : ""
        // console.log(queueUrlParameter)

        try {
            // let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}${queueUrlParameter}&routeToRiot=${routeToRiot}&summonerId=${summonerData?.id}&start=${riotAPIstartIndex}&count=${numberOfMatchesToAdd}`)
            let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}&routeToRiot=${routeToRiot}&summonerId=${summonerData?.id}&start=${start}&count=${numberOfMatchesToAdd}`)
            console.log(response.data)
            let copyOfSummonerData = {...summonerData}
            copyOfSummonerData.match_details.json = response.data
            setSummonerData(copyOfSummonerData)
            // setSummonerData((oldSummonerData) => {
            //     let copyOfSummonerData = oldSummonerData
            //     copyOfSummonerData.match_details.json = response.data
            //     return copyOfSummonerData
            // })
            // setRiotAPIstartIndex(response.data.length)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }


    // WORK ON THIS!!!!!!!! this is working for ARAM. 
    // TODO: determine starting index dynamically, make sure subsequent add-ons work, make sure works for all game modes
    // TODO: consider getting rid of queueID from abvove function & renaming to getMoreGeneralMatchDetails
    // TODO: look at the way state is being updated above and consider if that is best practice
    async function getMoreMatchDetailsQueueSpecific(queueId="", routeToRiot=false){
        // this start index needs to be synchronous/not in state because we have to filter the response (in state) and access its length immediately
        // unlike theriotAPIstartIndex ? state variable which is just the length of the response /w no manipulation
        const start = matchHistory?.length
        let queueUrlParameter = queueId ? `&queue=${queueId}` : ""
        console.log(queueUrlParameter)
        try {
            let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}${queueUrlParameter}&routeToRiot=${routeToRiot}&summonerId=${summonerData?.id}&start=${start}&count=${numberOfMatchesToAdd}`)
            console.log(response.data)
            let copyOfSummonerData = {...summonerData}
            // for (let i = 0; i < response.data.length; i++){
            //     copyOfSummonerData.match_details.json.push(response.data[i])
            // }
            // copyOfSummonerData.match_details.json.push({})

            let updatedMatchDetails = copyOfSummonerData.match_details.json.concat(response.data)
            copyOfSummonerData.match_details.json = updatedMatchDetails
            setSummonerData(copyOfSummonerData)
            // setRiotAPIstartIndex((oldValue) => oldValue + numberOfMatchesToAdd)
            // setRiotAPIstartIndex(response.data.length)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }


    function forceUpdatePage(){
        getSummonerData(true)
    }


    function formatLastUpdateTime(summonerOverview){
        let lastUpdatedText = "time unknown"
        try {
            let lastUpdated = summonerOverview?.updated_at
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


    let summonerOverview = {}
    try {
        summonerOverview = summonerData?.summoner_overviews[0]?.json
    } catch (error){
        summonerOverview = {}
    }


    let matchHistory = summonerData?.match_details?.json?.filter((match) => {
        if(queueType === ""){
            return match
        } else if(String(match?.info?.queueId) === String(queueType)){
            return match
        }
    })


    function undoFilterAndGetRecentMatchDetails(){
        setQueueType("")
        getMoreMatchDetails(false)
    }

    // function filterAndResetRiotStartIndex(queueId){
    //     setRiotAPIstartIndex(matchHistory.length)
    //     setQueueType(queueId)
    // }



    return (
        <>
            {/* Fix queue slicing once we implement match history updates alone */}
            {/* <button onClick={()=>getMoreMatchDetails("", false)}>All</button><button onClick={()=>getMoreMatchDetails(420, true)}>Ranked Solo/Duo</button><button onClick={()=>getMoreMatchDetails(400, true)}>Normal</button><button onClick={()=>getMoreMatchDetails(490, true)}>Quick Play</button><button onClick={()=>getMoreMatchDetails(450, true)}>ARAM</button><button onClick={()=>getMoreMatchDetails(440, true)}>Flex</button>
            <button onClick={()=>getMoreMatchDetails(700, true)}>Clash</button><button onClick={()=>getMoreMatchDetails(1300, true)}>Nexus Blitz</button><button onClick={()=>getMoreMatchDetails(1700, true)}>Arena</button> */}
            <button onClick={()=>undoFilterAndGetRecentMatchDetails()}>All</button><button onClick={()=>setQueueType(450)}>ARAM</button>
            <button onClick={()=>setQueueType(420)}>Ranked Solo/Duo</button><button onClick={()=>setQueueType(400)}>Normal</button><button onClick={()=>setQueueType(490)}>Quick Play</button><button onClick={()=>setQueueType(440)}>Flex</button>
            <button onClick={()=>setQueueType(700)}>Clash</button><button onClick={()=>setQueueType(1300)}>Nexus Blitz</button><button onClick={()=>setQueueType(1700)}>Arena</button>
            <h1>{params.gameName} #{params.tagLine}</h1>
            <img width="75" height="75" alt="profile icon" src={process.env.PUBLIC_URL + `/assets/profile_icons/${summonerData?.profileIconId}.png`} /> 
            <h2>Ranked Solo Queue:</h2>
            <img width="100" height="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank${summonerOverview?.tier?.toLowerCase()}.png`} /> 
            <plaintext>{summonerOverview?.tier} {summonerOverview?.rank}</plaintext>
            <plaintext>Wins: {summonerOverview?.wins} Losses:{summonerOverview?.losses}</plaintext>
            <plaintext>Win Rate {Math.round(summonerOverview?.wins/(summonerOverview?.wins + summonerOverview?.losses)*100)}%</plaintext>
            <plaintext>Last Updated {formatLastUpdateTime(summonerOverview)}</plaintext>
            <button onClick={()=>forceUpdatePage()}>Update</button>
            <MatchHistory matchHistory={matchHistory} setSummonerData={setSummonerData} summonerData={summonerData}/>
            {queueType? <button onClick={()=>getMoreMatchDetailsQueueSpecific(queueType, true)}>Fetch More Games (specific, remove this text)</button> :
            <button onClick={()=>getMoreMatchDetails(true)}>Fetch More Games (all, remove this text)</button>}
        </>
    )
}

export default SummonerDetail

