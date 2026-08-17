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