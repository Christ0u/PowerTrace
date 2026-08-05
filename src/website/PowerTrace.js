const MIN_SAMPLE_PERIOD_MS = 5;
const MAX_SAMPLE_PERIOD_MS = 5000;

const MIN_DURATION_SECONDS = 1;
const MAX_DURATION_SECONDS = 3600;

const startButton = document.getElementById("start-button");
const stopButton = document.getElementById("stop-button");

const samplePeriodInput = document.getElementById("sample-period-input");
const durationSecondsInput = document.getElementById("duration-seconds-input");
const durationFieldContainer = document.getElementById("duration-field-container");
const recordingModeInputs = document.querySelectorAll('input[name="recording_mode"]');

const adcRangeSelect = document.getElementById("adc-range-select");
const vbusctSelect = document.getElementById("vbusct-select");
const vshctSelect = document.getElementById("vshct-select");
const avgSelect = document.getElementById("avg-select");
const currentLsbInput = document.getElementById("current-lsb-input");
const ina228ConfigSummary = document.getElementById("ina228-config-summary");
const ina228ConfigDetail = document.getElementById("ina228-config-detail");

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

    if (data.ina228_config) {
    const cfg = data.ina228_config;

    ina228ConfigSummary.textContent = "Configured";
    ina228ConfigDetail.textContent =
        `adc_range=${cfg.adc_range}, ` +
        `vbusct=${cfg.v_bus_conversion_time}, ` +
        `vshct=${cfg.v_shunt_conversion_time}, ` +
        `avg=${cfg.avg}, ` +
        `current_lsb=${cfg.current_lsb === null ? "auto" : cfg.current_lsb}`;
    }else {
        ina228ConfigSummary.textContent = "Default";
        ina228ConfigDetail.textContent = "No INA228 configuration available.";
    }
}

function getValidatedSelectValue(selectElement, fallbackValue, min, max) {
    const rawValue = parseInt(selectElement.value, 10);

    if (Number.isNaN(rawValue)) {
        selectElement.value = String(fallbackValue);
        return fallbackValue;
    }

    const clampedValue = clampValue(rawValue, min, max, fallbackValue);
    selectElement.value = String(clampedValue);
    return clampedValue;
}

function getValidatedCurrentLsb() {
    const raw = currentLsbInput.value.trim();

    if (raw === "") {
        return null;
    }

    const value = Number(raw);

    if (!Number.isFinite(value) || value <= 0) {
        currentLsbInput.value = "";
        return null;
    }

    return value;
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
        const adcRange = getValidatedSelectValue(adcRangeSelect, 0, 0, 1);
        const vbusct = getValidatedSelectValue(vbusctSelect, 5, 0, 7);
        const vshct = getValidatedSelectValue(vshctSelect, 5, 0, 7);
        const avg = getValidatedSelectValue(avgSelect, 3, 0, 7);
        const currentLsb = getValidatedCurrentLsb();

        const body = new URLSearchParams();
        body.append("sample_period_ms", String(samplePeriodMs));
        body.append("recording_mode", recordingMode);
        body.append("adc_range", String(adcRange));
        body.append("v_bus_conversion_time", String(vbusct));
        body.append("v_shunt_conversion_time", String(vshct));
        body.append("avg", String(avg));

        if (currentLsb !== null) {
            body.append("current_lsb", String(currentLsb));
        }

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