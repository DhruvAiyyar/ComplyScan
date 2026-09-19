const API_BASE_URL = "http://127.0.0.1:8000";

let violationsChart = null;
let complianceChart = null;


// ================================
// ELEMENTS
// ================================

const totalScansElement =
    document.getElementById("totalScans");

const compliantScansElement =
    document.getElementById("compliantScans");

const nonCompliantScansElement =
    document.getElementById("nonCompliantScans");

const scanList =
    document.getElementById("scanList");

const dashboardError =
    document.getElementById("dashboardError");

const refreshButton =
    document.getElementById("refreshButton");


// ================================
// SHOW ERROR
// ================================

function showError(message) {

    dashboardError.textContent = message;

    dashboardError.style.display = "block";
}


// ================================
// HIDE ERROR
// ================================

function hideError() {

    dashboardError.style.display = "none";
}


// ================================
// FETCH DASHBOARD DATA
// ================================

async function loadDashboard() {

    hideError();

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/dashboard`
        );

        if (!response.ok) {
            throw new Error("Dashboard API request failed.");
        }

        const data = await response.json();

        updateStats(data);

        updateViolationChart(
            data.violation_breakdown || {}
        );

        updateComplianceChart(
            data.compliant || 0,
            data.non_compliant || 0
        );

    } catch (error) {

        console.error(error);

        showError(
            "Dashboard data could not be loaded. Make sure the backend is running."
        );

        updateStats({
            total_scans: 0,
            compliant: 0,
            non_compliant: 0
        });

        updateViolationChart({});

        updateComplianceChart(0, 0);
    }
}


// ================================
// UPDATE STAT CARDS
// ================================

function updateStats(data) {

    totalScansElement.textContent =
        data.total_scans ?? 0;

    compliantScansElement.textContent =
        data.compliant ?? 0;

    nonCompliantScansElement.textContent =
        data.non_compliant ?? 0;
}


// ================================
// VIOLATION BAR CHART
// ================================

function updateViolationChart(violations) {

    const canvas =
        document.getElementById("violationsChart");

    if (violationsChart) {
        violationsChart.destroy();
    }

    const labels = Object.keys(violations);

    const values = Object.values(violations);

    violationsChart = new Chart(canvas, {

        type: "bar",

        data: {
            labels: labels.length
                ? labels
                : ["No violations yet"],

            datasets: [
                {
                    label: "Violations",

                    data: values.length
                        ? values
                        : [0],

                    borderWidth: 0,

                    borderRadius: 8
                }
            ]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                }
            },

            scales: {

                y: {
                    beginAtZero: true,

                    ticks: {
                        precision: 0
                    }
                },

                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}


// ================================
// COMPLIANCE PIE CHART
// ================================

function updateComplianceChart(
    compliant,
    nonCompliant
) {

    const canvas =
        document.getElementById("complianceChart");

    if (complianceChart) {
        complianceChart.destroy();
    }

    complianceChart = new Chart(canvas, {

        type: "doughnut",

        data: {

            labels: [
                "Compliant",
                "Non-Compliant"
            ],

            datasets: [
                {
                    data: [
                        compliant,
                        nonCompliant
                    ],

                    borderWidth: 0
                }
            ]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: "68%",

            plugins: {

                legend: {
                    position: "bottom"
                }
            }
        }
    });
}


// ================================
// FETCH PAST SCANS
// ================================

async function loadScans() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/scans`
        );

        if (!response.ok) {
            throw new Error("Scans API request failed.");
        }

        const data = await response.json();

        renderScans(data);

    } catch (error) {

        console.error(error);

        scanList.innerHTML = `
            <div class="empty-state">
                <strong>No scan history available</strong>
                <span>
                    Scan history will appear here once the backend
                    provides previous scans.
                </span>
            </div>
        `;
    }
}


// ================================
// RENDER SCANS
// ================================

function renderScans(data) {

    let scans = data;

    // Some APIs return { scans: [...] }
    if (data && Array.isArray(data.scans)) {
        scans = data.scans;
    }

    if (!Array.isArray(scans) || scans.length === 0) {

        scanList.innerHTML = `
            <div class="empty-state">
                <strong>No scans yet</strong>
                <span>
                    Your previous compliance scans will appear here.
                </span>
            </div>
        `;

        return;
    }

    scanList.innerHTML = "";

    scans.slice(0, 10).forEach(scan => {

        const scanId =
            scan.id ??
            scan.scan_id ??
            "";

        const status =
            scan.overall_status ??
            scan.status ??
            "unknown";

        const isCompliant =
            String(status).toLowerCase().includes("compliant") &&
            !String(status).toLowerCase().includes("non");

        const dateValue =
            scan.created_at ??
            scan.scan_time ??
            scan.detection_time ??
            scan.timestamp ??
            "";

        const formattedDate =
            formatDate(dateValue);

        const item =
            document.createElement("a");

        item.className = "scan-item";

        item.href =
            `report.html?id=${encodeURIComponent(scanId)}`;

        const statusClass =
            isCompliant ? "pass" : "fail";

        const displayStatus =
            isCompliant
                ? "Compliant"
                : "Non-Compliant";

        item.innerHTML = `

            <div class="scan-info">

                <div class="scan-title">
                    Scan #${escapeHTML(String(scanId || "—"))}
                </div>

                <div class="scan-date">
                    ${escapeHTML(formattedDate)}
                </div>

            </div>

            <span class="status-badge ${statusClass}">
                ${displayStatus}
            </span>

        `;

        scanList.appendChild(item);
    });
}


// ================================
// FORMAT DATE
// ================================

function formatDate(value) {

    if (!value) {
        return "Date unavailable";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString();
}


// ================================
// ESCAPE HTML
// ================================

function escapeHTML(value) {

    return value
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ================================
// REFRESH BUTTON
// ================================

refreshButton.addEventListener(
    "click",
    async () => {

        refreshButton.textContent =
            "↻ Loading...";

        refreshButton.disabled = true;

        await Promise.all([
            loadDashboard(),
            loadScans()
        ]);

        refreshButton.textContent =
            "↻ Refresh";

        refreshButton.disabled = false;
    }
);


// ================================
// INITIAL LOAD
// ================================

loadDashboard();

loadScans();