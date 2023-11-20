import React from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useEffect, useState } from 'react'

const SummonerDetail = () => {


    const params = useParams()
    const [summonerOverview, setSummonerOverview] = useState({})
    const [matchHistory, setMatchHistory] = useState([])
    const location = useLocation()

    useEffect(() => {
        fetchSummonerOveview()
        fetchMatchHistory()
    },[location.pathname])


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

    function navAndSearchParticipant(gName = "I will trade", tLine ="NA1"){
        // may not be the best pattern
        // additionally, in the "Link" make sure that we are passing in gameName and tagLine from the individual participant once riot populates
        setSummonerOverview({})
        setMatchHistory([])
    } 

    function renderItemIcons(individualStats){
        return (
            <>
                <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item0}.png`} /><img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item1}.png`}/><img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item2}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item3}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item4}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item5}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item6}.png`} /> 
            </>
            )
    }

    function renderChampionIcon(individualStats){
        return <img width= "40" height = "40" alt="champion icon" src={process.env.PUBLIC_URL + `/assets/champ_icons/champion_img/${individualStats?.championName}.png`} />
    }

    function renderSummonerSpells(individualStats){
        return (
            <>
                <img width= "30" height = "30" alt="summoner spell icon" src={process.env.PUBLIC_URL + `/assets/summoner_spell_icons/${individualStats?.summoner1Id}.png`} /><img width= "30" height = "30" alt="summoner spell icon" src={process.env.PUBLIC_URL + `/assets/summoner_spell_icons/${individualStats?.summoner2Id}.png`} />
            </>
            )
    }

    function renderHighestStreak(individualStats){
        if(individualStats?.pentaKills){
            return "PENTA KILL"
        } else if (individualStats?.quadraKills){
            return "QUADRA KILL"
        } else if (individualStats?.tripleKills){
            return "TRIPLE KILL"
        } else if (individualStats?.doubleKills){
            return "DOUBLE KILL"
        } else {
            return null
        }
    }


    function calculateCs(individualStats, match){
        let totalCs = individualStats?.neutralMinionsKilled + individualStats?.totalMinionsKilled
        let gameLengthMinutes = match?.info?.gameDuration / 60
        let csPerMin = totalCs / gameLengthMinutes

        return (<plaintext>CS: {totalCs} ({csPerMin.toFixed(1)})</plaintext>)

    }

    // CHANGE THIS TO PARTICIPANT.RIOTID AND TAGLINE AND CHANGE URL TO THE GAMENAME AND TAGLINE
    function renderParticipants(match){
        let blueSide = match?.info?.participants?.filter((participant) => {
            return parseInt(participant.teamId) === 100
        })
        let redSide = match?.info.participants?.filter((participant) => {
            return parseInt(participant.teamId) === 200
        })

        return (
            <div>
                <h4>Blue Team:</h4>
                    {blueSide.map((participant, index)=>{
                        return (
                            <div key={index}>
                                <Link to={`/summoners/${params.region}/${params.platform}/I will trade/NA1`} onClick={navAndSearchParticipant}>{participant.summonerName}<br></br></Link>
                            </div>
                        )
                    })}
                <h4>Red Team:</h4>
                    {redSide.map((participant, index)=>{
                        return (
                            <div key={index}>
                                <Link to={`/summoners/${params.region}/${params.platform}/I will trade/NA1`} onClick={navAndSearchParticipant}>{participant.summonerName}<br></br></Link>
                            </div>
                        )
                    })}
            </div>
        )

    }

    function renderGameModeRole(match, individualStats){
        let gameType = ""
        if (parseInt(match?.info?.queueId) === 420){
            gameType = "Solo Ranked"
        } else if (parseInt(match?.info?.queueId) === 400){
            gameType = "Normal"
        } else if (parseInt(match?.info?.queueId) === 450){
            gameType = "ARAM"
        } else if (parseInt(match?.info?.queueId) === 440){
            gameType = "Flex"
        } else if (parseInt(match?.info?.queueId) === 700){
            gameType = "Clash"
        } else if (parseInt(match?.info?.queueId) === 1300){
            gameType = "Nexus Blitz"
        } else {
            gameType = "GAME TYPE NOT FOUND"
        }
        
        return (
            <>
                {/* <>Match ID: {match?.metadata?.matchId}<br></br></> */}
                {/* <>queueId: {match?.info?.queueId}</> */}
                {/* <>{gameType}</> */}
                <plaintext>{gameType}</plaintext>
                <plaintext>{individualStats?.teamPosition ? <>{individualStats?.teamPosition}</> :null }</plaintext>
            </>
        )
    }

    function renderMatchHistory(){
        return matchHistory.map((match, index)=>{
            // CHANGE THIS TO PLAYER.RIOTID AND TAGLINE TO === PARAMS.RIOT ID AND TAGLINE WHEN RIOT API IS FIXED
            let individualStats = match?.info?.participants?.filter((player) => player.summonerName === "Enemy Graves")[0]
            return (
                    <div key={index}>
                        <h3>{individualStats?.championName}</h3>
                        {renderGameModeRole(match, individualStats)}
                        <plaintext>{renderHighestStreak(individualStats)}</plaintext>
                        {calculateCs(individualStats, match)}
                        {renderChampionIcon(individualStats)}
                        {renderSummonerSpells(individualStats)}
                        <div>
                            {renderItemIcons(individualStats)}
                        </div>
                        <h3>{individualStats?.win ? "VICTORY" : "DEFEAT"}</h3>
                        <h3>Damage: {individualStats?.totalDamageDealtToChampions}, Damage Taken: {individualStats?.totalDamageTaken}</h3>
                        {renderParticipants(match)}
                        <br></br>
                    </div>
            )
        })
}


// NEXT: get champ icon/tile, and profile icon

return (
    <>
        <button onClick={fetchMatchHistory}>All</button><button onClick={()=>fetchMatchHistory("420")}>Ranked Solo/Duo</button><button onClick={()=>fetchMatchHistory("400")}>Normal</button><button onClick={()=>fetchMatchHistory("450")}>ARAM</button><button onClick={()=>fetchMatchHistory("440")}>Flex</button>
        <button onClick={()=>fetchMatchHistory("700")}>Clash</button><button onClick={()=>fetchMatchHistory("1300")}>Nexus Blitz</button>
        <h1>{params.gameName} #{params.tagLine}</h1>
        <h2>Ranked Solo Queue:</h2>
        <img width="150" height ="150" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank${summonerOverview?.tier?.toLowerCase()}.png`} /> 
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
// custom ?