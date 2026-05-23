# 🚀 PROJECT STARTUP SCRIPTS - USAGE GUIDE

## 📁 Available Scripts (3 Options)

Aapke paas **3 different startup scripts** hain. Choose karein based on your need:

---

## 1️⃣ **RUN_PROJECT_SMART.bat** (RECOMMENDED) ⭐

**Best for:** First time use, testing, or when you want detailed info

### Features:
- ✅ Pre-flight checks (Python, files, etc.)
- ✅ Optional test suite execution
- ✅ Detailed status messages
- ✅ Error handling and verification
- ✅ Port cleanup
- ✅ Service health checks
- ✅ Colored output
- ✅ Graceful shutdown option

### Usage:
```cmd
RUN_PROJECT_SMART.bat
```

### When to Use:
- ✅ First time running the project
- ✅ After making changes
- ✅ When debugging issues
- ✅ When you want to see what's happening
- ✅ When you want to run tests first

### Output:
```
╔════════════════════════════════════════╗
║  JUNE VA + TALKINGHEAD STARTER         ║
╚════════════════════════════════════════╝

PRE-FLIGHT CHECKS
✅ Python installed
✅ All critical files found
✅ Enhanced config available

OPTIONAL: Run tests? (Y/N)
...
```

---

## 2️⃣ **RUN_COMPLETE_PROJECT.bat** (DETAILED)

**Best for:** When you want detailed logs and information

### Features:
- ✅ Port cleanup
- ✅ Step-by-step progress
- ✅ Service status display
- ✅ Helpful instructions
- ✅ Error messages
- ✅ Manual shutdown control

### Usage:
```cmd
RUN_COMPLETE_PROJECT.bat
```

### When to Use:
- ✅ Daily use with detailed output
- ✅ When you want to see all steps
- ✅ When troubleshooting
- ✅ When teaching someone

### Output:
```
========================================
[STEP 1/5] Cleaning up...
✅ Cleanup complete

[STEP 2/5] Starting Bridge Server...
✅ Bridge Server started

[STEP 3/5] Starting TalkingHead...
✅ TalkingHead started
...
```

---

## 3️⃣ **RUN_QUICK.bat** (FASTEST) ⚡

**Best for:** Daily use when everything is working fine

### Features:
- ✅ Minimal output
- ✅ Fast startup
- ✅ Automatic cleanup
- ✅ Auto-selects enhanced config
- ✅ No questions asked

### Usage:
```cmd
RUN_QUICK.bat
```

### When to Use:
- ✅ Daily quick starts
- ✅ When everything is set up
- ✅ When you want no delays
- ✅ When you don't need detailed output

### Output:
```
Starting June VA...
[system]> Listening for sound...
```

---

## 📊 Comparison

| Feature | SMART | COMPLETE | QUICK |
|---------|-------|----------|-------|
| **Startup Time** | 15-20s | 10-15s | 5-10s |
| **Pre-flight Checks** | ✅ Yes | ⚠️ Basic | ❌ No |
| **Test Suite Option** | ✅ Yes | ❌ No | ❌ No |
| **Detailed Output** | ✅✅✅ | ✅✅ | ✅ |
| **Error Messages** | ✅✅✅ | ✅✅ | ❌ |
| **Service Verification** | ✅ Yes | ⚠️ Basic | ❌ No |
| **Graceful Shutdown** | ✅ Yes | ✅ Yes | ✅ Auto |
| **Best For** | First time | Daily detailed | Daily quick |

---

## 🎯 Which One to Use?

### **Starting Out? → Use SMART** ⭐
```cmd
RUN_PROJECT_SMART.bat
```
- Runs tests
- Checks everything
- Guides you through

### **Daily Use? → Use QUICK** ⚡
```cmd
RUN_QUICK.bat
```
- Fast startup
- No questions
- Just works

### **Need Details? → Use COMPLETE** 📋
```cmd
RUN_COMPLETE_PROJECT.bat
```
- See all steps
- Detailed logging
- Full control

---

## 🛠️ What Each Script Does

### All Scripts:
1. ✅ Change to project directory
2. ✅ Kill old processes on ports 8765, 8001, 8080
3. ✅ Start Bridge Server (WebSocket)
4. ✅ Start TalkingHead (HTTP server)
5. ✅ Open browser (http://localhost:8080)
6. ✅ Start June VA (Voice Assistant)
7. ✅ Cleanup on exit

### Additionally SMART does:
- ✅ Check Python installation
- ✅ Verify all required files exist
- ✅ Optional test suite execution
- ✅ Service health verification
- ✅ Interactive shutdown choice

### Additionally COMPLETE does:
- ✅ Detailed step-by-step output
- ✅ Usage instructions
- ✅ Port status display
- ✅ Config file detection

---

## 🚨 Troubleshooting

### Script doesn't start?
**Solution:**
1. Right-click the .bat file
2. Select "Run as Administrator"

### Port already in use?
**Solution:**
- Scripts automatically kill old processes
- If manual cleanup needed:
```cmd
netstat -ano | findstr ":8765"
taskkill /PID <PID_NUMBER> /F
```

### Bridge Server fails?
**Solution:**
1. Check Bridge Server window for errors
2. Verify `bridge_server.py` exists
3. Check Python dependencies:
```cmd
pip install websockets
```

### TalkingHead not loading?
**Solution:**
1. Check TalkingHead window for errors
2. Verify `TalkingHead/index.html` exists
3. Clear browser cache

### June VA fails?
**Solution:**
1. Check Google Cloud credentials
2. Verify config file exists
3. Check dependencies:
```cmd
cd june
pip install -r requirements.txt
```

---

## 📝 Notes

### Config Selection:
- If `config-enhanced-multilingual.json` exists → Uses Enhanced
- Otherwise → Uses `config.json`
- **Enhanced** is better for Hindi/Hinglish

### Credentials:
- Looks for `vaani-474822-49ec0963711e.json`
- Sets `GOOGLE_APPLICATION_CREDENTIALS` automatically
- If not found, uses environment variable

### Cleanup:
- **SMART**: Asks before closing all services
- **COMPLETE**: Asks before closing all services
- **QUICK**: Automatically closes all services

---

## 🎉 Quick Reference

### First Time:
```cmd
RUN_PROJECT_SMART.bat
```

### Daily Use:
```cmd
RUN_QUICK.bat
```

### Debugging:
```cmd
RUN_PROJECT_SMART.bat
```
(Choose Y for tests)

### Demo/Teaching:
```cmd
RUN_COMPLETE_PROJECT.bat
```

---

## ✅ Checklist Before Running

- [ ] Python 3.8+ installed?
- [ ] In correct directory (Avatar folder)?
- [ ] `bridge_server.py` exists?
- [ ] `TalkingHead` folder exists?
- [ ] `june` folder exists?
- [ ] Google Cloud credentials available?
- [ ] Ports 8765, 8001, 8080 free?

**All good? → Run any script!** 🚀

---

## 🌟 Recommended Workflow

### Monday Morning (First of Week):
```cmd
RUN_PROJECT_SMART.bat
```
(Run tests to ensure everything is working)

### Daily Use:
```cmd
RUN_QUICK.bat
```
(Fast and simple)

### After Updates:
```cmd
RUN_PROJECT_SMART.bat
```
(Verify changes)

---

**Happy coding! 🎉 Enjoy your Voice Assistant! 🗣️🎭**
