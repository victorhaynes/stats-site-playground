import React from 'react'
import { NavLink, useLocation, useParams } from 'react-router-dom'

const Header = ({displayRegion, handleSummonerNameEntry, handlePlatformSelection, submitAndSearchSummoner}) => {

    const params = useParams()
    const hideSearchBar = useLocation().pathname === '/' ? true : false

    // let regionUrl = params.displayRegion? params.displayRegion : 'na'

    return (
        <>
            <img alt="logo" src={process.env.PUBLIC_URL + `/logo.svg`}/>
            <NavLink to="/">Home</NavLink> <NavLink to={`/ladder/${displayRegion}/1`}>Leaderboards</NavLink>
            {/* <NavLink to="/">Home</NavLink><NavLink to={`/ladder/${regionUrl}/1`}>Leaderboards</NavLink> */}
            {/* <NavLink to="/">Tier List</NavLink>  */}
            { hideSearchBar ? null :
            // <>
            //     <div>
            //         <form onSubmit={submitAndSearchSummoner}>
            //             <label htmlFor='platform'></label>
            //                 <select onChange={(e) => handlePlatformSelection(e)} name="platform">
            //                     <option value={null}>Select Region</option>
            //                     <option value="na1">North America</option>
            //                     <option value="euw1">Europe West</option>
            //                     <option value="eun1">Europe Nordic & East</option>
            //                     <option value="kr">South Korea</option>
            //                     <option value="oc1">Oceania</option>
            //                     <option value="jp1">Japan</option>
            //                 </select>
            //             <label htmlFor='gameName'></label>
            //                 <input onChange={handleSummonerNameEntry} name="gameName"type="text"></input>
            //             <label htmlFor='tagLine'></label>
            //                 <input onChange={handleSummonerNameEntry} name="tagLine"type="text"></input>
            //             <input type="submit" value ="Search"></input>
            //         </form>
            //     </div>
            // </> 
            <>
            {
            (localStorage.getItem('platform') && localStorage.getItem('region') && localStorage.getItem('displayRegion')) ?
            <div>
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
            }
            <br/>
            <>---------------------------------------------------------</>
            <br></br>
        </>
    )
}

export default Header