// Data View JavaScript

const fileListContainer = document.getElementById("file-list-container");
const fileListSection = document.getElementById("file-list-section");
const fileDetailSection = document.getElementById("file-detail-section");
const closeDetailButton = document.getElementById("close-detail-button");
const deleteFileButton = document.getElementById("delete-file-button");
const detailFilename = document.getElementById("detail-filename");
const detailStats = document.getElementById("detail-stats");
const dataTableBody = document.getElementById("data-table-body");

let currentFileName = null;  // Track the currently displayed file

// Chart instances
let chartCurrent = null;
let chartVoltage = null;
let chartPower = null;
let chartEnergy = null;
let chartCharge = null;

// Analytical chart instances
let chartCurrentDist = null;
let chartVoltageDist = null;
let chartPowerDist = null;
let chartScatter = null;

/**
 * Format file size in bytes to human-readable format.
 * @param {number} bytes - File size in bytes.
 * @returns {string} Formatted file size.
 */
function formatFileSize(bytes) {
    if (bytes === 0) return "0 B";

    const units = ["B", "KB", "MB", "GB"];
    const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = (bytes / Math.pow(1024, unitIndex)).toFixed(2);

    return `${size} ${units[unitIndex]}`;
}

/**
 * Format number with fixed decimal places.
 * @param {number} value - Number to format.
 * @param {number} decimals - Number of decimal places.
 * @returns {string} Formatted number.
 */
function formatNumber(value, decimals = 6) {
    return value.toFixed(decimals);
}

/**
 * Fetch the list of .bin files from the server.
 */
async function fetchFileList() {
    try {
        const response = await fetch("/api/files/list");
        const payload = await response.json();

        if (!response.ok || !payload.success) {
            throw new Error(payload.message || "Unable to fetch file list");
        }

        renderFileList(payload.data.files, payload.data.directory);
    } catch (error) {
        renderError(error.message);
    }
}

/**
 * Render the file list as clickable buttons.
 * @param {Object[]} files - Array of file objects with name and size.
 * @param {string} directory - Directory path.
 */
function renderFileList(files, directory) {
    if (files.length === 0) {
        fileListContainer.innerHTML = `
            <p class="empty-text">
                No .bin files found in ${directory}
            </p>
        `;
        return;
    }

    const fileListHtml = `
        <div class="file-list">
            ${files.map(file => `
                <button 
                    class="file-button" 
                    type="button"
                    data-filename="${file.name}"
                >
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                </button>
            `).join('')}
        </div>
    `;

    fileListContainer.innerHTML = fileListHtml;

    // Add click event listeners to all file buttons
    const fileButtons = fileListContainer.querySelectorAll(".file-button");
    fileButtons.forEach(button => {
        button.addEventListener("click", () => {
            const fileName = button.getAttribute("data-filename");
            handleFileClick(fileName);
        });
    });
}

/**
 * Handle file button click.
 * @param {string} fileName - Name of the clicked file.
 */
async function handleFileClick(fileName) {
    console.log(`Loading file: ${fileName}`);

    currentFileName = fileName;

    // Show loading state
    fileDetailSection.classList.remove("hidden");
    detailFilename.textContent = fileName;
    detailStats.textContent = "Loading data...";
    dataTableBody.innerHTML = `
        <tr>
            <td colspan="7" class="loading-text">Loading data...</td>
        </tr>
    `;

    // Scroll to detail section
    fileDetailSection.scrollIntoView({ behavior: "smooth", block: "start" });

    try {
        await loadFileData(fileName);
    } catch (error) {
        detailStats.textContent = `Error: ${error.message}`;
        dataTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="error-text">Unable to load file data</td>
            </tr>
        `;
    }
}

/**
 * Load file data from server.
 * @param {string} fileName - Name of the file to load.
 */
async function loadFileData(fileName) {
    const response = await fetch(`/api/files/read?filename=${encodeURIComponent(fileName)}`);
    const payload = await response.json();

    if (!response.ok || !payload.success) {
        throw new Error(payload.message || "Unable to read file");
    }

    renderFileDetail(payload.data);
}

/**
 * Render file detail view.
 * @param {Object} data - File data from server.
 */
function renderFileDetail(data) {
    const { filename, file_size_bytes, record_count, total_records } = data;

    // Update file info
    detailFilename.textContent = filename;
    detailStats.textContent =
        `${record_count} records shown (${total_records} total) | ` +
        `File size: ${formatFileSize(file_size_bytes)}`;

    // Render data table
    if (data.records.length === 0) {
        dataTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-text">No data in file</td>
            </tr>
        `;
        return;
    }

    const tableRows = data.records.map(record => `
        <tr>
            <td>${record.index}</td>
            <td>${record.timestamp_ms}</td>
            <td>${formatNumber(record.bus_voltage_V, 6)}</td>
            <td>${formatNumber(record.current_A, 6)}</td>
            <td>${formatNumber(record.power_W, 6)}</td>
            <td>${formatNumber(record.energy_Wh, 6)}</td>
            <td>${formatNumber(record.charge_mAh, 6)}</td>
        </tr>
    `).join('');

    dataTableBody.innerHTML = tableRows;

    // Render charts
    renderCharts(data.records);
    renderAnalyticalCharts(data.records);
}

