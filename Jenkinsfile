pipeline {
    agent any

    environment {
        APP_IMAGE = 'inventory_api_project-api'
        APP_CONTAINER = 'inventory-api-container'
        MONGO_CONTAINER = 'inventory-mongo-container'
        NETWORK_NAME = 'inventory-net'
        MONGO_URI = 'mongodb://inventory-mongo-container:27017'
    }

    stages {
        stage('Build Docker Ubuntu Image') {
            steps {
                bat 'docker build -t %APP_IMAGE% .'
            }
        }

        stage('Create Docker Network and MongoDB') {
            steps {
                bat 'docker network create %NETWORK_NAME% || exit /b 0'
                bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
                bat 'docker run -d --name %MONGO_CONTAINER% --network %NETWORK_NAME% mongo:7'
                bat 'timeout /t 10'
            }
        }

        stage('Import CSV into MongoDB') {
            steps {
                bat 'python scripts\\import_csv_to_mongo.py --csv data\\products.csv --json data\\products.json --mongo-uri %MONGO_URI%'
            }
        }

        stage('Run API Container in Background') {
            steps {
                bat 'docker rm -f %APP_CONTAINER% >nul 2>nul || exit /b 0'
                bat 'docker run -d --name %APP_CONTAINER% --network %NETWORK_NAME% -e MONGO_URI=%MONGO_URI% -p 8000:8000 %APP_IMAGE%'
                bat 'timeout /t 15'
            }
        }

        stage('Run Python Unit Tests') {
            steps {
                bat 'set PYTHONPATH=. && pytest'
            }
        }

        stage('Run Newman Tests') {
            steps {
                bat 'newman run postman\\inventory_api.postman_collection.json --env-var baseUrl=http://127.0.0.1:8000'
            }
        }

        stage('Generate README from FastAPI OpenAPI') {
            steps {
                bat 'python scripts\\generate_readme.py'
            }
        }

        stage('Create Final Zip') {
            steps {
                bat 'powershell -Command "$ts = Get-Date -Format ''yyyyMMdd-HHmmss''; Compress-Archive -Path app,data,docker-compose.yml,Dockerfile,Jenkinsfile,monitoring,postman,requirements.txt,scripts,tests,README.txt -DestinationPath (''complete-'' + $ts + ''.zip'') -Force"'
            }
        }
    }

    post {
        always {
            bat 'docker rm -f %APP_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker network rm %NETWORK_NAME% >nul 2>nul || exit /b 0'
            archiveArtifacts artifacts: 'README.txt, complete-*.zip', fingerprint: true
        }
    }
}