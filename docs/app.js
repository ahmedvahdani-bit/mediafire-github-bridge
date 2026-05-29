document.getElementById('startBtn').addEventListener('click', async () => {
    const pat = document.getElementById('patToken').value.trim();
    const user = document.getElementById('ghUser').value.trim();
    const repo = document.getElementById('ghRepo').value.trim();
    const targetUrl = document.getElementById('targetUrl').value.trim();
    const quality = document.getElementById('qualitySelect').value;

    if (!pat || !user || !repo || !targetUrl) {
        logToConsole('Error: Token, Username, Repo, and URL are required!', 'error');
        return;
    }

    const jobId = 'job_' + Date.now();
    document.getElementById('currentJobId').innerText = jobId;
    
    updateStatus('RUNNING', 'running');
    logToConsole(`Initializing Universal V2 dispatch for Job: ${jobId}`);
    logToConsole(`Target URL: ${targetUrl.substring(0, 40)}...`);
    logToConsole(`Quality Strategy: ${quality}`);
    
    const apiUrl = `https://api.github.com/repos/${user}/${repo}/actions/workflows/worker.yml/dispatches`;
    
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

        logToConsole('V2 Workflow triggered successfully.');
        logToConsole('Check GitHub Actions tab for live yt-dlp logs.');
        
        // Generate Codeload Link
        const codeloadUrl = `https://codeload.github.com/${user}/${repo}/zip/refs/heads/main`;
        const linkEl = document.getElementById('codeloadLink');
        linkEl.href = codeloadUrl;
        linkEl.innerText = codeloadUrl;
        linkEl.classList.remove('disabled');

        // Generate RAW Github Content Link for the Manifest
        // Format: https://raw.githubusercontent.com/USER/REPO/main/data/jobs/JOB_ID/master_manifest.json
        const rawUrl = `https://raw.githubusercontent.com/${user}/${repo}/main/data/jobs/${jobId}/master_manifest.json`;
        const rawEl = document.getElementById('rawManifestLink');
        rawEl.href = rawUrl;
        rawEl.classList.remove('disabled');

        setTimeout(() => {
            updateStatus('DISPATCHED (Processing...)', 'success');
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
