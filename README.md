‎# 🚀 Bot Hosting Guide — কোথায় ও কিভাবে Run করবে
‎
‎---
‎
‎## 📸 Photo Banner Setup
‎
‎`bot.py` ফাইলে এই line টা খোঁজো:
‎
‎```python
‎BANNER_URL = "https://i.imgur.com/YOUR_IMAGE.jpg"
‎```
‎
‎তোমার photo URL দিয়ে replace করো। Free image hosting:
‎- **imgur.com** → Upload করো → Direct link copy করো (`.jpg` বা `.png` দিয়ে শেষ)
‎- **telegra.ph** → Upload করো → URL copy করো
‎- **postimg.cc** → Free hosting
‎
‎---
‎
‎## 🔑 Bot Token Setup
‎
‎```python
‎TOKEN = "YOUR_BOT_TOKEN_HERE"
‎```
‎
‎@BotFather থেকে পাওয়া token দাও।
‎
‎---
‎
‎## 🏠 Option 1: নিজের PC/Laptop-এ Run করো
‎
‎**শুধু test করার জন্য ভালো। PC বন্ধ হলে bot বন্ধ।**
‎
‎```bash
‎# Step 1: Install
‎pip install python-telegram-bot==20.7
‎
‎# Step 2: Run
‎python bot.py
‎```
‎
‎---
‎
‎## ☁️ Option 2: Koyeb (সবচেয়ে সহজ — FREE)
‎
‎**24/7 চলবে, কোনো Credit Card লাগবে না।**
‎
‎1. **koyeb.com** এ account খোলো (GitHub দিয়ে login করো)
‎2. "Create App" → "Docker" বা "Git" select করো
‎3. তোমার bot files GitHub-এ upload করো
‎4. Koyeb-এ connect করো
‎5. Environment variable-এ `TOKEN` দাও
‎6. Deploy করো ✅
‎
‎---
‎
‎## ☁️ Option 3: Railway (সহজ — FREE tier আছে)
‎
‎1. **railway.app** এ account খোলো
‎2. "New Project" → "Deploy from GitHub"
‎3. তোমার bot repository select করো
‎4. Environment variables-এ add করো:
‎   ```
‎   TOKEN = তোমার_bot_token
‎   ```
‎5. Deploy করো ✅
‎
‎Railway-তে **`Procfile`** বানাও:
‎```
‎worker: python bot.py
‎```
‎
‎---
‎
‎## ☁️ Option 4: Render (FREE — popular)
‎
‎1. **render.com** এ account খোলো
‎2. "New" → "Background Worker"
‎3. GitHub repo connect করো
‎4. Build Command: `pip install -r requirements.txt`
‎5. Start Command: `python bot.py`
‎6. Environment-এ TOKEN দাও
‎7. Deploy করো ✅
‎
‎---
‎
‎## ☁️ Option 5: VPS (সবচেয়ে Professional)
‎
‎**DigitalOcean, Vultr, Contabo** — মাসে $4-6
‎
‎```bash
‎# Server-এ SSH করে ঢোকো তারপর:
‎sudo apt update && sudo apt install python3-pip -y
‎pip3 install python-telegram-bot==20.7
‎
‎# Screen দিয়ে background-এ চালাও (বন্ধ হবে না)
‎sudo apt install screen -y
‎screen -S mybot
‎python3 bot.py
‎
‎# Ctrl+A তারপর D চাপলে background-এ চলবে
‎# ফিরে আসতে: screen -r mybot
‎```
‎
‎---
‎
‎## 📁 GitHub-এ Upload করার নিয়ম
‎
‎```
‎তোমার_repo/
‎├── bot.py
‎├── requirements.txt
‎└── Procfile          ← Railway/Render এর জন্য
‎```
‎
‎**Procfile এর ভেতরে লেখো:**
‎```
‎worker: python bot.py
‎```
‎
‎---
‎
‎## 🎯 Recommendation
‎
‎| Platform | Cost | সহজ? | 24/7? |
‎|----------|------|-------|-------|
‎| নিজের PC | Free | ✅ | ❌ |
‎| Koyeb | Free | ✅✅ | ✅ |
‎| Railway | Free tier | ✅✅ | ✅ |
‎| Render | Free | ✅✅ | ✅ |
‎| VPS | $4-6/mo | ❌ কঠিন | ✅✅ |
‎
‎**শুরুতে Railway বা Render use করো — সবচেয়ে সহজ এবং free!**
‎
