import React from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'
import MatchHistory from './MatchHistory'

const SummonerDetail = () => {

    const params = useParams()
    const [summonerOverview, setSummonerOverview] = useState({})
    const [matchHistory, setMatchHistory] = useState([])
    const location = useLocation()

    useEffect(() => {
        fetchSummonerOverview()
        fetchMatchHistory()
    },[location.pathname])


    async function fetchSummonerOverview(update=false){
        try {
            let response = await axios.get(`http://127.0.0.1:8000/summoner-overview/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}&update=${update}`)
            console.log(response.data)
            setSummonerOverview(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }


    async function fetchMatchHistory(queueId="", update=false){

        let queueUrlParameter = queueId ? `&queue=${queueId}` : ""
        console.log(queueUrlParameter)
        try {
            let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&gameName=${params.gameName}&tagLine=${params.tagLine}${queueUrlParameter}&update=${update}`)
            console.log(response.data)
            setMatchHistory(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    function forceUpdatePage(){
        fetchSummonerOverview(true)
        fetchMatchHistory("", true)
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


    return (
        <>
            <button onClick={()=>fetchMatchHistory()}>All</button><button onClick={()=>fetchMatchHistory("420")}>Ranked Solo/Duo</button><button onClick={()=>fetchMatchHistory("400")}>Normal</button><button onClick={()=>fetchMatchHistory("490")}>Quick Play</button><button onClick={()=>fetchMatchHistory("450")}>ARAM</button><button onClick={()=>fetchMatchHistory("440")}>Flex</button>
            <button onClick={()=>fetchMatchHistory("700")}>Clash</button><button onClick={()=>fetchMatchHistory("1300")}>Nexus Blitz</button><button onClick={()=>fetchMatchHistory("1700")}>Arena</button>
            <h1>{params.gameName} #{params.tagLine}</h1>
            <img width="75" height="75" alt="profile icon" src={process.env.PUBLIC_URL + `/assets/profile_icons/${summonerOverview?.profileIcon}.png`} /> 
            <h2>Ranked Solo Queue:</h2>
            <img width="100" height="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank${summonerOverview?.tier?.toLowerCase()}.png`} /> 
            <plaintext>{summonerOverview.tier} {summonerOverview.rank}</plaintext>
            <plaintext>Wins: {summonerOverview.wins} Losses:{summonerOverview.losses}</plaintext>
            <plaintext>Win Rate {Math.round(summonerOverview.wins/(summonerOverview.wins + summonerOverview.losses)*100)}%</plaintext>
            <plaintext>Last Updated {formatLastUpdateTime(summonerOverview)}</plaintext>
            <button onClick={()=>forceUpdatePage()}>Update</button>
            <MatchHistory matchHistory={matchHistory} setMatchHistory={setMatchHistory} setSummonerOverview={setSummonerOverview}/>
        </>
    )
}

export default SummonerDetail

