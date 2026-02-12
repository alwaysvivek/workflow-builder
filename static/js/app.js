const ACTIONS = [
    { value: 'clean', label: 'Clean' },
    { value: 'summarize', label: 'Summarize' },
    { value: 'keypoints', label: 'Keypoints' },
    { value: 'simplify', label: 'Simplify' },
    { value: 'analogy', label: 'Analogy' },
    { value: 'classify', label: 'Classify' },
    { value: 'tone', label: 'Tone Analysis' }
];

let SESSION_API_KEY = null;

document.addEventListener('DOMContentLoaded', () => {
    updateDropdowns(); // Initial population
    loadTemplates();   // Fetch and render templates

    // Check if we have key in sessionStorage
    const savedKey = sessionStorage.getItem('groq_api_key');
    if (savedKey) {
        // Validate silently or just use it? 
        // Let's just use it to keep it simple, but we should probably validate it if we want to be robust.
        // User said "once i enter it... then i dont see api key prompt".
        // Let's try to validate it quickly.
        validateDetailedKey(savedKey, true);
    }
});

async function loadTemplates() {
    try {
        const res = await fetch('/templates');
        if (!res.ok) throw new Error("Failed to load templates");
        const templates = await res.json();

        const container = document.getElementById('template-buttons');
        if (!container) return;

        container.innerHTML = ''; // Clear existing

        Object.keys(templates).forEach(key => {
            const tmpl = templates[key];
            const btn = document.createElement('button');
            btn.className = 'btn secondary-btn template-btn';
            btn.textContent = tmpl.label;
            btn.onclick = () => applyTemplate(tmpl.steps);
            container.appendChild(btn);
        });
    } catch (e) {
        console.error("Error loading templates:", e);
    }
}

function applyTemplate(steps) {
    if (!steps || steps.length < 3) return;

    // Set values
    const s1 = document.getElementById('step-1');
    const s2 = document.getElementById('step-2');
    const s3 = document.getElementById('step-3');

    s1.value = steps[0];
    updateDropdowns(); // Update S2 options based on S1

    s2.value = steps[1];
    // We need to manually trigger the change event or call updateDropdowns logic again
    // updateDropdowns() handles S2->S3 logic internally if we call it right?
    // Actually updateDropdowns() reads current values. 
    // But pupulateSelect clears the innerHTML of s2 and s3!

    // Valid approach:
    // 1. Set S1
    // 2. call updateDropdowns() -> this repopulates S2 and S3 based on S1. S2 and S3 values are lost/reset.
    // 3. Set S2
    // 4. call pupulateSelect for S3 separately? Or just updateDropdowns again?

    // Let's refine updateDropdowns to NOT reset if we pass values? 
    // Or just set them sequentially.

    // updateDropdowns() implementation:
    // const v1 = s1.options[s1.selectedIndex]?.value || "";
    // pupulateSelect(s2, v1, v2); -> Uses current v2 (which is empty string after repopulate?)
    // Actually pupulateSelect: const oldVal = currentValue || select.value;

    // So if we set s2.value *before* calling updateDropdowns(), it might be preserved IF the value is valid.
    // BUT s2 options might not contain the value yet if s1 just changed.

    // Correct sequence:
    // 1. Set S1
    // 2. Repopulate S2 options (exclude S1)
    // 3. Set S2
    // 4. Repopulate S3 options (exclude S1, S2)
    // 5. Set S3

    // Let's reuse pupulateSelect logic manually or just force it.

    // 1. Set S1
    s1.value = steps[0];

    // 2. Populate S2
    pupulateSelect(s2, steps[0], steps[1]);
    // 3. Set S2 (pupulateSelect does this if we pass current value as 3rd arg)

    // 4. Populate S3
    pupulateSelect(s3, [steps[0], steps[1]], steps[2]);
    // 5. Set S3
}

async function validateKey() {
    const keyInput = document.getElementById('gate-api-key');
    const errorDiv = document.getElementById('gate-error');
    const btn = document.getElementById('validate-btn');
    const key = keyInput.value.trim();

    if (!key) {
        errorDiv.textContent = "Please enter an API Key.";
        errorDiv.classList.remove('hidden');
        return;
    }

    errorDiv.classList.add('hidden');
    btn.disabled = true;
    btn.textContent = "Validating...";

    await validateDetailedKey(key, false);
}

async function validateDetailedKey(key, isSilent) {
    const errorDiv = document.getElementById('gate-error');
    const btn = document.getElementById('validate-btn');
    const gate = document.getElementById('api-gate');
    const mainUi = document.getElementById('main-ui');

    try {
        const res = await fetch('/validate-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: key })
        });

        const data = await res.json();

        if (res.ok && data.valid) {
            // Success
            SESSION_API_KEY = key;
            sessionStorage.setItem('groq_api_key', key);
            gate.classList.add('hidden');
            mainUi.classList.remove('hidden');
        } else {
            throw new Error(data.error || "Invalid API Key");
        }
    } catch (e) {
        if (!isSilent) {
            errorDiv.textContent = e.message;
            errorDiv.classList.remove('hidden');
        } else {
            // If silent check failed (e.g. key expired), create clear storage
            sessionStorage.removeItem('groq_api_key');
        }
    } finally {
        if (!isSilent) {
            btn.disabled = false;
            btn.textContent = "Enter Workflow Builder";
        }
    }
}

