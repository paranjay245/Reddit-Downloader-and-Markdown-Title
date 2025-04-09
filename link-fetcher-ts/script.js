// --- DOM Elements ---
const bulkInput = document.getElementById('bulkInput');
const processButton = document.getElementById('processButton');
const markdownOutput = document.getElementById('markdownOutput');
const urlOutput = document.getElementById('urlOutput');
const nonUrlOutput = document.getElementById('nonUrlOutput');

const copyMarkdownButton = document.getElementById('copyMarkdownButton');
const downloadMarkdownButton = document.getElementById('downloadMarkdownButton');
const urlMarkdownToggle = document.getElementById('urlMarkdownToggle');
const copyUrlsButton = document.getElementById('copyUrlsButton');
const downloadUrlsButton = document.getElementById('downloadUrlsButton');
const copyNonUrlsButton = document.getElementById('copyNonUrlsButton');
const downloadNonUrlsButton = document.getElementById('downloadNonUrlsButton');

// --- Global Storage ---
let extractedUrls = []; // Store original URLs for toggle

// --- Event Listeners ---
processButton.addEventListener('click', processInput);
urlMarkdownToggle.addEventListener('change', toggleUrlOutputFormat);

// Add listeners for copy/download buttons
copyMarkdownButton.addEventListener('click', () => copyToClipboard(markdownOutput));
downloadMarkdownButton.addEventListener('click', () => downloadFile(markdownOutput.value, 'links.md', 'text/markdown'));
copyUrlsButton.addEventListener('click', () => copyToClipboard(urlOutput));
downloadUrlsButton.addEventListener('click', () => downloadFile(urlOutput.value, 'urls.txt', 'text/plain'));
copyNonUrlsButton.addEventListener('click', () => copyToClipboard(nonUrlOutput));
downloadNonUrlsButton.addEventListener('click', () => downloadFile(nonUrlOutput.value, 'text.txt', 'text/plain'));


// --- Core Processing Function ---
async function processInput() {
    const inputText = bulkInput.value.trim();
    extractedUrls = []; // Reset global urls
    const nonUrls = [];
    let markdownResult = "";
    let urlsResult = "";

    // Clear previous outputs
    markdownOutput.value = "";
    urlOutput.value = "";
    nonUrlOutput.value = "";
    urlMarkdownToggle.checked = false; // Reset toggle
    disableAllOutputButtons();

    if (!inputText) {
        return; // Nothing to process
    }

    processButton.textContent = 'Processing...';
    processButton.disabled = true;

    const lines = inputText.split('\n');
    // Slightly improved URL regex (still basic)
    const urlPattern = /^(https?:\/\/[^\s$.?#].[^\s]*)$/i;

    lines.forEach(line => {
        const trimmedLine = line.trim();
        if (urlPattern.test(trimmedLine)) {
            try {
                new URL(trimmedLine); // Validate parsability
                extractedUrls.push(trimmedLine);
            } catch (e) {
                if (trimmedLine) nonUrls.push(trimmedLine); // Invalid URL structure
            }
        } else if (trimmedLine) {
            nonUrls.push(trimmedLine); // Non-URL text
        }
    });

    // --- Generate Outputs ---

    // Layer 1 & Prepare Layer 2 (URLs)
    urlsResult = extractedUrls.join('\n');
    urlOutput.value = urlsResult; // Set Layer 2 initially to raw URLs

    for (const url of extractedUrls) {
        let title = "Page Title (Fetch Blocked)"; // Default placeholder
        let isRedditPost = false;
        try {
            const parsedUrl = new URL(url);
            title = `Page at ${parsedUrl.hostname}`; // Use hostname as better default
            // Check if it's a Reddit post link
             if (parsedUrl.hostname.includes('reddit.com') && parsedUrl.pathname.includes('/comments/')) {
                  // Basic check - could be more specific (e.g., exclude user profiles)
                  isRedditPost = true;
             } else if (parsedUrl.hostname.includes('reddit.com') && parsedUrl.pathname.includes('/r/') && parsedUrl.pathname.includes('/s/')) {
                 // Handle the /s/ share links as well
                 isRedditPost = true;
             }
        } catch {
            title = "Invalid URL";
        }

        // Add Reddit "download" note to Layer 1 Markdown
        if (isRedditPost) {
            // NOTE: This is just text output, not actual fetching
             markdownResult += `- [${title} - (Reddit Post Content Fetch Simulated)](${url})\n`;
        } else {
            markdownResult += `- [${title}](${url})\n`;
        }

        // Add slight delay for visual feedback during processing (optional)
        // await new Promise(resolve => setTimeout(resolve, 10));
    }

    // Layer 3
    nonUrlOutput.value = nonUrls.join('\n');

    // Update Layer 1 Output
    markdownOutput.value = markdownResult.trim();

    // Enable buttons if content exists
    enableOutputButtons();

    processButton.textContent = 'Extract Layers';
    processButton.disabled = false;
}


// --- Layer 2 Toggle ---
function toggleUrlOutputFormat() {
    if (!extractedUrls.length) return;

    let newUrlOutput = "";
    if (urlMarkdownToggle.checked) {
        // Format as Markdown
        extractedUrls.forEach(url => {
            let title = "Page Title (Fetch Blocked)";
            try { title = `Page at ${new URL(url).hostname}`; } catch { title = "Invalid URL"; }
            newUrlOutput += `- [${title}](${url})\n`;
        });
         downloadUrlsButton.textContent = 'Download .md'; // Change download type
    } else {
        // Format as raw URLs
        newUrlOutput = extractedUrls.join('\n');
         downloadUrlsButton.textContent = 'Download .txt'; // Change download type back
    }
    urlOutput.value = newUrlOutput.trim();
}


// --- Button State Management ---
function disableAllOutputButtons() {
    copyMarkdownButton.disabled = true;
    downloadMarkdownButton.disabled = true;
    copyUrlsButton.disabled = true;
    downloadUrlsButton.disabled = true;
    copyNonUrlsButton.disabled = true;
    downloadNonUrlsButton.disabled = true;
    urlMarkdownToggle.disabled = true; // Disable toggle when no URLs
}

function enableOutputButtons() {
    copyMarkdownButton.disabled = !markdownOutput.value;
    downloadMarkdownButton.disabled = !markdownOutput.value;
    copyUrlsButton.disabled = !urlOutput.value;
    downloadUrlsButton.disabled = !urlOutput.value;
    copyNonUrlsButton.disabled = !nonUrlOutput.value;
    downloadNonUrlsButton.disabled = !nonUrlOutput.value;
     urlMarkdownToggle.disabled = !extractedUrls.length; // Enable toggle if URLs exist
}

// --- Utility Functions ---
function copyToClipboard(textareaElement) {
    if (!textareaElement.value) return;
    textareaElement.select();
    textareaElement.setSelectionRange(0, 99999); // For mobile devices

    navigator.clipboard.writeText(textareaElement.value)
        .then(() => {
            alert('Copied to clipboard!');
        })
        .catch(err => {
            alert('Failed to copy automatically. Please copy manually.');
            console.error('Clipboard copy failed:', err);
        });
}

function downloadFile(content, filename, mimeType) {
    if (!content) return;
    const blob = new Blob([content], { type: `${mimeType};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}