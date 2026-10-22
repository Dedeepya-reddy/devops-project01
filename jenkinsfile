
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
    }
}

