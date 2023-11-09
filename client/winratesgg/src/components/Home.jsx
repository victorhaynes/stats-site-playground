import React, {useState} from 'react'
import { useNavigate } from 'react-router-dom'

const Home = ({handleSummonerSearchChange, summonerSearchFormData,setSummonerSearchFormData}) => {

    const navigate = useNavigate()

    function submitAndSearchSummoner(event){
        let re = ""
        if ({...summonerSearchFormData}.platform === "na1" || {...summonerSearchFormData}.platform === "oc1"){
          re = "americas"
        } else if ({...summonerSearchFormData}.platform === "kr" || {...summonerSearchFormData}.platform === "jp1"){
          re = "asia"
        // } else if ({...summonerSearchFormData}.platform == "sea" || {...summonerSearchFormData}.platform == "sea"){
        //   re = "sea"
        // }
        } else if ({...summonerSearchFormData}.platform === "euw1" || {...summonerSearchFormData}.platform === "eun1"){
          re = "europe"
        } else {
          re = ""
        }
        setSummonerSearchFormData({...summonerSearchFormData, region:re})
        event.preventDefault()
        navigate(`/summoners/${summonerSearchFormData.platform}/${summonerSearchFormData.gameName}/${summonerSearchFormData.tagLine}`)
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