/**
 * Render an error message in file list.
 * @param {string} message - Error message to display.
 */
function renderError(message) {
    fileListContainer.innerHTML = `
        <p class="error-text">
            Error: ${message}
        </p>
    `;
}

/**
 * Delete the current file.
 */
async function deleteCurrentFile() {
    if (!currentFileName) {
        alert("No file selected");
        return;
    }

    console.log("Attempting to delete:", currentFileName);

    // Confirmation dialog
    const confirmed = confirm(`Are you sure you want to delete this file?\n\n${currentFileName}\n\nThis action cannot be undone.`);

    if (!confirmed) {
        return;
    }

    try {
        console.log("Sending DELETE request...");

        const response = await fetch(`/api/files/delete?filename=${encodeURIComponent(currentFileName)}`, {
            method: "POST"
        });

        console.log("Response status:", response.status);

        const payload = await response.json();

        console.log("Response payload:", payload);

        if (!response.ok || !payload.success) {
            throw new Error(payload.message || "Unable to delete file");
        }

        alert(`File deleted successfully: ${currentFileName}`);

        // Close detail section
        fileDetailSection.classList.add("hidden");

        // Refresh file list
        await fetchFileList();

        // Scroll to file list
        fileListSection.scrollIntoView({ behavior: "smooth", block: "start" });

    } catch (error) {
        console.error("Delete error:", error);
        alert(`Error deleting file: ${error.message}`);
    }
}

/**
 * Compute histogram data for a given array.
 * @param {number[]} data - Array of values.
 * @param {number} bins - Number of bins.
 * @returns {Object} Histogram data with bins and frequencies.
 */
function computeHistogram(data, bins = 20) {
    if (data.length === 0) {
        return { labels: [], values: [] };
    }

    const min = Math.min(...data);
    const max = Math.max(...data);

    if (min === max) {
        return {
            labels: [min.toFixed(4)],
            values: [100]
        };
    }

    const binWidth = (max - min) / bins;
    const histogram = new Array(bins).fill(0);
    const binLabels = [];

    // Create bin labels
    for (let i = 0; i < bins; i++) {
        const binStart = min + i * binWidth;
        const binEnd = min + (i + 1) * binWidth;
        binLabels.push(`${binStart.toFixed(3)} - ${binEnd.toFixed(3)}`);
    }

    // Count values in each bin
    for (const value of data) {
        const binIndex = Math.min(
            Math.floor((value - min) / binWidth),
            bins - 1
        );
        histogram[binIndex]++;
    }

    // Convert to percentages
    const total = histogram.reduce((a, b) => a + b, 0);
    const percentages = histogram.map(count => (count / total) * 100);

    return {
        labels: binLabels,
        values: percentages
    };
}

/**
 * Render dynamic charts.
 * @param {Object[]} records - Array of measurement records.
 */
function renderCharts(records) {
    // Destroy existing charts
    if (chartCurrent) chartCurrent.destroy();
    if (chartVoltage) chartVoltage.destroy();
    if (chartPower) chartPower.destroy();
    if (chartEnergy) chartEnergy.destroy();
    if (chartCharge) chartCharge.destroy();

    if (records.length === 0) {
        return;
    }

    // Extract data
    const labels = records.map(r => r.timestamp_ms);
    const currentData = records.map(r => r.current_A);
    const voltageData = records.map(r => r.bus_voltage_V);
    const powerData = records.map(r => r.power_W);
    const energyData = records.map(r => r.energy_Wh);
    const chargeData = records.map(r => r.charge_mAh);

    // Common chart options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 0
        },
        interaction: {
            mode: 'index',
            intersect: false
        },
        scales: {
            x: {
                type: 'linear',
                title: {
                    display: true,
                    text: 'Time (ms)'
                }
            }
        }
    };

    // Current chart
    const ctxCurrent = document.getElementById('chart-current').getContext('2d');
    chartCurrent = new Chart(ctxCurrent, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Current (A)',
                data: currentData,
                borderColor: '#2f80ed',
                backgroundColor: 'rgba(47, 128, 237, 0.1)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.1
            }]
        },
        options: commonOptions
    });

    // Voltage chart
    const ctxVoltage = document.getElementById('chart-voltage').getContext('2d');
    chartVoltage = new Chart(ctxVoltage, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Voltage (V)',
                data: voltageData,
                borderColor: '#1f8f4d',
                backgroundColor: 'rgba(31, 143, 77, 0.1)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.1
            }]
        },
        options: commonOptions
    });

    // Power chart
    const ctxPower = document.getElementById('chart-power').getContext('2d');
    chartPower = new Chart(ctxPower, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Power (W)',
                data: powerData,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.1
            }]
        },
        options: commonOptions
    });

    // Energy chart
    const ctxEnergy = document.getElementById('chart-energy').getContext('2d');
    chartEnergy = new Chart(ctxEnergy, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Energy (Wh)',
                data: energyData,
                borderColor: '#7c3aed',
                backgroundColor: 'rgba(124, 58, 237, 0.1)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.1
            }]
        },
        options: commonOptions
    });

    // Charge chart
    const ctxCharge = document.getElementById('chart-charge').getContext('2d');
    chartCharge = new Chart(ctxCharge, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Charge (mAh)',
                data: chargeData,
                borderColor: '#ec4899',
                backgroundColor: 'rgba(236, 72, 153, 0.1)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.1
            }]
        },
        options: commonOptions
    });
}

