# 🚀 Deploy OpTrade to HuggingFace Spaces (Free & Permanent)

Follow these steps exactly. Total time: ~10 minutes. No credit card needed.

---

## Step 1 — Create a HuggingFace account

1. Go to **https://huggingface.co/join**
2. Enter your email, pick a username (e.g. `ibrahim-ai`), and create a password
3. Verify your email address

---

## Step 2 — Create a new Space

1. Log in to HuggingFace and click your profile picture (top right) → **New Space**
2. Fill in the form:
   - **Space name:** `optrade` (the URL will be `huggingface.co/YOUR_USERNAME/optrade`)
   - **License:** MIT
   - **SDK:** Select **Gradio**
   - **Space hardware:** CPU Basic *(free tier — enough for this app)*
3. Click **Create Space**

---

## Step 3 — Upload the files

You need to upload **these files and folders** from your `BIST_PROJECT` folder:

```
app.py
requirements.txt
README.md
backend/
  train_model.py
  cache/           ← create this empty folder (needed at runtime)
```

### Option A — Upload via the HuggingFace website (easiest)

1. On your Space page, click **Files** → **Add file** → **Upload files**
2. Upload `app.py`, `requirements.txt`, and `README.md` first
3. Then click **Add file** → **Upload files** again, and drag the entire `backend/` folder
4. Click **Commit changes**

### Option B — Upload via Git (for developers)

```bash
# Install git-lfs first (only needed once)
git lfs install

# Clone your new Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/optrade
cd optrade

# Copy files from BIST_PROJECT
cp /path/to/BIST_PROJECT/app.py .
cp /path/to/BIST_PROJECT/requirements.txt .
cp /path/to/BIST_PROJECT/README.md .
cp -r /path/to/BIST_PROJECT/backend ./backend

# Make sure the cache directory exists
mkdir -p backend/cache

# Push
git add .
git commit -m "Initial deployment"
git push
```

---

## Step 4 — Wait for the build

1. HuggingFace will now install packages from `requirements.txt` (takes 3–5 minutes on first deploy)
2. Watch the **Build** tab — you'll see logs as it installs TensorFlow, Gradio, etc.
3. When you see **Running**, your app is live! 🎉

---

## Step 5 — Visit your live app

Your app will be at:
```
https://huggingface.co/spaces/YOUR_USERNAME/optrade
```

Share this link with anyone — it works in any browser, no installation needed.

---

## ⚠️ Important notes

| Topic | Details |
|-------|---------|
| **Cold start** | HF Spaces "sleep" after inactivity. First visit after sleeping takes ~30 sec to wake up |
| **Analysis time** | First analysis of a stock takes 2–4 min (LSTM trains fresh). 2nd request uses cache = much faster |
| **Cache** | Cache is stored in `backend/cache/` inside the Space. It resets when the Space restarts |
| **Free limits** | CPU Basic tier has 16 GB RAM, 2 vCPUs. Enough for one user at a time |
| **Persistence** | The Space is permanent as long as your HF account is active |

---

## Upgrading hardware (optional)

If the app is slow, you can upgrade to a better CPU for ~$0.60/hr in Space Settings → Hardware.
You only pay while the Space is running (not while sleeping).

---

## Troubleshooting

**"Build failed — could not find tensorflow-cpu"**
→ Edit `requirements.txt`, change `tensorflow-cpu` to `tensorflow` and push again.

**"ModuleNotFoundError: No module named 'hmmlearn'"**
→ Make sure `requirements.txt` is in the root of the Space (same level as `app.py`).

**"train_model.py not found"**
→ Make sure `backend/train_model.py` was uploaded correctly (check Files tab on HF).

**Analysis returns "Could not download data"**
→ Yahoo Finance may be temporarily rate-limiting the HF server IP. Wait 2–3 minutes and retry.
