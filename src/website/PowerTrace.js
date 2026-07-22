const MIN_SAMPLE_PERIOD_MS = 10;
const MAX_SAMPLE_PERIOD_MS = 5000;

const MIN_DURATION_SECONDS = 1;
const MAX_DURATION_SECONDS = 3600;

const startButton = document.getElementById("start-button");
const stopButton = document.getElementById("stop-button");

const samplePeriodInput = document.getElementById("sample-period-input");
const durationSecondsInput = document.getElementById("duration-seconds-input");
const durationFieldContainer = document.getElementById("duration-field-container");
const recordingModeInputs = document.querySelectorAll('input[name="recording_mode"]');

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

function clampValue(value, min, max, fallbackValue) {
    if (Number.isNaN(value)) {
        return fallbackValue;
    }

    if (value < min) {
        return min;
    }

    if (value > max) {
        return max;
    }

    return value;
}

function getSelectedRecordingMode() {
    for (const input of recordingModeInputs) {
        if (input.checked) {
            return input.value;
        }
    }

    return "manual";
}

function updateRecordingModeView() {
    const mode = getSelectedRecordingMode();
    const isTimed = mode === "timed";

    durationFieldContainer.classList.toggle("hidden", !isTimed);
    durationSecondsInput.disabled = !isTimed;
}

function getValidatedSamplePeriod() {
    const rawValue = parseInt(samplePeriodInput.value, 10);
    const clampedValue = clampValue(
        rawValue,
        MIN_SAMPLE_PERIOD_MS,
        MAX_SAMPLE_PERIOD_MS,
        50
    );

    samplePeriodInput.value = String(clampedValue);
    return clampedValue;
}

function getValidatedDurationSeconds() {
    const rawValue = parseInt(durationSecondsInput.value, 10);
    const clampedValue = clampValue(
        rawValue,
        MIN_DURATION_SECONDS,
        MAX_DURATION_SECONDS,
        30
    );

    durationSecondsInput.value = String(clampedValue);
    return clampedValue;
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

    samplePeriodInput.disabled = data.is_recording;

    for (const input of recordingModeInputs) {
        input.disabled = data.is_recording;
    }

    durationSecondsInput.disabled = data.is_recording || getSelectedRecordingMode() !== "timed";
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
        const samplePeriodMs = getValidatedSamplePeriod();
        const recordingMode = getSelectedRecordingMode();

        const body = new URLSearchParams();
        body.append("sample_period_ms", String(samplePeriodMs));
        body.append("recording_mode", recordingMode);

        if (recordingMode === "timed") {
            const durationSeconds = getValidatedDurationSeconds();
            body.append("duration_seconds", String(durationSeconds));
        }

        const response = await fetch("/api/acquisition/start", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: body.toString()
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

samplePeriodInput.addEventListener("change", () => {
    getValidatedSamplePeriod();
});

durationSecondsInput.addEventListener("change", () => {
    getValidatedDurationSeconds();
});

for (const input of recordingModeInputs) {
    input.addEventListener("change", updateRecordingModeView);
}

startButton.addEventListener("click", () => {
    void startRecording();
});

stopButton.addEventListener("click", () => {
    void stopRecording();
});

updateRecordingModeView();
void fetchStatus();

setInterval(() => {
    void fetchStatus();
}, 1000);