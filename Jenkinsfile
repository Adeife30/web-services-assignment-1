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
                checkout scm
            }
        }

        stage('Build Docker Ubuntu Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME% .'
            }
        }

        stage('Create Docker Network and MongoDB') {
            steps {
                bat 'docker network inspect %NETWORK_NAME% >nul 2>nul || docker network create %NETWORK_NAME%'
                bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
                bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'
                bat 'docker run -d --name %MONGO_CONTAINER% --network %NETWORK_NAME% mongo:7'
                bat 'powershell -Command "Start-Sleep -Seconds 10"'
            }
        }

        stage('Import CSV into MongoDB') {
            steps {
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
                bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'
                bat '''
                docker run -d ^
                  --name %API_CONTAINER% ^
                  --network %NETWORK_NAME% ^
                  -e MONGO_URI=%MONGO_URI% ^
                  %IMAGE_NAME%
                '''
                bat 'powershell -Command "Start-Sleep -Seconds 15"'
                bat 'docker logs %API_CONTAINER%'
            }
        }

        stage('Run Python Unit Tests') {
            steps {
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
                script {
                    def collectionPath = powershell(
                        returnStdout: true,
                        script: '''
$files = Get-ChildItem -Path . -Recurse -File | Where-Object {
    $_.Name -like "*postman_collection*.json" -or $_.Name -like "*collection*.json"
}

if (-not $files) {
    Write-Error "No Postman collection JSON file found in repo."
    exit 1
}

$relative = Resolve-Path -Relative $files[0].FullName
$relative = $relative -replace "^\\.\\\\", ""
$relative = $relative -replace "\\\\", "/"
Write-Output $relative
'''
                    ).trim()

                    echo "Using Postman collection: ${collectionPath}"

                    bat """
                    docker run --rm ^
                      --network %NETWORK_NAME% ^
                      -v "%cd%:/etc/newman" ^
                      postman/newman:alpine run /etc/newman/${collectionPath} ^
                      --env-var base_url=%API_BASE_URL%
                    """
                }
            }
        }

        stage('Generate README from FastAPI OpenAPI') {
            steps {
                bat '''
                if not exist generated mkdir generated
                docker run --rm ^
                  --network %NETWORK_NAME% ^
                  -v "%cd%\\generated:/output" ^
                  %IMAGE_NAME% ^
                  sh -c "curl -s %API_BASE_URL%/openapi.json -o /output/openapi.json"
                '''
            }
        }

        stage('Create Final Zip') {
            steps {
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

                bat 'powershell -Command "Compress-Archive -Path submission\\* -DestinationPath submission.zip -Force"'
            }
        }
    }

    post {
        always {
            bat 'docker rm -f %API_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker rm -f %MONGO_CONTAINER% >nul 2>nul || exit /b 0'
            bat 'docker network rm %NETWORK_NAME% >nul 2>nul || exit /b 0'
            archiveArtifacts artifacts: 'submission.zip', fingerprint: true, onlyIfSuccessful: false
        }
    }
}