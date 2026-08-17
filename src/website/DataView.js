// Data View JavaScript

const fileListContainer = document.getElementById("file-list-container");

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
function handleFileClick(fileName) {
    alert(`Selected file: ${fileName}`);
    // TODO: Implement actual file viewing functionality
}

/**
 * Render an error message.
 * @param {string} message - Error message to display.
 */
function renderError(message) {
    fileListContainer.innerHTML = `
        <p class="error-text">
            Error: ${message}
        </p>
    `;
}

// Initialize on page load
fetchFileList();

console.log("Data View page loaded");