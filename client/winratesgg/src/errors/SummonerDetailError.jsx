import React from 'react'
import { useParams } from 'react-router-dom';

const SummonerDetailError = ({error}) => {
    const params = useParams()

    const displayName = params.displayNameZipped
    const [gameName, tagLine] = displayName.split("-")

    const errorCode = String(error?.status_code);
    let errorDetails = null;

    if (errorCode === "404") {
        errorDetails = (
            <div>Summoner "{gameName} #{tagLine}" does not exist in Riot databases.</div>
            //{/* <div>{error?.status?.message}</div> */}
        )
    } else if (errorCode[0] === "5") {
        console.log(error)
        errorDetails = (
            <div>There was an issue seaching for your summoner. Please try again later.</div>
        )
    } else if (errorCode === "408") {
        errorDetails = (
            <div>Your request timed out (took unexpectedly long). Please try again momentarily.</div>
        )
    } else {
        errorDetails = (
            <div>Unexpected error. Please try again later.</div>
        )
    }

    return (
        <>
            {errorDetails}
        </>
        
    )
}


export default SummonerDetailError