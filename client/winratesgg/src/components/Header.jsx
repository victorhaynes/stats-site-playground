import React from 'react'
import { NavLink, useLocation, useParams } from 'react-router-dom'

const Header = ({displayRegion, handleSummonerNameEntry, handlePlatformSelection, submitAndSearchSummoner}) => {

    const params = useParams()
    const hideSearchBar = useLocation().pathname === '/' ? true : false


    return (
        <>
            <NavLink to="/">Home</NavLink><NavLink to={`/ladder/${displayRegion}`}>Leaderboards</NavLink>
            {/* <NavLink to="/">Tier List</NavLink>  */}
            { hideSearchBar ? null :
            <>
                <div>
                    <form onSubmit={submitAndSearchSummoner}>
                        <label htmlFor='platform'></label>
                            <select onChange={(e) => handlePlatformSelection(e)} name="platform">
                                <option value={null}>Select Region</option>
                                <option value="na1">North America</option>
                                <option value="euw1">Europe West</option>
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
            </> 
            }
            <br/>
            <>------------------</>
            <br></br>
        </>
    )
}

export default Header