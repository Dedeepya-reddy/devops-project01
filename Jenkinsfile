
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

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
                    docker run -d --rm \
                      --name hello-devops-ci-${BUILD_NUMBER} \
                      -p 127.0.0.1:5002:5000 \
                      hello-devops:${BUILD_NUMBER}
                '''
                sh '''
                    trap 'docker stop hello-devops-ci-${BUILD_NUMBER} >/dev/null 2>&1 || true' EXIT

                    for i in $(seq 1 15); do
                        if curl -fsS http://127.0.0.1:5002/ -o response.txt; then
                            break
                        fi
                        sleep 2
                    done

                    grep -Fx 'Hello, Everyone! My first project is running.' response.txt
                '''
                echo 'Application test passed!'
            }
        }
    }
}


