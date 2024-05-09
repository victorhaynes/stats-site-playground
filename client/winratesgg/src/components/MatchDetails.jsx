import React from 'react'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

const MatchDetails = ({matchRecord, renderChampionIcon, navAndSearchParticipant, renderParticipantItemIcons, calculateKda}) => {
// # rename to match record
    const [showDetails, setShowDetails] = useState(false)
    const params = useParams()
    const match = matchRecord?.metadata

    function displayMatchDetails(){
      setShowDetails((previousState)=>!previousState)
    }


    function calculateParticipantCsAndGold(individualStats, match){
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

    function renderParticipantsDetail(match){
        let blueSide = []
        let redSide = []
        let arenaTeams = []

        if (match?.info?.queueId !== 1700){
            blueSide = match?.info?.participants?.filter((participant) => {
                return parseInt(participant.teamId) === 100
            })
            redSide = match?.info?.participants?.filter((participant) => {
                return parseInt(participant.teamId) === 200
            })
        } else if (match?.info?.queueId === 1700){
            arenaTeams = match?.info?.participants
            arenaTeams.sort((a, b) => a.placement - b.placement);
        }

        // Non-Arena Format, assumed 5v5 Game Mode
        if (match?.info?.queueId !== 1700){
            return (
                <div>
                    <h3>Blue Team:</h3>
                        {blueSide.map((participant, index)=>{
                            return (
                                <div key={index}>
                                    {renderChampionIcon(participant, "25", "25")}
                                    <Link to={`/summoners/${params.region}/${params.platform}/${participant.riotIdGameName}/${participant.riotIdTagline}`} onClick={navAndSearchParticipant}>{participant.riotIdGameName + " #" + participant.riotIdTagline}<br></br></Link>
                                    <>{renderParticipantItemIcons(participant)}</>
                                    {calculateKda(participant)}
                                    {calculateParticipantCsAndGold(participant, match)}
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
                                    {calculateKda(participant)}
                                    {calculateParticipantCsAndGold(participant, match)}
                                    <plaintext>Damage: {participant?.totalDamageDealtToChampions}</plaintext>
                                    <plaintext>Damage Taken: {participant?.totalDamageTaken}</plaintext>
                                    <plaintext>Control Wards Placed: {participant?.challenges?.controlWardsPlaced}</plaintext>
                                    <plaintext>{participant?.wardsPlaced} / {participant?.wardsKilled}</plaintext>
                                </div>
                            )
                        })}
                </div>
            )
        /// If Game Mode is Arena return different HTML
        } else if (match?.info?.queueId === 1700) {
            return (
                <div>
                    <h3>Arena Teams:</h3> 
                        {arenaTeams.map((participant, index)=>{
                            return (
                                <div key={index}>
                                    <plaintext>{participant?.placement}</plaintext>
                                    {renderChampionIcon(participant, "25", "25")}
                                    <Link to={`/summoners/${params.region}/${params.platform}/${participant.riotIdGameName}/${participant.riotIdTagline}`} onClick={navAndSearchParticipant}>{participant.riotIdGameName + " #" + participant.riotIdTagline}<br></br></Link>
                                    <>{renderParticipantItemIcons(participant)}</>
                                    {calculateKda(participant)}
                                    {calculateParticipantCsAndGold(participant, match)}
                                    <plaintext>Damage: {participant?.totalDamageDealtToChampions}</plaintext>
                                    <plaintext>Damage Taken: {participant?.totalDamageTaken}</plaintext>
                                    <plaintext>Control Wards Placed: {participant?.challenges?.controlWardsPlaced}</plaintext>
                                    <plaintext>{participant?.wardsPlaced} / {participant?.wardsKilled}</plaintext>
                                </div>
                            )
                        })}
                </div>
            )
        } else {
            return <></>
        }

    }

  return (
    <>
        {showDetails ? 
            <> 
                {renderParticipantsDetail(match)}
                <button onClick={displayMatchDetails}>Hide Details</button>
            </>
            : 
            <div>
                <button onClick={displayMatchDetails}>Show Details</button>
            </div>}
    </>
  )
}

export default MatchDetails