function updateDropdowns() {
    const s1 = document.getElementById('step-1');
    const s2 = document.getElementById('step-2');
    const s3 = document.getElementById('step-3');

    const v1 = s1.options[s1.selectedIndex]?.value || "";
    const v2 = s2.options[s2.selectedIndex]?.value || "";
    const v3 = s3.options[s3.selectedIndex]?.value || "";

    // Populate Step 2 (exclude v1)
    pupulateSelect(s2, v1, v2);

    // Populate Step 3 (exclude v1 and v2)
    pupulateSelect(s3, [v1, s2.value], v3);
}

function pupulateSelect(select, excludeValues, currentValue) {
    if (!Array.isArray(excludeValues)) excludeValues = [excludeValues];

    // Check if we need to rebuild options
    // To avoid flickering, we can check if options are already correct?
    // But simple rebuild is fine for this scale.

    // Save current selection if possible
    const oldVal = currentValue || select.value;

    select.innerHTML = '<option value="" disabled selected>Select Action</option>';

    ACTIONS.forEach(action => {
        if (!excludeValues.includes(action.value)) {
            const opt = document.createElement('option');
            opt.value = action.value;
            opt.textContent = action.label;
            if (action.value === oldVal) opt.selected = true;
            select.appendChild(opt);
        }
    });
}

// Ensure S2 change updates S3
document.getElementById('step-2').addEventListener('change', () => {
    const s1 = document.getElementById('step-1').value;
    const s2 = document.getElementById('step-2').value;
    const s3 = document.getElementById('step-3');
    pupulateSelect(s3, [s1, s2], s3.value);
});


async function runWorkflow() {
    const inputText = document.getElementById('input-text').value;
    const s1 = document.getElementById('step-1').value;
    const s2 = document.getElementById('step-2').value;
    const s3 = document.getElementById('step-3').value;
    const btn = document.getElementById('run-btn');
    const errorDiv = document.getElementById('error-msg');
    const resultsArea = document.getElementById('results-area');

    // Validation
    errorDiv.classList.add('hidden');
    if (!SESSION_API_KEY) return showError("API Key missing. Please refresh and log in again.");
    if (!inputText) return showError("Please enter some input text.");
    if (!s1 || !s2 || !s3) return showError("Please select actions for all 3 steps.");

    // UI Reset
    btn.disabled = true;
    btn.textContent = "Running...";
    resultsArea.classList.remove('hidden');

    // Reset output cards
    [1, 2, 3].forEach(i => {
        document.getElementById(`result-step-${i}`).classList.remove('hidden');
        document.getElementById(`output-${i}`).textContent = '';
        document.getElementById(`status-${i}`).className = 'status-indicator waiting';
        document.getElementById(`status-${i}`).textContent = 'Waiting...';

        // Update Action Names
        const sel = document.getElementById(`step-${i}`);
        const label = sel.options[sel.selectedIndex].text;
        document.getElementById(`action-name-${i}`).textContent = label;
    });

    try {
        // 1. Create Workflow Definition
        const wfRes = await fetch('/workflows', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: "Frontend Workflow",
                steps: [
                    { action: s1 },
                    { action: s2 },
                    { action: s3 }
                ]
            })
        });

        if (!wfRes.ok) throw new Error("Failed to create workflow definition.");
        const wfData = await wfRes.json();
        const wfId = wfData.id;

        // 2. Start Streaming Run
        const response = await fetch(`/workflows/${wfId}/run_stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-groq-api-key': SESSION_API_KEY
            },
            body: JSON.stringify({ input_text: inputText })
        });

        if (!response.ok) throw new Error(`Streaming failed: ${response.statusText}`);

        // Read stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep last incomplete line

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const msg = JSON.parse(line);
                    handleStreamMessage(msg);
                } catch (e) {
                    console.error("JSON Parse error", e);
                }
            }
        }

    } catch (e) {
        showError(e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = "Run";
    }
}

function handleStreamMessage(msg) {
    if (msg.error) {
        showError(msg.details || msg.error);
        return;
    }

    if (msg.status === "workflow_completed") {
        return;
    }

    const stepNum = msg.step;
    const outputDiv = document.getElementById(`output-${stepNum}`);
    const statusSpan = document.getElementById(`status-${stepNum}`);

    if (msg.status === "started") {
        statusSpan.className = 'status-indicator running';
        statusSpan.textContent = 'Processing...';
    } else if (msg.chunk) {
        // Append text
        outputDiv.textContent += msg.chunk;
    } else if (msg.status === "completed") {
        statusSpan.className = 'status-indicator completed';
        statusSpan.textContent = 'Completed';
    }
}

function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.classList.remove('hidden');
}
