import React from 'react'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

const MatchDetails = ({match, renderChampionIcon, navAndSearchParticipant, renderParticipantItemIcons}) => {

    const [showDetails, setShowDetails] = useState(false)
    const params = useParams()

     function displayMatchDetails(){
      setShowDetails((previousState)=>!previousState)
     }

     function renderParticipantsDetail(match){
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