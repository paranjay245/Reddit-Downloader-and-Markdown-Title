import { request } from 'obsidian';

const headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1'
};

async function fetchWithTimeout(url: string): Promise<string> {
    try {
        const response = await request({
            url: url,
            headers: headers
        });
        return response;
    } catch (error) {
        console.error('Error fetching URL:', error);
        throw error;
    }
}

function extractTitleFromHtml(html: string): string | null {
    // Try h1 tag first (most reliable for Reddit)
    const h1Match = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
    if (h1Match && h1Match[1].trim()) {
        return h1Match[1].trim();
    }

    // Try meta title as fallback
    const metaTitleMatch = html.match(/<meta[^>]*property="og:title"[^>]*content="([^"]*)"[^>]*>/i);
    if (metaTitleMatch) {
        return metaTitleMatch[1].trim();
    }

    return null;
}

export async function getRedditTitle(url: string): Promise<string> {
    try {
        // Clean up the URL by removing extra parentheses
        url = url.replace(/\)+$/, '');
        
        // Extract subreddit and post ID using the exact regex from reddit links.py
        const match = url.match(/https:\/\/www\.reddit\.com\/r\/([^/]+)\/s\/([^/]+)/);
        if (match) {
            const subreddit = match[1];
            const postId = match[2];
            
            // Try to get the title from the page
            const html = await fetchWithTimeout(url);
            
            // Try to find the post title in the HTML (exact same logic as Python)
            const title = extractTitleFromHtml(html);
            if (title) {
                return title;
            }
            
            // If we can't find the title, return subreddit-based format
            return `Post in r/${subreddit}`;
        }
        
        return 'Reddit post';
    } catch (error) {
        console.error('Error fetching Reddit title:', error);
        return 'Reddit post';
    }
}

// This function now just returns the URL as-is for non-Reddit links
export async function getOtherTitle(url: string): Promise<string> {
    return url;
} 