# GitHub Codespaces Setup Guide

## Quick Start

1. **Open in Codespaces**
   - Go to your repository
   - Click `Code` → `Codespaces` → `Create codespace on main`
   - Wait for the environment to build (~3-5 minutes)

2. **Configure Environment Variables**
   ```bash
   # Copy the config template
   cp config.env.example config.env
   
   # Edit with your credentials
   code config.env
   ```

3. **Install Dependencies**
   - Dependencies are automatically installed via `postCreateCommand`
   - To reinstall manually: `pip install -r requirements.txt`

4. **Run the Bot**
   ```bash
   # Option 1: Using the run script
   bash run.sh
   
   # Option 2: Direct Python
   python3 update.py && python3 -m bot
   
   # Option 3: In debug mode
   python3 -m debugpy --listen 5678 -m bot
   ```

## Environment Variables Required

Add these to your `config.env`:

```
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
ADMIN=your_admin_id
LOG_CHANNEL=-100xxxxxxxxxx
DOWNLOAD_DIR=/tmp/downloads
MONGO_DB_URI=your_mongodb_uri
UPSTREAM_REPO=https://github.com/yourfork
UPSTREAM_BRANCH=main
```

## Features & Tools Pre-installed

### Extensions
- Python + Pylance (IntelliSense)
- Ruff (Fast Python linter)
- GitLens (Git integration)
- Makefile Tools

### System Tools
- FFmpeg & FFprobe (pre-installed)
- Git CLI
- GitHub CLI
- wget, curl, jq

### Forwarded Ports
- **Port 8080**: Bot API/Webhook
- **Port 5000**: Web Server

## Development Tips

### Debugging
```python
# Add breakpoints in your code
import debugpy
debugpy.listen(("0.0.0.0", 5678))
```

Then in VS Code Terminal:
```bash
python3 -m debugpy --listen 5678 -m bot
```

### File Storage
- Use `/tmp/downloads` for temporary files (cleaned on restart)
- Use `./data/` for persistent data within Codespace session
- **Note**: Files are lost when Codespace is deleted

### Monitor Logs
```bash
# Watch logs in real-time
tail -f log.txt

# Or in separate terminal
watch -n 1 tail -20 log.txt
```

### Database Connection
```bash
# Test MongoDB connection
python3 -c "from motor.motor_asyncio import AsyncIOMotorClient; print('MongoDB ready')"
```

## Common Commands

```bash
# Format code
black . --line-length 100

# Lint code
ruff check . --fix

# Run tests
python3 -m pytest

# Update dependencies
pip install --upgrade -r requirements.txt
```

## Limitations

⚠️ **Important:**
- Codespaces are temporary development environments
- Data is lost when Codespace is deleted
- Use for development/testing only, not for production
- Internet connectivity depends on GitHub
- Storage is limited (based on plan)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + ~` | Toggle Terminal |
| `Ctrl + Shift + P` | Command Palette |
| `F5` | Start Debugging |
| `Ctrl + K Ctrl + C` | Comment Selection |

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### FFmpeg not found
```bash
which ffmpeg
which ffprobe
# Should return /usr/local/bin/ffmpeg
```

### MongoDB connection fails
- Check `MONGO_DB_URI` in config.env
- Ensure your IP is whitelisted in MongoDB Atlas
- Test with: `python3 -c "import motor; print('OK')"`

### Port already in use
```bash
# Find and kill process
lsof -i :8080
kill -9 <PID>
```

### Codespace storage full
```bash
# Clean up
rm -rf .cache/ __pycache__ *.pyc
pip cache purge
```

## Persistence

To keep data between Codespace sessions:
1. Push code to GitHub
2. Use `.codespacerc` or settings sync
3. Or store data in MongoDB/external database

## Support

For issues:
- Check GitHub Codespaces docs: https://docs.github.com/en/codespaces
- Check devcontainer docs: https://containers.dev/
