import React, {useState} from 'react'
import { useNavigate } from 'react-router-dom'

const Home = ({handleSummonerSearchChange, summonerSearchFormData,region}) => {

    const navigate = useNavigate()

    function submitAndSearchSummoner(event){
        event.preventDefault()
        navigate(`/summoners/${region}/${summonerSearchFormData.platform}/${summonerSearchFormData.gameName}/${summonerSearchFormData.tagLine}`)
    }


    return (
        <div>
            <h1>WINRATES.GG</h1>
            <form onSubmit={submitAndSearchSummoner}>
            <label htmlFor='platform'></label>
                <select onChange={handleSummonerSearchChange} name="platform">
                <option value={null}>Select Region</option>
                <option value="na1">North America</option>
                <option value="euw1">Europe West</option>
                <option value="eun1">Europe Nordic & East</option>
                <option value="kr">South Korea</option>
                <option value="oc1">Oceania</option>
                <option value="jp1">Japan</option>
                </select>
            <label htmlFor='gameName'></label>
            <input onChange={handleSummonerSearchChange} name="gameName"type="text"></input>
            <label htmlFor='tagLine'></label>
            <input onChange={handleSummonerSearchChange} name="tagLine"type="text"></input>
            <input type="submit" value ="Search"></input>
            </form>
        </div>
    )
}

export default Home