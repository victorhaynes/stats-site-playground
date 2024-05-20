import React from 'react'

const Home = ({handleSummonerNameEntry, handlePlatformSelection, submitAndSearchSummoner, summonerSearchFormData, region, platform}) => {

    return (
       <>
        {
        (localStorage.getItem('platform') && localStorage.getItem('region') && localStorage.getItem('displayRegion')) ?
        <div>
            <h1>WINRATES.GG</h1>
            <form onSubmit={submitAndSearchSummoner}>
                <label htmlFor='platform'></label>
                    <select value={localStorage.getItem('platform')} onChange={(e) => handlePlatformSelection(e)} name="platform">
                        <option value={null}>Select Region</option>
                        <option value="na1">North America</option>
                        <option value="euw1">Europe West</option>
                        <option value="br1">Brazil</option>
                        <option value="eun1">Europe Nordic & East</option>
                        <option value="kr">South Korea</option>
                        <option value="oc1">Oceania</option>
                        <option value="jp1">Japan</option>
                    </select>
                <label htmlFor='gameName'></label>
                    <input onChange={handleSummonerNameEntry} name="gameName"type="text"></input>
                <label htmlFor='tagLine'></label>
                    <input onChange={handleSummonerNameEntry} name="tagLine"type="text"></input>
                <input type="submit" value ="Search"></input>
            </form>
        </div>
        :
        <div>
            <h1>WINRATES.GG</h1>
            <form onSubmit={submitAndSearchSummoner}>
                <label htmlFor='platform'></label>
                    <select onChange={(e) => handlePlatformSelection(e)} name="platform">
                        <option value={null}>Select Region</option>
                        <option value="na1">North America</option>
                        <option value="euw1">Europe West</option>
                        <option value="br1">Brazil</option>
                        <option value="eun1">Europe Nordic & East</option>
                        <option value="kr">South Korea</option>
                        <option value="oc1">Oceania</option>
                        <option value="jp1">Japan</option>
                    </select>
                <label htmlFor='gameName'></label>
                    <input onChange={handleSummonerNameEntry} name="gameName"type="text"></input>
                <label htmlFor='tagLine'></label>
                    <input onChange={handleSummonerNameEntry} name="tagLine"type="text"></input>
                <input type="submit" value ="Search"></input>
            </form>
        </div>
        }
        </>
    )
}

export default Home