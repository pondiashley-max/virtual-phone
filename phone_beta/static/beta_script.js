console.log("beta phone active");

let localStream = null;

function pollStatus() {
    fetch('/api/status/')
        .then(response => response.json())
        .then(data => {
            const statusSpan = document.getElementById('call-status');
            const callActionsContainer = document.getElementById('call-actions');
            if (statusSpan && data.call) {
                statusSpan.textContent = data.call.status;

                if (callActionsContainer) {
                    let htmlContent = '';
                    if (data.call.status === 'ringing') {
                        if (data.call.caller === 'beta') {
                            htmlContent = '<form method="post"><input type="hidden" name="csrfmiddlewaretoken" value="' + getCsrfToken() + '"><button type="submit" name="action" value="end_call">cancel call</button></form>';
                        } else {
                            htmlContent = '<p>incoming call from alpha phone...</p><form method="post"><input type="hidden" name="csrfmiddlewaretoken" value="' + getCsrfToken() + '"><button type="submit" name="action" value="answer_call">answer call</button><button type="submit" name="action" value="end_call">reject call</button></form>';
                        }
                    } else if (data.call.status === 'active') {
                        htmlContent = '<p>call in progress over internet...</p><form method="post"><input type="hidden" name="csrfmiddlewaretoken" value="' + getCsrfToken() + '"><button type="submit" name="action" value="end_call">end call</button></form>';
                        if (!localStream) {
                            startAudioStream();
                        }
                    } else {
                        htmlContent = '<form method="post"><input type="hidden" name="csrfmiddlewaretoken" value="' + getCsrfToken() + '"><button type="submit" name="action" value="start_call">start voice / video call</button></form>';
                        if (localStream) {
                            stopAudioStream();
                        }
                    }
                    callActionsContainer.innerHTML = htmlContent;
                }
            }
        })
        .catch(error => console.error("polling error:", error));
}

function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const parts = cookie.trim().split('=');
        if (parts[0] === 'csrftoken') {
            return parts[1];
        }
    }
    return '';
}

function startAudioStream() {
    navigator.mediaDevices.getUserMedia({ audio: true, video: true })
        .then(stream => {
            localStream = stream;
            const videoElement = document.getElementById('local-video');
            if (videoElement) {
                videoElement.srcObject = stream;
            }
            console.log("internet audio/video call stream connected");
        })
        .catch(err => console.log("media stream permission denied or unavailable:", err));
}

function stopAudioStream() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
        console.log("call stream stopped");
    }
}

setInterval(pollStatus, 1000);
