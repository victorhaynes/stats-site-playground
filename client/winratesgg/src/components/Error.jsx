import React from 'react'

const Error = ({error}) => {

    const errorCode = String(error?.status_code);
    let errorDetails = null;

    if (errorCode[0] === "4") {
        errorDetails = (
            <div>
                <div>There was an error please try again.</div>
                <div>Code: {error?.status_code}</div>
                <div>Message: {error?.status?.message}</div>
            </div>
        );
    } else if (errorCode[0] === "5") {
        console.log(error)
        errorDetails = (
            <div>
                <div>Server error</div>
            </div>
        );
    }

    return (
        errorDetails
    )
}

export default Error