import React from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'

const SummonerDetail = () => {

    const params = useParams()
    const [summonerOverview, setSummonerOverview] = useState({})

    useEffect(() => {
        fetchSummonerOveview()
        fetchMatchHistory()
    },[])

    
    async function fetchSummonerOveview(){
        try {
            let response = await axios.get(`http://127.0.0.1:8000/summoner-overview/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}`)
            console.log(response.data)
            setSummonerOverview(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    async function fetchMatchHistory(){
        try {
            let response = await axios.get(`http://127.0.0.1:8000/match-history/?region=${params.region}&gameName=${params.gameName}&tagLine=${params.tagLine}`)
            console.log(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    function renderMatchHistory(){
        // write function that maps through match history state and renders elements
    }

    return (
        <>
            <h1>{params.gameName} #{params.tagLine}</h1>
            <h2>Ranked Solo Queue:</h2>
            <img width="150" height ="150" src={process.env.PUBLIC_URL + `/assets/Rank${summonerOverview?.tier?.toLowerCase()}.png`} /> 
            <plaintext>{summonerOverview.tier} {summonerOverview.rank}</plaintext>
            <plaintext>Wins: {summonerOverview.wins} Losses:{summonerOverview.losses}</plaintext>
            <plaintext>Win Rate {Math.round(summonerOverview.wins/(summonerOverview.wins + summonerOverview.losses)*100)}%</plaintext>
        </>
    )
}

export default SummonerDetail


   // function renderRank(){
    //     let iconPath = ""
    //     switch(summonerOverview.tier){
    //         case "IRON":
    //             return iconPath = "/RankIron.png"
    //         case "BRONZE":
    //             return iconPath = "/RankBronze.png"
    //         case "SILVER":
    //             return iconPath = "/RankSilver.png"
    //         case "GOLD":
    //             return iconPath = "/RankGold.png"
    //         case "PLATINUM":
    //             return iconPath = "/RankPlatinum.png"
    //         case "EMERALD":
    //             return iconPath = "/RankEmerald.png"
    //         case "DIAMOND":
    //             return iconPath = "/RankDiamond.png"
    //         case "MASTER":
    //             return iconPath = "/RankMaster.png"
    //         case "GRANDMASTER":
    //             return iconPath = "/RannkGrandMaster.png"
    //         case "CHALLENGER":
    //             return iconPath = "/RankChallenger.png"

    //     }
    // }