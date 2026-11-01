pipeline {
    agent any
    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    environment {
        IMAGE_NAME = 'skycast-weather'
        CONTAINER_NAME = 'skycast-weather'
        HOST_PORT = '5000'
    }
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Verify Tools') {
            steps {
                bat 'py --version'
                bat 'docker --version'
                bat 'docker info'
            }
        }
        stage('Install Dependencies') { steps { bat 'py -m pip install -r requirements.txt' } }
        stage('Unit Tests') { steps { bat 'py -m pytest -v' } }
        stage('Build Image') {
            steps { bat 'docker build --pull -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .' }
        }
        stage('Deploy Locally') {
            steps {
                bat '''
@echo off
docker rm -f %CONTAINER_NAME% 2>NUL
docker run -d --name %CONTAINER_NAME% --restart unless-stopped -p %HOST_PORT%:5000 %IMAGE_NAME%:%BUILD_NUMBER%
'''
            }
        }
        stage('Smoke Test') {
            steps {
                bat '''
@echo off
py -c "import time,urllib.request; time.sleep(4); u='http://127.0.0.1:%HOST_PORT%/health'; r=urllib.request.urlopen(u,timeout=10); b=r.read().decode(); print(b); assert r.status==200 and 'ok' in b"
'''
            }
        }
    }
    post {
        success { echo 'SkyCast tests, image build, deployment and smoke test succeeded.' }
        failure { echo 'Pipeline failed. Inspect the failed stage in Console Output.' }
        always { echo 'Pipeline finished.' }
    }
}
