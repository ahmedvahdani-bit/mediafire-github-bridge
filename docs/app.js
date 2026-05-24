document.getElementById('startBtn').addEventListener('click', async () => {
    const pat = document.getElementById('patToken').value.trim();
    const user = document.getElementById('ghUser').value.trim();
    const repo = document.getElementById('ghRepo').value.trim();
    const mfUrl = document.getElementById('mfUrl').value.trim();

    if (!pat || !user || !repo || !mfUrl) {
        logToConsole('Error: All fields are required!', 'error');
        return;
    }

    // Generate unique Job ID using timestamp
    const jobId = 'job_' + Date.now();
    document.getElementById('currentJobId').innerText = jobId;
    
    updateStatus('RUNNING', 'running');
    logToConsole(`Initializing workflow dispatch for Job: ${jobId}`);
    
    const apiUrl = `https://api.github.com/repos/${user}/${repo}/actions/workflows/worker.yml/dispatches`;
    
    try {
        // Trigger GitHub Action
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
                    mediafire_url: mfUrl,
                    job_id: jobId
                }
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(`API Error ${response.status}: ${errData.message}`);
        }

        logToConsole('Workflow triggered successfully. System is now processing backend tasks.');
        logToConsole('Please wait while files are downloaded, split, and committed (This may take several minutes)...');
        
        // Generate Codeload Link immediately for future reference
        const codeloadUrl = `https://codeload.github.com/${user}/${repo}/zip/refs/heads/main`;
        const linkEl = document.getElementById('codeloadLink');
        linkEl.href = codeloadUrl;
        linkEl.innerText = codeloadUrl;
        linkEl.classList.remove('disabled');

        // Optional: Polling logic could be added here using GET /repos/{owner}/{repo}/actions/runs
        // For simplicity in this static architecture, we assume completion or manual check via Actions tab.
        setTimeout(() => {
            updateStatus('COMPLETED (Check Repo)', 'success');
            logToConsole('Workflow dispatch completed. Check your GitHub Actions tab for live pipeline logs.');
        }, 5000);

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
