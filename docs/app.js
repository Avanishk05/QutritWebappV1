'use strict';

const API_BASE = 'http://127.0.0.1:5001/api/v1';

// DOM Elements
const d = document;
const screens = [
    d.getElementById('screen-0'),
    d.getElementById('screen-1'),
    d.getElementById('screen-2'),
    d.getElementById('screen-3'),
    d.getElementById('screen-4'),
    d.getElementById('screen-5')
];
const errorBar = d.getElementById('global-error');

// Screen 0
const state1 = d.getElementById('bootstrap-state-1');
const state2 = d.getElementById('bootstrap-state-2');
const state3 = d.getElementById('bootstrap-state-3');
const dlContainer = d.getElementById('downloads-container');

// Screen 1
const btnDetectDevice = d.getElementById('btn-detect-device');

// Screen 2
const btnStartFlash = d.getElementById('btn-start-flash');
const btnCancelFlash = d.getElementById('btn-cancel-flash');
const inputSsid = d.getElementById('wifi-ssid');
const inputPassword = d.getElementById('wifi-password');
const lblDeviceChip = d.getElementById('device-chip');

// Screen 3
const flashProgress = d.getElementById('flash-progress');
const flashLog = d.getElementById('flash-log');

// Screen 4
const wifiStatus = d.getElementById('wifi-status');

// Screen 5
const btnFlashAnother = d.getElementById('btn-flash-another');

// State
let pollInterval = null;

// --- Flow Controller ---
function showScreen(index) {
    screens.forEach((s, i) => {
        if (s) {
            if (i === index) {
                s.classList.add('active');
            } else {
                s.classList.remove('active');
            }
        }
    });
    hideError();
}

function showError(msg) {
    errorBar.textContent = msg;
    errorBar.classList.remove('hidden');
}

function hideError() {
    errorBar.classList.add('hidden');
}

// --- API Helpers ---
async function apiGet(path) {
    const res = await fetch(`${API_BASE}${path}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
}

async function apiPost(path, body = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
}

// --- Screen 0: Agent Check ---
async function checkAgent() {
    showScreen(0);
    
    try {
        const data = await apiGet('/status');
        if (data.status === 'running') {
            // Agent found! Stop polling status and switch to polling downloads.
            if (pollInterval) clearInterval(pollInterval);
            pollInterval = setInterval(pollImages, 1000);
            pollImages();
        }
    } catch (err) {
        // State 1: Agent Missing
        state1.classList.remove('hidden');
        state2.classList.add('hidden');
        
        // Keep polling indefinitely until the user installs and service starts
        if (!pollInterval) {
            pollInterval = setInterval(checkAgent, 2000);
        }
    }
}

async function pollImages() {
    try {
        const data = await apiGet('/images/status');
        state1.classList.add('hidden');
        
        if (data.files_ready) {
            clearInterval(pollInterval);
            pollInterval = null;
            state2.classList.add('hidden');
            state3.classList.remove('hidden');
            setTimeout(() => {
                showScreen(1);
            }, 1000);
        } else {
            state2.classList.remove('hidden');
            dlContainer.innerHTML = data.files.map(f => {
                return `
                    <div style="margin-bottom: 0.5rem; text-align: left;">
                        <span class="card-label" style="display:flex; justify-content:space-between; margin-bottom: 0.25rem;">
                            <span>Downloading ${f.filename}</span>
                            <span>${f.progress_percent}%</span>
                        </span>
                        <div class="progress-container" style="height: 6px; margin-bottom: 0.25rem;">
                            <div class="progress-bar" style="width: ${f.progress_percent}%;"></div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch(err) {
        console.error("Image polling failed", err);
    }
}

// --- Screen 1: Detect Device ---
async function detectDevice() {
    btnDetectDevice.disabled = true;
    hideError();
    try {
        const data = await apiGet('/device');
        if (data.connected && data.maskrom) {
            lblDeviceChip.textContent = data.chip;
            showScreen(2);
        } else {
            showError("Device found, but not in MaskROM mode.");
        }
    } catch (err) {
        showError(err.message);
    } finally {
        btnDetectDevice.disabled = false;
    }
}

// --- Screen 2 & 3: Flash Flow ---
async function startFlash() {
    const ssid = inputSsid.value.trim();
    const pw = inputPassword.value;
    
    if (!ssid || !pw) {
        showError("WiFi credentials are required.");
        return;
    }
    
    btnStartFlash.disabled = true;
    hideError();
    try {
        await apiPost('/flash');
        showScreen(3);
        pollInterval = setInterval(pollLogs, 2000);
    } catch (err) {
        showError(err.message);
        btnStartFlash.disabled = false;
    }
}

async function pollLogs() {
    try {
        const data = await apiGet('/logs');
        
        flashProgress.style.width = `${data.progress}%`;
        
        if (data.lines && data.lines.length > 0) {
            // Render lines with minimal formatting mapping
            flashLog.innerHTML = data.lines.map(line => {
                if(line.includes('[ERROR')) return `<div class="log-line log-error">${line}</div>`;
                if(line.includes('[OK]')) return `<div class="log-line log-ok">${line}</div>`;
                if(line.includes('[STEP')) return `<div class="log-line log-step">${line}</div>`;
                return `<div class="log-line">${line}</div>`;
            }).join('');
            
            flashLog.scrollTop = flashLog.scrollHeight;
        }

        if (data.status === 'done' || data.status === 'error') {
            clearInterval(pollInterval);
            if (data.status === 'error') {
                showError("Flash failed. Check log.");
                btnStartFlash.disabled = false;
                // Switch back to Screen 2 to restart
                setTimeout(() => showScreen(2), 2000);
            } else {
                // Success leads to Screen 4 (WiFi)
                showScreen(4);
                configureWifi();
            }
        }
    } catch (err) {
        console.error("Log poll error", err);
    }
}

// --- Screen 4: WiFi Config ---
async function configureWifi() {
    wifiStatus.textContent = "Writing network config via adb shell...";
    try {
        await apiPost('/wifi', {
            ssid: inputSsid.value.trim(),
            password: inputPassword.value
        });
        showScreen(5);
    } catch (err) {
        showError("WiFi configuration failed: " + err.message);
        wifiStatus.textContent = "Failed. You can ignore this and configure manually later.";
        setTimeout(() => showScreen(5), 3000);
    }
}

// --- Binding Events ---
d.addEventListener('DOMContentLoaded', () => {
    btnDetectDevice.addEventListener('click', detectDevice);
    btnCancelFlash.addEventListener('click', () => showScreen(1));
    btnStartFlash.addEventListener('click', startFlash);
    btnFlashAnother.addEventListener('click', () => {
        if(pollInterval) clearInterval(pollInterval);
        pollInterval = null;
        checkAgent();
    });

    // Initial load
    checkAgent();
});
