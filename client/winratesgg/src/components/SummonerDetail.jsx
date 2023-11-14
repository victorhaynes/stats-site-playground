import React from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'

const SummonerDetail = () => {

    const params = useParams()
    const [summonerOverview, setSummonerOverview] = useState({})
    const [matchHistory, setMatchHistory] = useState([])

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

function renderMatchHistory(){
    return matchHistory.map((match)=>{
        return (
            <>
                <div>
                    <>Game ID: {match?.info?.gameId}<br></br></>
                    {match?.info?.participants?.map((participant)=>{
                        return <>{participant.summonerName}<br></br></>
                    })}
                    <>queueId: {match?.info?.queueId}</>
                </div>
                <br></br>
            </>
        )
    })
}

return (
    <>
        <button onClick={fetchMatchHistory}>All</button><button onClick={()=>fetchMatchHistory("420")}>Ranked Solo/Duo</button><button onClick={()=>fetchMatchHistory("400")}>Normal</button><button onClick={()=>fetchMatchHistory("450")}>ARAM</button><button onClick={()=>fetchMatchHistory("440")}>Flex</button>
        <button onClick={()=>fetchMatchHistory("700")}>Clash</button><button onClick={()=>fetchMatchHistory("1300")}>Nexus Blitz</button>
        <h1>{params.gameName} #{params.tagLine}</h1>
        <h2>Ranked Solo Queue:</h2>
        <img width="150" height ="150" src={process.env.PUBLIC_URL + `/assets/Rank${summonerOverview?.tier?.toLowerCase()}.png`} /> 
        <plaintext>{summonerOverview.tier} {summonerOverview.rank}</plaintext>
        <plaintext>Wins: {summonerOverview.wins} Losses:{summonerOverview.losses}</plaintext>
        <plaintext>Win Rate {Math.round(summonerOverview.wins/(summonerOverview.wins + summonerOverview.losses)*100)}%</plaintext>
        {renderMatchHistory()}
    </>
)
}

export default SummonerDetail


// Queue IDs:
// 1300 = nb
// 420 = ranked
// 400 = normal
// aram = 450
// flex = 440
// clash = 700
// arena = ? not out yet, comes back on nov 22nd