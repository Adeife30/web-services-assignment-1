pipeline {
    agent any

    environment {
        IMAGE_NAME = 'inventory-api-image'
        API_CONTAINER = 'inventory-api-container'
        MONGO_CONTAINER = 'inventory-mongo-container'
        DOCKER_NETWORK = 'inventory-net'
        ZIP_STAMP = "${new Date().format('yyyy-MM-dd-HHmmss')}"
    }

    stages {
        stage('Clone from GitHub') {
            steps {
                git url: 'https://github.com/YOUR_USERNAME/inventory-management-api.git', branch: 'main'
            }
        }

        stage('Build Docker Ubuntu Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME% .'
            }
        }

        stage('Create Docker Network and MongoDB') {
            steps {
                bat 'docker network inspect %DOCKER_NETWORK% >nul 2>nul || docker network create %DOCKER_NETWORK%'
                bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
                bat 'docker run -d --name %MONGO_CONTAINER% --network %DOCKER_NETWORK% mongo:7'
            }
        }

        stage('Import CSV into MongoDB') {
            steps {
                bat 'docker run --rm --network %DOCKER_NETWORK% -e MONGO_URI=mongodb://%MONGO_CONTAINER%:27017 -e MONGO_DB_NAME=inventory_db -e MONGO_COLLECTION_NAME=products %IMAGE_NAME% python3 scripts/import_csv_to_mongo.py --csv /app/data/products.csv --json /app/data/products.json'
            }
        }

        stage('Run API Container in Background') {
            steps {
                bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'
                bat 'docker run -d --name %API_CONTAINER% --network %DOCKER_NETWORK% -p 8000:8000 -e MONGO_URI=mongodb://%MONGO_CONTAINER%:27017 -e MONGO_DB_NAME=inventory_db -e MONGO_COLLECTION_NAME=products %IMAGE_NAME%'
                bat 'timeout /t 10 >nul'
            }
        }

        stage('Run Python Unit Tests') {
            steps {
                bat 'pytest -v tests'
            }
        }

        stage('Run Newman Tests') {
            steps {
                bat 'newman run postman/inventory_api.postman_collection.json --environment postman/inventory_api.postman_environment.json'
            }
        }

        stage('Generate README from FastAPI OpenAPI') {
            steps {
                bat 'curl http://localhost:8000/openapi.json -o openapi.json'
                bat 'python scripts/generate_readme.py openapi.json README.txt'
            }
        }

        stage('Create Final Zip') {
            steps {
                powershell 'Compress-Archive -Path app,tests,scripts,postman,data,Dockerfile,docker-compose.yml,Jenkinsfile,requirements.txt,README.txt -DestinationPath complete-$env:ZIP_STAMP.zip -Force'
            }
        }
    }

    post {
        always {
            bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker network rm %DOCKER_NETWORK% >nul 2>nul || exit /b 0'
            archiveArtifacts artifacts: 'complete-*.zip, README.txt', fingerprint: true
        }
    }
}
