# URL Magic for Obsidian

A simple Obsidian plugin that helps you fetch titles from URLs and format them in markdown. Perfect for creating reading lists, reference collections, or just organizing your links.

## Features

- Fetch titles from any URL
- Special handling for Reddit posts (includes subreddit name)
- Multiple output formats (plain, bullet points, numbered list)
- Works with both selected text and a modal input
- Dark mode support
- Settings customization

## Installation

1. Download the latest release from the releases page
2. Extract the zip file into your Obsidian plugins folder:
   - Windows: `%APPDATA%\Obsidian\plugins\`
   - macOS: `~/Library/Application Support/Obsidian/plugins/`
   - Linux: `~/.config/Obsidian/plugins/`
3. Enable the plugin in Obsidian settings

## Usage

1. Select text containing URLs or use the ribbon icon
2. Choose your preferred output format in settings
3. The plugin will fetch titles and format them in markdown

## Settings

- **Default Format**: Choose between plain text, bullet points, or numbered list
- **Include Comments**: Option to include Reddit post comments
- **Max Comments**: Maximum number of comments to include

## Development

To build the plugin:

```bash
npm install
npm run build
```

For development:

```bash
npm run dev
```

## License

MIT License - feel free to use this plugin as you wish! 