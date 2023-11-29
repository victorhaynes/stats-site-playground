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
                <img width="40" height="40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item0}.png`} /><img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item1}.png`}/><img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item2}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item3}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item4}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item5}.png`} /> <img width= "40" height = "40" alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item6}.png`} /> 
            </>
            )
    }

    function renderParticipantItemIcons(individualStats, width="20", height="20"){
        return (
            <>
                <img width={width} height={height} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item0}.png`} /><img width={width} height={height} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item1}.png`}/><img width={width} height={height} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item2}.png`} /> <img width={width} height={height} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item3}.png`} /> <img width={width} height={height} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item4}.png`} /> <img width={width} height={height} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item5}.png`} /> <img width={width} height={height} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${individualStats?.item6}.png`} /> 
            </>
            )
    }

    function renderChampionIcon(individualStats, width="40", height="40"){
        return <img width={width} height={height} alt="champion icon" src={process.env.PUBLIC_URL + `/assets/champ_icons/champion_img/${individualStats?.championName}.png`} />
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


    function calculateCsGold(individualStats, match){
        let totalCs = individualStats?.neutralMinionsKilled + individualStats?.totalMinionsKilled
        let gameLengthMinutes = match?.info?.gameDuration / 60
        let csPerMin = totalCs / gameLengthMinutes

        return (
            <>
                <plaintext>CS: {totalCs} ({csPerMin.toFixed(1)})</plaintext>
                <plaintext>Gold: {individualStats?.goldEarned} ({individualStats?.challenges?.goldPerMinute.toFixed(1)})</plaintext>
            </>
        )
    }

    function calculateGameTimes(match){
        let gameEndTime = match?.info?.gameEndTimestamp
        let now = Date.now()
        let unixTimeHoursAgo = (now - gameEndTime) / 1000 / 60 / 60
        let daysAgo = 0
        let minutesAgo = 0 
        let hoursAgo = 0

        if(unixTimeHoursAgo < 1){
            minutesAgo = Math.round(unixTimeHoursAgo * 60)
        } else if (unixTimeHoursAgo > 24){
            daysAgo = Math.floor(unixTimeHoursAgo/24)
        } else if (unixTimeHoursAgo >= 1 && unixTimeHoursAgo < 24){
            hoursAgo = Math.round(unixTimeHoursAgo)
            minutesAgo = Math.round((unixTimeHoursAgo % 24) * 60)
        }
        
        let duration = new Date(match?.info?.gameDuration * 1000)
        let durationString = duration.toUTCString()
        let formattedDuration = durationString.slice(-11,-4)
        let individualDurations = formattedDuration.split(":")
        let gameHours = parseInt(individualDurations[0])
        let gameMinutes = parseInt(individualDurations[1])
        let gameSeconds = parseInt(individualDurations[2])

        return (
            <>
                {gameHours ? <plaintext>{gameHours}h {gameMinutes}m {gameSeconds}s</plaintext> : <plaintext>{gameMinutes}m {gameSeconds}s</plaintext>}
                {daysAgo ? <plaintext>{daysAgo} day(s) ago</plaintext> : null}
                {(!daysAgo && hoursAgo) ? <plaintext>{hoursAgo} hour(s) ago</plaintext> : null}
                {(!daysAgo && hoursAgo < 1 && minutesAgo) ? <plaintext>{minutesAgo} minute(s) ago</plaintext> : null}
            </>
        )
    }

    // CHANGE THIS TO PARTICIPANT.RIOTID AND TAGLINE AND CHANGE URL TO THE GAMENAME AND TAGLINE
    function renderParticipants(match){
        let blueSide = match?.info?.participants?.filter((participant) => {
            return parseInt(participant.teamId) === 100
        })
        let redSide = match?.info?.participants?.filter((participant) => {
            return parseInt(participant.teamId) === 200
        })

        return (
            <div>
                <h3>Blue Team:</h3>
                    {blueSide.map((participant, index)=>{
                        return (
                            <div key={index}>
                                {renderChampionIcon(participant, "25", "25")}
                                <Link to={`/summoners/${params.region}/${params.platform}/${participant.riotIdGameName}/${participant.riotIdTagline}`} onClick={navAndSearchParticipant}>{participant.riotIdGameName + " #" + participant.riotIdTagline}<br></br></Link>
                                <>{renderParticipantItemIcons(participant)}</>
                                <plaintext>Damage: {participant?.totalDamageDealtToChampions}</plaintext>
                                <plaintext>Damage Taken: {participant?.totalDamageTaken}</plaintext>
                                <plaintext>Control Wards Placed: {participant?.challenges?.controlWardsPlaced}</plaintext>
                                <plaintext>{participant?.wardsPlaced} / {participant?.wardsKilled}</plaintext>
                            </div>
                        )
                    })}
                <h3>Red Team:</h3>
                    {redSide.map((participant, index)=>{
                        return (
                            <div key={index}>
                                {renderChampionIcon(participant, "25", "25")}
                                <Link to={`/summoners/${params.region}/${params.platform}/${participant.riotIdGameName}/${participant.riotIdTagline}`} onClick={navAndSearchParticipant}>{participant.riotIdGameName + " #" + participant.riotIdTagline}<br></br></Link>
                                <>{renderParticipantItemIcons(participant)}</>
                                <plaintext>Damage: {participant?.totalDamageDealtToChampions}</plaintext>
                                <plaintext>Damage Taken: {participant?.totalDamageTaken}</plaintext>
                                <plaintext>Control Wards Placed: {participant?.challenges?.controlWardsPlaced}</plaintext>
                                <plaintext>{participant?.wardsPlaced} / {participant?.wardsKilled}</plaintext>
                            </div>
                        )
                    })}
            </div>
        )
    }


    function calculateKda(individualStats){
        let kda = individualStats?.challenges?.perfectGame ? "Perfect" : (individualStats?.challenges?.kda).toFixed(1)
        return (
            <plaintext>KDA: ({kda}) {individualStats?.kills}/{individualStats?.deaths}/{individualStats?.assists} ({(individualStats?.challenges?.killParticipation).toFixed(2)*100}%)</plaintext>
        )
    }


    function renderGameModeRole(match, individualStats){
        let gameType = ""
        if (parseInt(match?.info?.queueId) === 420){
            gameType = "Solo Ranked"
        } else if (parseInt(match?.info?.queueId) === 400){
            gameType = "Normal"
        } else if (parseInt(match?.info?.queueId) === 490){
            gameType = "Quick Play"
        } else if (parseInt(match?.info?.queueId) === 450){
            gameType = "ARAM"
        } else if (parseInt(match?.info?.queueId) === 1300){
            gameType = "Nexus Blitz"
        } else if (parseInt(match?.info?.queueId) === 1700){
            gameType = "Arena"
        } else if (parseInt(match?.info?.queueId) === 440){
            gameType = "Flex"
        } else if (parseInt(match?.info?.queueId) === 700){
            gameType = "Clash"
        } else if (parseInt(match?.info?.queueId) === 900){
            gameType = "ARUF"
        } else if (parseInt(match?.info?.queueId) === 1900){
            gameType = "Pick URF"
        } else if (parseInt(match?.info?.queueId) === 1020){
            gameType = "One For All"
        } else if (parseInt(match?.info?.queueId) === 470){
            gameType = "(N) Twisted Treeline"
        } else {
            gameType = "Unknown Game Mode"
        }

        return (
            <>
                {/* <>Match ID: {match?.metadata?.matchId}<br></br></> */}
                {/* <>queueId: {match?.info?.queueId}</> */}
                {/* <>{gameType}</> */}
                <plaintext>{gameType}</plaintext>
                <plaintext>{individualStats?.teamPosition ? <>{individualStats?.teamPosition === "UTILITY" ? "SUPPORT" : individualStats?.teamPosition}</> :null }</plaintext>
            </>
        )
    }

    function renderMatchHistory(){
        return matchHistory.map((match, index)=>{
            let individualStats = match?.info?.participants?.filter((player) => {
                return player.riotIdGameName?.toLowerCase() === (params.gameName).toLowerCase() && player.riotIdTagline?.toLowerCase() === params.tagLine.toLowerCase()
            })[0]
            console.log(individualStats)
            return (
                    <div key={index}>
                        <h1>------------------------------</h1>
                        <h3>{individualStats?.championName} {`[${individualStats?.champLevel}]`}</h3>
                        {renderGameModeRole(match, individualStats)}
                        <plaintext>{renderHighestStreak(individualStats)}</plaintext>
                        {calculateKda(individualStats)}
                        {calculateCsGold(individualStats, match)}
                        {calculateGameTimes(match)}
                        {renderChampionIcon(individualStats)}
                        {renderSummonerSpells(individualStats)}
                        <div>
                            {renderItemIcons(individualStats)}
                        </div>
                        <h3>{individualStats?.win ? "VICTORY" : "DEFEAT"}</h3>
                        <plaintext>Damage: {individualStats?.totalDamageDealtToChampions}</plaintext>
                        <plaintext>Damage Taken: {individualStats?.totalDamageTaken}</plaintext>
                        <plaintext>Vision Score: {individualStats?.visionScore}</plaintext>
                        <plaintext>Control Wards Placed: {individualStats?.challenges?.controlWardsPlaced}</plaintext>
                        <plaintext>{individualStats?.wardsPlaced} / {individualStats?.wardsKilled}</plaintext>
                        {renderParticipants(match)}
                        <br></br>
                    </div>
            )
        })
}


// NEXT: get champ icon/tile, and profile icon

return (
    <>
        <button onClick={()=>fetchMatchHistory()}>All</button><button onClick={()=>fetchMatchHistory("420")}>Ranked Solo/Duo</button><button onClick={()=>fetchMatchHistory("400")}>Normal</button><button onClick={()=>fetchMatchHistory("490")}>Quick Play</button><button onClick={()=>fetchMatchHistory("450")}>ARAM</button><button onClick={()=>fetchMatchHistory("440")}>Flex</button>
        <button onClick={()=>fetchMatchHistory("700")}>Clash</button><button onClick={()=>fetchMatchHistory("1300")}>Nexus Blitz</button><button onClick={()=>fetchMatchHistory("1700")}>Arena</button>
        <h1>{params.gameName} #{params.tagLine}</h1>
        <img width="75" height ="75" alt="profile icon" src={process.env.PUBLIC_URL + `/assets/profile_icons/${summonerOverview?.profileIcon}.png`} /> 
        <h2>Ranked Solo Queue:</h2>
        <img width="100" height ="100" alt="ranked icons" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank${summonerOverview?.tier?.toLowerCase()}.png`} /> 
        <plaintext>{summonerOverview.tier} {summonerOverview.rank}</plaintext>
        <plaintext>Wins: {summonerOverview.wins} Losses:{summonerOverview.losses}</plaintext>
        <plaintext>Win Rate {Math.round(summonerOverview.wins/(summonerOverview.wins + summonerOverview.losses)*100)}%</plaintext>
        {renderMatchHistory()}
    </>
)
}

export default SummonerDetail