/**
 * Render analytical charts.
 * @param {Object[]} records - Array of measurement records.
 */
function renderAnalyticalCharts(records) {
    // Destroy existing charts
    if (chartCurrentDist) chartCurrentDist.destroy();
    if (chartVoltageDist) chartVoltageDist.destroy();
    if (chartPowerDist) chartPowerDist.destroy();
    if (chartScatter) chartScatter.destroy();

    if (records.length === 0) {
        return;
    }

    // Extract data
    const currentData = records.map(r => r.current_A);
    const voltageData = records.map(r => r.bus_voltage_V);
    const powerData = records.map(r => r.power_W);

    // Compute histograms
    const currentHist = computeHistogram(currentData, 20);
    const voltageHist = computeHistogram(voltageData, 20);
    const powerHist = computeHistogram(powerData, 20);

    // Common histogram options
    const histogramOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 0
        },
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Frequency (%)'
                }
            }
        }
    };

    // Current distribution chart
    const ctxCurrentDist = document.getElementById('chart-current-dist').getContext('2d');
    chartCurrentDist = new Chart(ctxCurrentDist, {
        type: 'bar',
        data: {
            labels: currentHist.labels,
            datasets: [{
                label: 'Current (A)',
                data: currentHist.values,
                backgroundColor: 'rgba(47, 128, 237, 0.7)',
                borderColor: '#2f80ed',
                borderWidth: 1
            }]
        },
        options: histogramOptions
    });

    // Voltage distribution chart
    const ctxVoltageDist = document.getElementById('chart-voltage-dist').getContext('2d');
    chartVoltageDist = new Chart(ctxVoltageDist, {
        type: 'bar',
        data: {
            labels: voltageHist.labels,
            datasets: [{
                label: 'Voltage (V)',
                data: voltageHist.values,
                backgroundColor: 'rgba(31, 143, 77, 0.7)',
                borderColor: '#1f8f4d',
                borderWidth: 1
            }]
        },
        options: histogramOptions
    });

    // Power distribution chart
    const ctxPowerDist = document.getElementById('chart-power-dist').getContext('2d');
    chartPowerDist = new Chart(ctxPowerDist, {
        type: 'bar',
        data: {
            labels: powerHist.labels,
            datasets: [{
                label: 'Power (W)',
                data: powerHist.values,
                backgroundColor: 'rgba(245, 158, 11, 0.7)',
                borderColor: '#f59e0b',
                borderWidth: 1
            }]
        },
        options: histogramOptions
    });

    // Scatter plot (Voltage vs Current)
    const ctxScatter = document.getElementById('chart-scatter').getContext('2d');
    chartScatter = new Chart(ctxScatter, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'V vs I',
                data: voltageData.map((v, i) => ({ x: v, y: currentData[i] })),
                backgroundColor: 'rgba(124, 58, 237, 0.5)',
                borderColor: '#7c3aed',
                borderWidth: 1,
                pointRadius: 2,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 0
            },
            scales: {
                x: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Voltage (V)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Current (A)'
                    }
                }
            }
        }
    });
}

// Close detail button
closeDetailButton.addEventListener("click", () => {
    fileDetailSection.classList.add("hidden");
    fileListSection.scrollIntoView({ behavior: "smooth", block: "start" });
});

// Delete file button
deleteFileButton.addEventListener("click", () => {
    void deleteCurrentFile();
});

// Initialize on page load
fetchFileList();

console.log("Data View page loaded");