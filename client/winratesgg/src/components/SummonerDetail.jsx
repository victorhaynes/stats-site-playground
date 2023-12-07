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
        fetchSummonerOveview()
        fetchMatchHistory()
    },[location.pathname])


    async function fetchSummonerOveview(update=false){
        try {
            let response = await axios.get(`http://127.0.0.1:8000/summoner-overview/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}&update=${update}`)
            console.log(response.data)
            setSummonerOverview(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    async function fetchMatchHistory(queueId=""){

        let queueUrlParameter = queueId ? `&queue=${queueId}` : ""
        console.log(queueUrlParameter)
        try {
            let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&gameName=${params.gameName}&tagLine=${params.tagLine}${queueUrlParameter}`)
            console.log(response.data)
            setMatchHistory(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
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
            <MatchHistory matchHistory={matchHistory} setMatchHistory={setMatchHistory} setSummonerOverview={setSummonerOverview}/>
        </>
    )
}

export default SummonerDetail

