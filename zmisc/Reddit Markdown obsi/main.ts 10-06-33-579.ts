import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting } from 'obsidian';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);

interface RedditMarkdownLinkSettings {
    pythonPath: string;
}

const DEFAULT_SETTINGS: RedditMarkdownLinkSettings = {
    pythonPath: 'python3'
}

export default class RedditMarkdownLink extends Plugin {
    settings: RedditMarkdownLinkSettings;

    async onload() {
        await this.loadSettings();

        // Add a command to convert Reddit links
        this.addCommand({
            id: 'convert-reddit-links',
            name: 'Convert Links to Markdown',
            editorCallback: (editor: Editor) => this.convertLinks(editor)
        });

        // Add settings tab
        this.addSettingTab(new RedditMarkdownLinkSettingTab(this.app, this));
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    async convertLinks(editor: Editor) {
        const content = editor.getValue();
        // Match any URL in the content
        const urlRegex = /https?:\/\/[^\s)]+/g;
        const urls = content.match(urlRegex) || [];
        
        try {
            // Get the current working directory
            const { stdout: cwd } = await execAsync('pwd');
            const pluginDir = cwd.trim();
            const scriptPath = path.join(pluginDir, 'reddit_link_converter.py');
            
            // Check if Python script exists
            if (!fs.existsSync(scriptPath)) {
                throw new Error(`Python script not found at: ${scriptPath}`);
            }

            // Create a temporary file with the URLs
            const tempFile = path.join(pluginDir, 'urls.json');
            fs.writeFileSync(tempFile, JSON.stringify(urls));

            // Run the Python script
            const { stdout } = await execAsync(`${this.settings.pythonPath} "${scriptPath}" < "${tempFile}"`);

            // Clean up temp file
            fs.unlinkSync(tempFile);

            // Parse the results
            const results = JSON.parse(stdout);
            
            // Create markdown list
            const markdownList = results.map((result: { url: string, title: string }) => 
                `- [${result.title}](${result.url})`
            ).join('\n');

            // Update the editor content
            editor.setValue(markdownList);
        } catch (error) {
            console.error('Error running Python script:', error);
            new Notice('Error converting links. Check console for details.');
        }
    }
}

class RedditMarkdownLinkSettingTab extends PluginSettingTab {
    plugin: RedditMarkdownLink;

    constructor(app: App, plugin: RedditMarkdownLink) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        const {containerEl} = this;
        containerEl.empty();

        containerEl.createEl('h2', {text: 'Reddit Markdown Link Settings'});

        new Setting(containerEl)
            .setName('Python Path')
            .setDesc('Path to Python executable (e.g., python3)')
            .addText(text => text
                .setValue(this.plugin.settings.pythonPath)
                .onChange(async (value) => {
                    this.plugin.settings.pythonPath = value;
                    await this.plugin.saveSettings();
                }));
    }
} 