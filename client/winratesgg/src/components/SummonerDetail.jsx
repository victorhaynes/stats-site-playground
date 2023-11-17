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

    // function isolateIndividualStats(match){
    //     let individualStats = match?.info?.participants?.filter((player) => player.summonerName == "Enemy Graves")[0]
    //     return individualStats
    // }

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


    function renderMatchHistory(){
        return matchHistory.map((match, index)=>{
            let individualStats = match?.info?.participants?.filter((player) => player.summonerName === "Enemy Graves")[0]
            return (
                // <>
                    <div key={index}>
                        <>Match ID: {match?.metadata?.matchId}<br></br></>
                        <>queueId: {match?.info?.queueId}</>
                        <h3>{individualStats?.championName}</h3>
                        {renderChampionIcon(individualStats)}
                        {renderSummonerSpells(individualStats)}
                        <div>
                            {renderItemIcons(individualStats)}
                        </div>
                        <h3>Role {individualStats?.teamPosition ? individualStats.teamPosition  : "ARAM/NB"}, </h3>
                        <h3>Outcome: {individualStats?.win ? "Victory" : "Defeat"}</h3>
                        <h3>Damage: {individualStats?.totalDamageDealtToChampions}, Damage Taken: {individualStats?.totalDamageTaken}</h3>
                        {match?.info?.participants?.map((participant, index)=>{
                            return (
                                <div key={index}>
                                    <Link to={`/summoners/${params.region}/${params.platform}/I will trade/NA1`} onClick={navAndSearchParticipant}>{participant.summonerName}<br></br></Link>
                                </div>
                            )
                        })}
                        <br></br>
                    </div>
                // </>
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
        <img width="150" height ="150" src={process.env.PUBLIC_URL + `/assets/ranked_icons/Rank${summonerOverview?.tier?.toLowerCase()}.png`} /> 
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