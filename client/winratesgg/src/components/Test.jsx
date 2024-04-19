import {React, useState, useEffect} from 'react'
import axios from 'axios'

const Test = () => {

    const [itemPaths, setItemPaths] = useState([])

    useEffect(()=> {showItems()}, [])

    async function showItems(){
        try {
            let response = await axios.get(`http://localhost:8000/get-timeline/`)
            console.log(response.data)
            setItemPaths(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    return (
        // <>
        //     {itemPaths.map( (path) => { path?.build.map( (build) => {
        //         return <img key={build?.itemId + "_" + build?.timestamp} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${build?.itemId}.png`} />
        //     })
        //     })}
        // </>

        // <>
        //     {itemPaths.map((path) => {
        //         return <div>path?.build.map((build) => {
        //             return <img key={build?.itemId + "_" + build?.timestamp} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${build?.itemId}.png`} />;
        //         })</div>;
        //     })}
        // </>

        <>
        {itemPaths.map((path) => (
            <div key={path?.puuid}>
                <h3>{path?.puuid}</h3>
                {path?.build.map((build) => (
                    <img key={build?.itemId + "_" + build?.timestamp} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${build?.itemId}.png`} />
                ))}
            </div>
        ))}
        </>
    )
}

export default Test

                // return <img key={item?.itemId + "_" + item?.timestamp} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${item?.itemId}.png`} />
