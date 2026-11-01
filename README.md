# SkyCast — Weather Intelligence + DevOps CI/CD
Responsive Flask weather app using Open-Meteo APIs, Docker, and a Jenkins Pipeline.

## Features
- Current weather and five-day forecast by city
- Error handling, `/health`, Docker health check, non-root runtime
- Offline-safe pytest tests for app routes and provider errors
- Jenkins checkout → tools → dependencies → tests → image build → deploy → smoke test

## Prerequisites
Windows, Python 3.12+, Git, Docker Desktop, Jenkins agent able to run `py` and `docker`.

## Run locally
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m pytest -v
py app.py
```
Open http://127.0.0.1:5000. If activation is blocked, install dependencies with `py -m pip install -r requirements.txt` without activating the venv.

## Docker
```powershell
docker version
docker build -t skycast-weather:latest .
docker run -d --name skycast-weather -p 5000:5000 skycast-weather:latest
docker ps
Invoke-RestMethod http://127.0.0.1:5000/health
docker inspect --format='{{.State.Health.Status}}' skycast-weather
```
Stop: `docker rm -f skycast-weather`. If port 5000 is busy, map `-p 5001:5000`.

## GitHub
Create an empty repository named `skycast-weather-devops`, then run in the project directory:
```powershell
git init
git add .
git commit -m "Build SkyCast weather app with Docker and Jenkins CI/CD"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/skycast-weather-devops.git
git push -u origin main
```
Replace `YOUR-USERNAME`. Never commit tokens, passwords or `.env` files.

## Jenkins setup
1. Start Docker Desktop and confirm `docker info` works.
2. Ensure `py --version` works for the Windows account that runs the Jenkins agent.
3. Jenkins → New Item → `SkyCast-CI-CD` → Pipeline.
4. Pipeline Definition: **Pipeline script from SCM**, SCM Git, repository URL, branch `*/main`, script path `Jenkinsfile`.
5. Save → Build Now → Console Output.
The Jenkinsfile uses Windows `bat` steps. Jenkins may run as a different service account than your desktop login; that account/agent must have Docker engine permissions and Python on PATH.

A GitHub webhook requires Jenkins to be reachable from GitHub. A localhost-only server cannot receive internet webhooks, so use manual builds for a local-only setup. Never expose unsecured Jenkins publicly.

The pipeline tags the image with the Jenkins build number and `latest`, replaces the local container, and checks `/health`. It does not push to a registry or publish the application publicly.

Weather data is provided by Open-Meteo. Review current terms and attribution rules before commercial use.

## GitHub Webhook CI/CD Test
