import React from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { useEffect } from 'react'

const SummonerDetail = () => {

    const params = useParams()


    useEffect(() => {
        fetchSummonerOveview()
    },[])

    // FROM HERE: SETUP DJANGO API BACKEND, SO THE API CAN DO THIS FETCH REQUEST, THEN I CAN QUERY AND CHAIN THE RESULTS
    // ON THE CLIENT SIDE USING AXIOS
    
    function fetchSummonerOveview(){
        axios.get(`http://127.0.0.1:8000/summoner-overview/?region=${params.region}&platform=${params.platform}&gameName=${params.gameName}&tagLine=${params.tagLine}`)
        .then((res)=>{
            console.log(res.data)
        })
        .catch((error)=>{
            console.log(error)
        })

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