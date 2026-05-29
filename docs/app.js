// --- CONFIGURATION ---
const GITHUB_USERNAME = "ahmedvahdani-bit";
const GITHUB_REPO = "mediafire-github-bridge";  
// ---------------------

document.getElementById('startBtn').addEventListener('click', async () => {
    const pat = document.getElementById('patToken').value.trim();
    const targetUrl = document.getElementById('targetUrl').value.trim();
    const quality = document.getElementById('qualitySelect').value;

    if (!pat || !targetUrl) {
        logToConsole('Error: Token and URL are required!', 'error');
        return;
    }

    const jobId = 'job_' + Date.now();
    document.getElementById('currentJobId').innerText = jobId;
    
    updateStatus('RUNNING', 'running');
    logToConsole(`Initializing dispatch for Job: ${jobId}`);
    
    const apiUrl = `https://api.github.com/repos/${GITHUB_USERNAME}/${GITHUB_REPO}/actions/workflows/worker.yml/dispatches`;
    
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Accept': 'application/vnd.github+json',
                'Authorization': `Bearer ${pat}`,
                'X-GitHub-Api-Version': '2022-11-28',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ref: 'main',
                inputs: {
                    target_url: targetUrl,
                    job_id: jobId,
                    quality: quality
                }
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(`API Error ${response.status}: ${errData.message}`);
        }

        logToConsole('Workflow triggered successfully.');
        
        const rawUrl = `https://raw.githubusercontent.com/${GITHUB_USERNAME}/${GITHUB_REPO}/main/data/jobs/${jobId}/master_manifest.json`;
        const rawEl = document.getElementById('rawManifestLink');
        rawEl.href = rawUrl;
        rawEl.innerText = "Click here for Direct Raw Links (Available after job finishes)";
        rawEl.classList.remove('disabled');

        setTimeout(() => {
            updateStatus('DISPATCHED', 'success');
        }, 3000);

    } catch (error) {
        updateStatus('FAILED', 'error');
        logToConsole(`Exception: ${error.message}`, 'error');
    }
});

function logToConsole(message, type = 'info') {
    const consoleEl = document.getElementById('logConsole');
    const timestamp = new Date().toLocaleTimeString();
    const prefix = type === 'error' ? '[ERROR]' : '[INFO]';
    consoleEl.innerText += `\n> ${timestamp} ${prefix} ${message}`;
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

function updateStatus(text, className) {
    const badge = document.getElementById('statusBadge');
    badge.innerText = text;
    badge.className = `badge ${className}`;
}
