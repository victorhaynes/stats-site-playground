import React from 'react'

const LadderError = ({error}) => {


    const errorCode = String(error?.status_code);
    let errorDetails = null;

    if (errorCode === "404") {
        errorDetails = (
            <div>Could not find high elo leaderboards in Riot servers.</div>
            //{/* <div>{error?.status?.message}</div> */}
        )
    } else if (errorCode[0] === "5") {
        console.log(error)
        errorDetails = (
            <div>There was an issue retriving for the leaderboards. Please try again later.</div>
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


export default LadderError