pipeline {
    agent any

    environment {
        IMAGE_NAME       = 'inventory_api_project-api'
        NETWORK_NAME     = 'inventory-net'
        MONGO_CONTAINER  = 'inventory-mongo-container'
        API_CONTAINER    = 'inventory-api-container'
        MONGO_URI        = 'mongodb://inventory-mongo-container:27017'
        API_BASE_URL     = 'http://inventory-api-container:8000'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }

        stage('Build Docker Ubuntu Image') {
            steps {
                echo 'Building Docker image...'
                bat 'docker build -t %IMAGE_NAME% .'
            }
        }

        stage('Create Docker Network and MongoDB') {
            steps {
                echo 'Creating Docker network...'
                bat 'docker network inspect %NETWORK_NAME% >nul 2>nul || docker network create %NETWORK_NAME%'

                echo 'Removing old containers if they exist...'
                bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
                bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'

                echo 'Starting MongoDB container...'
                bat 'docker run -d --name %MONGO_CONTAINER% --network %NETWORK_NAME% mongo:7'

                echo 'Waiting for MongoDB to start...'
                bat 'powershell -Command "Start-Sleep -Seconds 10"'
            }
        }

        stage('Import CSV into MongoDB') {
            steps {
                echo 'Importing CSV into MongoDB inside Docker...'
                bat '''
                docker run --rm ^
                  --network %NETWORK_NAME% ^
                  -e MONGO_URI=%MONGO_URI% ^
                  %IMAGE_NAME% ^
                  python3 scripts/import_csv_to_mongo.py ^
                  --csv data/products.csv ^
                  --json /tmp/products.json ^
                  --mongo-uri %MONGO_URI%
                '''
            }
        }

        stage('Run API Container in Background') {
            steps {
                echo 'Starting API container...'
                bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'

                bat '''
                docker run -d ^
                  --name %API_CONTAINER% ^
                  --network %NETWORK_NAME% ^
                  -p 8000:8000 ^
                  -e MONGO_URI=%MONGO_URI% ^
                  %IMAGE_NAME%
                '''

                echo 'Waiting for API to start...'
                bat 'powershell -Command "Start-Sleep -Seconds 15"'

                echo 'Showing API container logs...'
                bat 'docker logs %API_CONTAINER%'
            }
        }

        stage('Run Python Unit Tests') {
            steps {
                echo 'Running pytest inside Docker...'
                bat '''
                docker run --rm ^
                  --network %NETWORK_NAME% ^
                  -e MONGO_URI=%MONGO_URI% ^
                  %IMAGE_NAME% ^
                  pytest -v
                '''
            }
        }

        stage('Run Newman Tests') {
            steps {
                echo 'Running Newman tests inside Docker...'
                bat '''
                docker run --rm ^
                  --network %NETWORK_NAME% ^
                  -v "%cd%:/etc/newman" ^
                  postman/newman:alpine run /etc/newman/postman_collection.json ^
                  --env-var base_url=%API_BASE_URL%
                '''
            }
        }

        stage('Generate README from FastAPI OpenAPI') {
            steps {
                echo 'Generating README/OpenAPI output...'
                bat '''
                if not exist generated mkdir generated
                curl %API_BASE_URL%/openapi.json -o generated\\openapi.json
                '''
            }
        }

        stage('Create Final Zip') {
            steps {
                echo 'Preparing submission folder...'
                bat '''
                if exist submission rmdir /s /q submission
                mkdir submission

                if exist app xcopy app submission\\app /E /I /Y
                if exist scripts xcopy scripts submission\\scripts /E /I /Y
                if exist tests xcopy tests submission\\tests /E /I /Y
                if exist data xcopy data submission\\data /E /I /Y
                if exist postman xcopy postman submission\\postman /E /I /Y
                if exist generated xcopy generated submission\\generated /E /I /Y

                if exist Dockerfile copy Dockerfile submission\\Dockerfile
                if exist Jenkinsfile copy Jenkinsfile submission\\Jenkinsfile
                if exist requirements.txt copy requirements.txt submission\\requirements.txt
                if exist README.md copy README.md submission\\README.md
                if exist postman_collection.json copy postman_collection.json submission\\postman_collection.json
                if exist .env.example copy .env.example submission\\.env.example
                '''

                echo 'Creating ZIP file...'
                bat 'powershell -Command "Compress-Archive -Path submission\\* -DestinationPath submission.zip -Force"'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up containers and network...'
            bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker network rm %NETWORK_NAME% >nul 2>nul || exit /b 0'

            archiveArtifacts artifacts: 'submission.zip', fingerprint: true, onlyIfSuccessful: false
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the stage logs above.'
        }
    }
}