const startButton = document.getElementById("start-button");
const stopButton = document.getElementById("stop-button");

const statusText = document.getElementById("status-text");
const recordingText = document.getElementById("recording-text");
const stopRequestedText = document.getElementById("stop-requested-text");
const samplePeriodText = document.getElementById("sample-period-text");
const targetDurationText = document.getElementById("target-duration-text");
const samplesText = document.getElementById("samples-text");
const durationText = document.getElementById("duration-text");
const errorText = document.getElementById("error-text");
const messageText = document.getElementById("message-text");

async function parseJsonResponse(response) {
    return await response.json();
}

function updateStatusView(data) {
    statusText.textContent = data.status;
    recordingText.textContent = data.is_recording ? "Yes" : "No";
    stopRequestedText.textContent = data.stop_requested ? "Yes" : "No";
    samplePeriodText.textContent = String(data.sample_period_ms);
    targetDurationText.textContent = data.target_duration_ms === null
        ? "None"
        : String(data.target_duration_ms);
    samplesText.textContent = String(data.recorded_samples);
    durationText.textContent = String(data.duration_ms);
    errorText.textContent = data.last_error ? data.last_error : "None";

    startButton.disabled = data.is_recording;
    stopButton.disabled = !data.is_recording;
}

async function fetchStatus() {
    try {
        const response = await fetch("/api/acquisition/status");
        const payload = await parseJsonResponse(response);

        if (!response.ok || !payload.success) {
            messageText.textContent = payload.message || "Unable to read acquisition status.";
            return;
        }

        updateStatusView(payload.data);
        messageText.textContent = "Status updated.";
    } catch (error) {
        messageText.textContent = "Communication error while reading status.";
    }
}

async function startRecording() {
    try {
        const response = await fetch("/api/acquisition/start", {
            method: "POST"
        });

        const payload = await parseJsonResponse(response);

        messageText.textContent = payload.message || "Start request sent.";

        if (payload.data) {
            updateStatusView(payload.data);
        } else {
            await fetchStatus();
        }
    } catch (error) {
        messageText.textContent = "Communication error while starting acquisition.";
    }
}

async function stopRecording() {
    try {
        const response = await fetch("/api/acquisition/stop", {
            method: "POST"
        });

        const payload = await parseJsonResponse(response);

        messageText.textContent = payload.message || "Stop request sent.";

        if (payload.data) {
            updateStatusView(payload.data);
        } else {
            await fetchStatus();
        }
    } catch (error) {
        messageText.textContent = "Communication error while stopping acquisition.";
    }
}

startButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

void fetchStatus();
setInterval(()=>{
    void fetchStatus();
},1000)
