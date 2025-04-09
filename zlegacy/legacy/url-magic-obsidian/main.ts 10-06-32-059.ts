import { App, Editor, MarkdownView, Modal, Notice, Plugin, PluginSettingTab, Setting } from 'obsidian';
import { getRedditTitle, getOtherTitle } from './urlProcessor';

interface URLMagicSettings {
    defaultFormat: 'plain' | 'bullet' | 'number';
    includeComments: boolean;
    maxComments: number;
}

const DEFAULT_SETTINGS: URLMagicSettings = {
    defaultFormat: 'bullet',
    includeComments: false,
    maxComments: 5
}

export default class URLMagicPlugin extends Plugin {
    settings: URLMagicSettings;

    async onload() {
        await this.loadSettings();

        // Add ribbon icon
        this.addRibbonIcon('link', 'URL Magic', () => {
            new URLMagicModal(this.app, this).open();
        });

        // Add command to process selected URLs
        this.addCommand({
            id: 'process-selected-urls',
            name: 'Process Selected URLs',
            editorCallback: (editor: Editor) => {
                const selectedText = editor.getSelection();
                if (selectedText) {
                    this.processSelectedText(editor, selectedText);
                }
            }
        });

        // Add settings tab
        this.addSettingTab(new URLMagicSettingTab(this.app, this));
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    async processSelectedText(editor: Editor, text: string) {
        const urls = this.extractUrls(text);
        if (urls.length === 0) {
            new Notice('No URLs found in selection');
            return;
        }

        const results = await Promise.all(
            urls.map(async (url) => {
                try {
                    const title = url.includes('reddit.com') 
                        ? await getRedditTitle(url)
                        : await getOtherTitle(url);
                    return { url, title };
                } catch (error) {
                    console.error(`Error processing ${url}:`, error);
                    return { url, title: `Error fetching title for ${url}` };
                }
            })
        );

        const markdown = this.formatResults(results);
        editor.replaceSelection(markdown);
    }

    extractUrls(text: string): string[] {
        const urlRegex = /(https?:\/\/[^\s<>",]+)/g;
        return text.match(urlRegex) || [];
    }

    formatResults(results: { url: string; title: string }[]): string {
        switch (this.settings.defaultFormat) {
            case 'bullet':
                return results.map(r => `- [${r.title}](${r.url})`).join('\n');
            case 'number':
                return results.map((r, i) => `${i + 1}. [${r.title}](${r.url})`).join('\n');
            default:
                return results.map(r => `[${r.title}](${r.url})`).join('\n');
        }
    }
}

class URLMagicModal extends Modal {
    plugin: URLMagicPlugin;

    constructor(app: App, plugin: URLMagicPlugin) {
        super(app);
        this.plugin = plugin;
    }

    onOpen() {
        const { contentEl } = this;
        contentEl.empty();

        contentEl.createEl('h2', { text: 'URL Magic ✨' });
        contentEl.createEl('p', { text: 'Paste your URLs (one per line):' });

        const textarea = contentEl.createEl('textarea', { attr: { rows: '6' } });
        textarea.style.width = '100%';
        textarea.style.marginBottom = '1rem';

        const buttonContainer = contentEl.createEl('div', { cls: 'button-container' });
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '1rem';
        buttonContainer.style.justifyContent = 'flex-end';

        const processButton = buttonContainer.createEl('button', { text: '✨ Process URLs' });
        processButton.addEventListener('click', async () => {
            const text = textarea.value;
            if (!text) {
                new Notice('Please enter some URLs');
                return;
            }

            const editor = this.app.workspace.getActiveViewOfType(MarkdownView)?.editor;
            if (!editor) {
                new Notice('Please open a markdown file');
                return;
            }

            await this.plugin.processSelectedText(editor, text);
            this.close();
        });
    }

    onClose() {
        const { contentEl } = this;
        contentEl.empty();
    }
}

class URLMagicSettingTab extends PluginSettingTab {
    plugin: URLMagicPlugin;

    constructor(app: App, plugin: URLMagicPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        const { containerEl } = this;
        containerEl.empty();

        containerEl.createEl('h2', { text: 'URL Magic Settings' });

        new Setting(containerEl)
            .setName('Default Format')
            .setDesc('Choose how your links will be formatted')
            .addDropdown(dropdown => dropdown
                .addOption('plain', 'Plain')
                .addOption('bullet', 'Bullet Points')
                .addOption('number', 'Numbered')
                .setValue(this.plugin.settings.defaultFormat)
                .onChange(async (value) => {
                    this.plugin.settings.defaultFormat = value as 'plain' | 'bullet' | 'number';
                    await this.plugin.saveSettings();
                }));

        new Setting(containerEl)
            .setName('Include Comments')
            .setDesc('Include Reddit post comments (if available)')
            .addToggle(toggle => toggle
                .setValue(this.plugin.settings.includeComments)
                .onChange(async (value) => {
                    this.plugin.settings.includeComments = value;
                    await this.plugin.saveSettings();
                }));

        new Setting(containerEl)
            .setName('Max Comments')
            .setDesc('Maximum number of comments to include')
            .addText(text => text
                .setValue(this.plugin.settings.maxComments.toString())
                .onChange(async (value) => {
                    this.plugin.settings.maxComments = parseInt(value) || 5;
                    await this.plugin.saveSettings();
                }));
    }
} 