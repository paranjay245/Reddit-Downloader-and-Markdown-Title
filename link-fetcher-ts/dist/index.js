"use strict";
// src/index.ts (Hybrid Approach - V9 - Improved Failure Formatting)
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
// --- Dependencies ---
const axios_1 = __importDefault(require("axios"));
const cheerio = __importStar(require("cheerio"));
const playwright_1 = require("playwright");
const url_1 = require("url");
// --- Configuration ---
const urlsToFetch = [
    "https://www.espncricinfo.com/series/ipl-2025-1449924/lucknow-super-giants-vs-punjab-kings-13th-match-1473450/live-cricket-score",
    "https://www.hotstar.com/in/sports/cricket/lsg-vs-pbks/1540040213/video/live/watch",
    "https://apps.apple.com/us/app/uhf-love-your-iptv/id6443751726",
    "https://apps.apple.com/us/app/sortio/id6737292062?mt=12",
    "https://www.reddit.com/r/AskReddit/s/gUhoHN6h7j",
    "https://www.reddit.com/r/JEENEETards/s/WwYnYRcAx6",
    "https://www.youtube.com/watch?v=tELxjdWHByk",
    "https://x.com/sama",
    "https://1001albumsgenerator.com/",
    "https://t3.chat/chat",
    "https://help.openai.com/en/articles/6825453-chatgpt-release-notes",
    "https://invalid-url-that-will-fail.xyz/",
    "https://broflix.ci/watch/movie/1290938?title=South%20Park:%20The%20End%20of%20Obesity&imdb_id=tt32375562"
];
const FAST_CHECK_TIMEOUT_MS = 10000;
const PLAYWRIGHT_TIMEOUT_MS = 75000;
const DELAY_BETWEEN_REQUESTS_MS = 750;
const USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36';
const REQUEST_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Cache-Control': 'no-cache',
};
// Titles that indicate a failure to get the real content or are generic login prompts
const FAILURE_TITLES = [
    "access denied", "page not found", "404", "403 forbidden", "error",
    "just a moment...", "log in", "sign in", "log in to x" // Added login/signin/X login
];
// --- Helper: Title Cleaning Function (REVISED to be LESS aggressive) ---
function cleanTitle(rawTitle, url) {
    if (!rawTitle) {
        return null;
    }
    let title = rawTitle.replace(/\u200e/g, '').trim();
    // Special handling for Reddit titles - preserve the original format
    if (url.includes('reddit.com')) {
        // If it already has the r/subreddit format, keep it as is
        if (title.includes(' : r/')) {
            return title;
        }
        // Only clean up generic Reddit titles
        if (title.toLowerCase().includes('reddit - dive into anything') ||
            title.toLowerCase().includes('reddit - the heart of the internet')) {
            return null;
        }
        return title;
    }
    // Special handling for X/Twitter titles - preserve the original format
    if (url.includes('x.com') || url.includes('twitter.com')) {
        // If it's not just "X" or "Twitter", keep it as is
        if (title && !title.match(/^(X|Twitter)$/i)) {
            return title;
        }
        return null;
    }
    const suffixesToRemove = [
        '- YouTube', '| YouTube',
        '| Reddit',
        '| BROFLIX'
    ];
    const prefixesToRemove = ['Watch '];
    const genericTitlesToDiscard = [
        "x", "log in to x", "log in", "sign in",
        "javascript required", "error", "page not found", "404", "403 forbidden", "forbidden",
        "just a moment...", "enable cookies", "enable javascript",
        "reddit - dive into anything", "reddit - the heart of the internet"
    ];
    let changed = true;
    while (changed) {
        changed = false;
        for (const suffix of suffixesToRemove) {
            if (title.endsWith(suffix)) {
                title = title.substring(0, title.length - suffix.length).trim();
                changed = true;
                break;
            }
        }
        if (changed)
            continue;
        for (const prefix of prefixesToRemove) {
            if (title.startsWith(prefix)) {
                title = title.substring(prefix.length).trim();
                changed = true;
                break;
            }
        }
    }
    if (genericTitlesToDiscard.includes(title.toLowerCase())) {
        if (title.toLowerCase() !== "welcome to t3 chat - t3 chat") {
            console.log(`    [Cleaner] Discarded generic title: '${rawTitle}'`);
            return null;
        }
    }
    // --- Final Cleanup ---
    title = title.replace(/\s+/g, ' ').trim();
    return title || null;
}
// --- Helper: Fallback Title Generation (Returns NULL) ---
function getFallbackTitle(url, reason) {
    console.log(`    [Fallback Triggered] ${reason}. Will use URL as title.`);
    return null; // Indicate failure to get title
}
// --- Main Hybrid Fetching Function (User's Code Base) ---
function fetchTitlesHybrid() {
    return __awaiter(this, void 0, void 0, function* () {
        var _a, _b;
        let browser = null;
        const results = [];
        console.log("🚀 Starting Hybrid Title Fetching (V9 - Improved Failure Formatting)...");
        console.log(`Processing ${urlsToFetch.length} URLs...`);
        // --- Fetching Loop (Identical to V8 - condensed logging for brevity) ---
        for (let i = 0; i < urlsToFetch.length; i++) {
            const url = urlsToFetch[i];
            const urlNum = i + 1;
            console.log(`\n[${urlNum}/${urlsToFetch.length}] Processing: ${url}`);
            let fetchedTitle = null;
            let fetchMethod = "None";
            let effectiveUrl = url;
            // Step 1: axios
            try {
                const response = yield axios_1.default.get(url, { headers: REQUEST_HEADERS, timeout: FAST_CHECK_TIMEOUT_MS, maxRedirects: 5 });
                effectiveUrl = ((_b = (_a = response.request) === null || _a === void 0 ? void 0 : _a.res) === null || _b === void 0 ? void 0 : _b.responseUrl) || url;
                const contentType = response.headers['content-type'] || '';
                if (contentType.toLowerCase().includes('html')) {
                    const $ = cheerio.load(response.data);
                    const rawTitle = $('meta[property="og:title"]').attr('content') || $('meta[name="twitter:title"]').attr('content') || $('title').text() || null;
                    if (rawTitle) {
                        console.log(`  ⚡ axios raw: '${rawTitle.substring(0, 60)}...'`);
                        fetchedTitle = cleanTitle(rawTitle, effectiveUrl);
                    }
                    if (fetchedTitle) {
                        console.log(`  ✅ axios clean: '${fetchedTitle}'`);
                        fetchMethod = "Fast (axios)";
                    }
                    else {
                        if (rawTitle)
                            console.log(`  ⚠️ axios clean fail`);
                    }
                }
                else {
                    console.log(`  ⚠️ axios skip non-html`);
                }
            }
            catch (error) {
                console.log(`  ❌ axios fail: ${axios_1.default.isAxiosError(error) ? error.code : error.message}`);
                fetchedTitle = null;
            }
            // Step 2: Playwright Fallback
            if (!fetchedTitle) {
                fetchMethod = "Slow (Playwright)";
                console.log("  🐢 Playwright fallback...");
                let context = null, page = null;
                try {
                    if (!browser) {
                        console.log("    launching browser...");
                        browser = yield playwright_1.chromium.launch({ headless: true });
                    }
                    context = yield browser.newContext({ userAgent: USER_AGENT, javaScriptEnabled: true, ignoreHTTPSErrors: true });
                    page = yield context.newPage();
                    yield page.setExtraHTTPHeaders(REQUEST_HEADERS);
                    console.log(`      Navigating with Playwright... (Timeout: ${PLAYWRIGHT_TIMEOUT_MS / 1000}s)`);
                    yield page.goto(url, { timeout: PLAYWRIGHT_TIMEOUT_MS, waitUntil: 'networkidle' });
                    const effectiveUrl = page.url();
                    console.log(`      Landed on: ${effectiveUrl}`);
                    // Special handling for Reddit and X/Twitter
                    if (url.includes('reddit.com')) {
                        // Wait for the post title to load
                        try {
                            yield page.waitForSelector('h1', { timeout: 5000 });
                            const titleElement = yield page.$('h1');
                            if (titleElement) {
                                const rawTitle = yield titleElement.textContent();
                                if (rawTitle && !rawTitle.includes('Reddit - The heart of the internet')) {
                                    console.log(`      Found Reddit post title: '${rawTitle}'`);
                                    fetchedTitle = cleanTitle(rawTitle, effectiveUrl);
                                }
                            }
                        }
                        catch (error) {
                            console.log(`      Could not find Reddit post title: ${error.message}`);
                        }
                    }
                    else if (url.includes('x.com') || url.includes('twitter.com')) {
                        yield page.waitForTimeout(1500);
                        const usernameMatch = url.match(/(?:x\.com|twitter\.com)\/([^\/\?]+)/i);
                        const username = usernameMatch ? usernameMatch[1] : '';
                        const pageData = yield page.evaluate(() => {
                            const scripts = Array.from(document.querySelectorAll('script'));
                            let userData = null;
                            for (const script of scripts) {
                                const content = script.textContent || '';
                                if (content.includes('"screen_name"') || content.includes('"followers_count"')) {
                                    try {
                                        const jsonMatch = content.match(/({.+})/);
                                        if (jsonMatch) {
                                            const data = JSON.parse(jsonMatch[1]);
                                            if (data.user || data.profile) {
                                                userData = data.user || data.profile;
                                                break;
                                            }
                                        }
                                    }
                                    catch (e) {
                                        continue;
                                    }
                                }
                            }
                            if (!userData) {
                                const nameSelectors = [
                                    'meta[property="og:title"]',
                                    'meta[name="twitter:title"]',
                                    'h1[data-testid="primaryColumn"] div[data-testid="UserName"] div span'
                                ];
                                const descriptionSelectors = [
                                    'meta[name="description"]',
                                    'meta[property="og:description"]'
                                ];
                                for (const selector of nameSelectors) {
                                    const element = document.querySelector(selector);
                                    if (element) {
                                        const content = element.getAttribute('content') || element.textContent;
                                        if (content && !content.includes('X (formerly Twitter)')) {
                                            userData = { name: content.trim() };
                                            break;
                                        }
                                    }
                                }
                                if (userData) {
                                    for (const selector of descriptionSelectors) {
                                        const element = document.querySelector(selector);
                                        if (element) {
                                            const content = element.getAttribute('content') || element.textContent;
                                            if (content) {
                                                const match = content.match(/(\d+(?:,\d+)*)\s*Followers?/i);
                                                if (match) {
                                                    userData.followers_count = match[1].replace(/,/g, '');
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            return userData;
                        });
                        const displayName = (pageData === null || pageData === void 0 ? void 0 : pageData.name) || (pageData === null || pageData === void 0 ? void 0 : pageData.screen_name) || null;
                        const followerCount = (pageData === null || pageData === void 0 ? void 0 : pageData.followers_count) || '0';
                        const formattedTitle = displayName
                            ? `${displayName} (@${username}) / X`
                            : `(@${username}) / X`;
                        console.log('Created X/Twitter title:', formattedTitle);
                        fetchedTitle = formattedTitle;
                    }
                    // If we didn't get a good title from the special handling, try the page title
                    if (!fetchedTitle) {
                        yield page.waitForTimeout(1500);
                        const rawTitle = yield page.title();
                        console.log(`      Playwright raw title: '${rawTitle.substring(0, 70)}${rawTitle.length > 70 ? '...' : ''}'`);
                        fetchedTitle = cleanTitle(rawTitle, effectiveUrl);
                    }
                    yield page.close();
                    yield context.close();
                }
                catch (error) {
                    console.error(`  ❌ Playwright error: ${error.message.split('\n')[0]}`);
                    fetchedTitle = null;
                }
            }
            // Step 3: Final Fallback determination
            if (!fetchedTitle && fetchMethod !== "Fast (axios)") {
                fetchMethod = "Fallback";
                fetchedTitle = getFallbackTitle(url, "Both methods failed");
            }
            else if (!fetchedTitle && fetchMethod === "Fast (axios)") {
                fetchMethod = "Fallback (Cleaned)";
                fetchedTitle = null;
            }
            // Store result
            results.push({ url: url, title: fetchedTitle, method: fetchMethod, effectiveUrl: effectiveUrl });
            // Delay
            if (i < urlsToFetch.length - 1) {
                console.log(`--- delay ${DELAY_BETWEEN_REQUESTS_MS}ms ---`);
                yield new Promise(resolve => setTimeout(resolve, DELAY_BETWEEN_REQUESTS_MS));
            }
        } // --- End loop ---
        // Cleanup
        if (browser) {
            console.log("\nClosing shared Playwright browser instance...");
            yield browser.close();
        }
        // --- Generate Final Markdown Output ---
        console.log("\n--- ✅ Processing Complete ---");
        console.log("\n--- Final Markdown List (V9 - Improved Failure Formatting) ---");
        const finalMarkdownLines = []; // Collect lines before printing
        results.forEach(r => {
            const urlToUse = r.effectiveUrl || r.url;
            let markdownLine;
            const fetchFailed = !r.title;
            if (fetchFailed) {
                markdownLine = `- ${urlToUse}`;
                console.log(`   LOG: Failed fetch for ${r.url} (Method: ${r.method}) -> Outputting plain URL`);
            }
            else {
                let displayTitle = r.title;
                try {
                    const parsedUrl = new url_1.URL(urlToUse);
                    const hostname = parsedUrl.hostname.replace(/^www\./, '');
                    // Reddit Specific Formatting
                    const redditRegex = /reddit\.com\/r\/([^\/]+)/i;
                    const redditMatch = urlToUse.match(redditRegex);
                    if (redditMatch && redditMatch[1]) {
                        const subreddit = redditMatch[1];
                        // If the title already has the r/subreddit format, use it as is
                        if (displayTitle.includes(' : r/')) {
                            markdownLine = `- [${displayTitle}](${urlToUse})`;
                        }
                        else {
                            // Clean up Reddit title
                            displayTitle = displayTitle
                                .replace(/reddit - dive into anything/i, '')
                                .replace(/reddit - the heart of the internet/i, '')
                                .trim();
                            if (!displayTitle) {
                                markdownLine = `- ${urlToUse}`;
                                console.log(`   LOG: Reddit title cleaning resulted in empty title -> Outputting plain URL`);
                            }
                            else {
                                markdownLine = `- [${displayTitle} : r/${subreddit}](${urlToUse})`;
                            }
                        }
                    }
                    // X.com/Twitter Specific Formatting
                    else if (hostname === 'x.com' || hostname === 'twitter.com') {
                        const urlUsernameMatch = urlToUse.match(/(?:x\.com|twitter\.com)\/([^\/\?]+)/i);
                        const urlUsername = urlUsernameMatch ? urlUsernameMatch[1] : '';
                        
                        if (urlUsername && urlUsername !== 'home' && urlUsername !== 'explore' && 
                            urlUsername !== 'notifications' && urlUsername !== 'messages') {
                            let displayName = '';
                            
                            if (displayTitle && !displayTitle.match(/^(X|Twitter)$/i)) {
                                const cleanedTitle = displayTitle.replace(/^\(\d+(?:,\d+)*\)\s*/, '');
                                
                                const nameMatch = cleanedTitle.match(/^([^@]+)@/);
                                if (nameMatch) {
                                    displayName = nameMatch[1].trim();
                                }
                            }
                            
                            if (!displayName) {
                                displayName = urlUsername;
                            }
                            
                            markdownLine = `- [${displayName} (@${urlUsername}) / X](${urlToUse})`;
                        } else {
                            markdownLine = `- ${urlToUse}`;
                            console.log(`   LOG: X/Twitter URL doesn't contain a valid username -> Outputting plain URL`);
                        }
                    }
                    // Other Formatting/Cleaning
                    else {
                        if (hostname === 'youtube.com') {
                            displayTitle = displayTitle.replace(/\s+-\s+YouTube$/i, '').trim();
                        }
                        else if (hostname === 'apps.apple.com') {
                            displayTitle = displayTitle.replace(/ on the (Mac )?App Store$/i, '').trim();
                        }
                        displayTitle = displayTitle.replace(/\[/g, '(').replace(/\]/g, ')');
                        markdownLine = `- [${displayTitle}](${urlToUse})`;
                    }
                    console.log(`   LOG: Success fetch for ${r.url} (Method: ${r.method}) -> Title: '${displayTitle}'`);
                }
                catch (formatError) {
                    console.error(`  LOG: FORMATTING error for ${urlToUse}: ${formatError.message}`);
                    markdownLine = `- ${urlToUse}`;
                }
            }
            finalMarkdownLines.push(markdownLine);
        });
        // Print the final collected list cleanly
        finalMarkdownLines.forEach(line => console.log(line));
    });
}
// --- Run ---
fetchTitlesHybrid().catch(err => {
    console.error("\n🚨 An unexpected critical error occurred during execution:", err);
    process.exit(1);
});
