
pipeline {
    agent any

    stages {
        stage('Check Project Files') {
            steps {
                sh 'test -f app.py'
                sh 'test -f requirements.txt'
                sh 'test -f Dockerfile'
                echo 'All required project files exist!'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t hello-devops:${BUILD_NUMBER} .'
            }
        }

        stage('Test Application') {
            steps {
                sh '''
                    set -eu

                    APP_CONTAINER="hello-devops-ci-${BUILD_NUMBER}"
                    TEST_NETWORK="jenkins"

                    cleanup() {
                        docker rm -f "$APP_CONTAINER" >/dev/null 2>&1 || true
                    }
                    trap cleanup EXIT

                    docker run -d \
                        --name "$APP_CONTAINER" \
                        --network "$TEST_NETWORK" \
                        hello-devops:${BUILD_NUMBER}

                    docker run --rm \
                        --network "$TEST_NETWORK" \
                        curlimages/curl:latest \
                        -fsS --retry 10 --retry-connrefused --retry-delay 2 \
                        "http://${APP_CONTAINER}:5000/" \
                        -o /tmp/response.txt

                    grep -Fx \
                        'Hello, Everyone! My first project is running.' \
                        /tmp/response.txt

                    echo 'Application test passed!'
                '''
            }
        }
    }
}

