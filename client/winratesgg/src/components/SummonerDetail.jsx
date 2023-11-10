import React from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { useEffect } from 'react'

const SummonerDetail = () => {

    const params = useParams()

    useEffect(() => {
        getSummonerPuuid()
    },[])

    // FROM HERE: SETUP DJANGO API BACKEND, SO THE API CAN DO THIS FETCH REQUEST, THEN I CAN QUERY AND CHAIN THE RESULTS
    // ON THE CLIENT SIDE USING AXIOS
    
    async function getSummonerPuuid(){
        try {
            let response = await axios.get(`https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/${params.summoner}`)
            console.log("yay i waited")
        } catch (error) {
            console.log(error)
        }
    }

    return (
        <>
            <div>SummonerDetail</div>
            <h3>Region: {params.platform}</h3>
            <h3>Summoner: {params.gameName}</h3>
            <h3>tagLine: {params.tagLine}</h3>
        </>
    )
}

export default SummonerDetail