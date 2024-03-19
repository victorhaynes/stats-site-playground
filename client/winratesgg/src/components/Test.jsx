import {React, useState, useEffect} from 'react'
import axios from 'axios'

const Test = () => {

    const [items, setItems] = useState([])

    useEffect(()=> {showItems()}, [])

    async function showItems(){
        try {
            let response = await axios.get(`http://localhost:8000/get-timeline/`)
            console.log(response.data)
            setItems(response.data)
        } catch (error) {
            console.log({[error.response.request.status]: error.response.data})
        }
    }

    return (
        <>
            {items.map( (item) => <img key={item?.itemId + "_" + item?.timestamp} alt="item icon" src={process.env.PUBLIC_URL + `/assets/item_icons/${item?.itemId}.png`} />)}
        </>
    )
}

export default Test