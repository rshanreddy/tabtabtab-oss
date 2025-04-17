# Daily Digest Extension

An AI-powered content curator that helps you collect and analyze interesting content throughout your day. Perfect for researchers, analysts, and anyone who wants to keep track of important information they come across.

## Features

- **Smart Content Collection**: Automatically captures selected text and webpage context when you copy
- **Contextual Storage**: Saves URLs, titles, and timestamps with your content
- **AI-Powered Analysis**: Generates insightful summaries using Claude 3
- **Customizable Analysis**: Use your own prompt to focus on what matters to you
- **Daily Organization**: Content is organized by day for easy review

## Setup

1. **Install Dependencies**:
   ```bash
   pip install beautifulsoup4 aiohttp
   ```

2. **Configure Environment**:
   Create a `.env` file in your TabTabTab config directory with:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   DAILY_DIGEST_STORAGE_PATH=/path/to/storage/directory
   DAILY_DIGEST_PROMPT="""Your custom prompt here"""
   ```

3. **Add to TabTabTab**:
   - Open TabTabTab
   - Go to Menu -> Manage Extensions
   - Click "Add Local Extension"
   - Select this directory

## Usage

1. **Collecting Content**:
   - Select text on any webpage
   - Press `Option+C` to copy and save to digest
   - You'll get a notification confirming it's saved

2. **Getting Analysis**:
   - Press `Option+V` anywhere
   - The extension will analyze all content collected that day
   - Analysis includes:
     - Key themes
     - Important insights
     - Connections between pieces
     - Action items

3. **Customizing Analysis**:
   - Edit the `DAILY_DIGEST_PROMPT` in your `.env` file
   - Restart TabTabTab for changes to take effect

## Storage

Content is stored in JSON files organized by date:
```
daily_digest_data/
  digest_2025-04-16.json
  digest_2025-04-17.json
  ...
```

## Dependencies

- Anthropic API key (for Claude 3)
- Beautiful Soup 4 (for webpage parsing)
- aiohttp (for async web requests)

## Troubleshooting

1. **Content Not Saving**:
   - Check storage path in `.env`
   - Ensure directory exists and is writable

2. **Analysis Not Working**:
   - Verify Anthropic API key
   - Check internet connection
   - Look for error notifications

3. **Missing Context**:
   - Make sure you're copying from a webpage
   - Check if URL is accessible 