// function sendThumbClick(buttonNumber) {
//     const buttons = document.querySelectorAll('button');
//     // buttons.querySelectorAll('.thumb-up-button').forEach(button => {
//     //     button.disabled = true;
//     // });
//     // send a GET request to the server
//     window.location.href = `/thumb_click?button_number=${buttonNumber}`;
// }

function sendThumbClick(buttonNumber) {
    fetch('/thumb_click', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            intVariable: buttonNumber
        }),
    })
    .then(() => {
        // If you don't care about the response, you don't need to do anything here
    })
    .catch((error) => console.error('Error:', error));
}