
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        PYTHON_EXE = 'C:\\Users\\manas\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
        IMAGE_NAME = 'skycast-weather'
        CONTAINER_NAME = 'skycast-weather'
        HOST_PORT = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Tools') {
            steps {
                bat '"%PYTHON_EXE%" --version'
                bat 'git --version'
                bat 'docker --version'
                bat 'docker info'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                @echo off
                if not exist .venv\\Scripts\\python.exe (
                    "%PYTHON_EXE%" -m venv .venv
                )
                if errorlevel 1 exit /b 1

                ".venv\\Scripts\\python.exe" -m pip install -r requirements.txt
                if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                bat '".venv\\Scripts\\python.exe" -m pytest -v'
            }
        }

        stage('Build Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
                bat 'docker tag %IMAGE_NAME%:%BUILD_NUMBER% %IMAGE_NAME%:latest'
            }
        }

        stage('Deploy Locally') {
            steps {
                bat '''
                @echo off
                docker rm -f %CONTAINER_NAME% >NUL 2>&1
                docker run -d --name %CONTAINER_NAME% --restart unless-stopped -p %HOST_PORT%:5000 %IMAGE_NAME%:%BUILD_NUMBER%
                if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                bat '''
                @echo off
                powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Start-Sleep -Seconds 5; $r=Invoke-RestMethod 'http://127.0.0.1:%HOST_PORT%/health'; if ($r.status -ne 'ok') { throw 'Health check failed' }; Write-Host 'Health check passed'"
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed and SkyCast was deployed locally.'
        }
        failure {
            echo 'FAILURE: Check the first failed stage in Console Output.'
        }
    }
}
