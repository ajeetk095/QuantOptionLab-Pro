# Deployment Guide — OptionLab Pro

## 1. GitHub
```bash
git init
git add .
git commit -m "Initial Commit — OptionLab Pro: Heston & Merton option pricing platform"
git branch -M main
git remote add origin REPOSITORY_URL
git push -u origin main
```
Version management: tag releases with `git tag v1.0.0 && git push --tags`, and use
GitHub Releases for portfolio showcase entries.

## 2. Streamlit Cloud
1. Go to share.streamlit.io → **New app**.
2. Connect your GitHub repository, select branch `main`, main file `app.py`.
3. Click **Deploy**. No secrets needed (no API keys used).
4. Update versions by pushing to `main` — auto redeploys.

## 3. Hugging Face Spaces
1. Create a Space → SDK: **Streamlit**.
2. Upload the repo files (or `git push` to the Space remote).
3. The Space runs `streamlit run app.py` automatically (see README app_port 8501).
4. Updates redeploy on push.

## 4. Railway
1. New Project → **Deploy from GitHub repo**.
2. Railway detects the `Procfile`; start command:
   `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. No environment variables required.

## 5. Render
1. New → **Web Service** → connect repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## 6. Docker
```bash
docker build -t optionlab-pro .
docker run -p 8501:8501 optionlab-pro
# open http://localhost:8501
```

## 7. Replit
1. Import the GitHub repo into Replit.
2. Add a `.replit` file: `run = "streamlit run app.py --server.port 8501 --server.address 0.0.0.0"`.
3. Run; the webview exposes port 8501.
