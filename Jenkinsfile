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

                    echo "Starting application container..."
                    docker run -d \
                        --name "$APP_CONTAINER" \
                        --network "$TEST_NETWORK" \
                        hello-devops:${BUILD_NUMBER}

                    ATTEMPT=1
                    RESPONSE=""

                    while [ "$ATTEMPT" -le 15 ]; do
                        if RESPONSE=$(docker run --rm \
                            --network "$TEST_NETWORK" \
                            curlimages/curl:latest \
                            -fsS --connect-timeout 2 \
                            "http://${APP_CONTAINER}:5000/" \
                            2>/dev/null); then
                            break
                        fi

                        if [ "$ATTEMPT" -eq 15 ]; then
                            echo "Application did not become ready."
                            docker logs "$APP_CONTAINER"
                            exit 1
                        fi

                        ATTEMPT=$((ATTEMPT + 1))
                        sleep 2
                    done

                    EXPECTED="Hello, Everyone! My first project is running."
                    echo "Application response: $RESPONSE"

                    if [ "$RESPONSE" != "$EXPECTED" ]; then
                        echo "Application test failed!"
                        exit 1
                    fi

                    echo "Application test passed!"
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                    set -eu

                    REGISTRY_IMAGE="host.docker.internal:5001/hello-devops:${BUILD_NUMBER}"

                    docker tag "hello-devops:${BUILD_NUMBER}" "$REGISTRY_IMAGE"
                    docker push "$REGISTRY_IMAGE"
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'kubernetes-deployer-token',
                        variable: 'KUBE_TOKEN'
                    ),
                    file(
                        credentialsId: 'kubernetes-ca-cert',
                        variable: 'KUBE_CA'
                    )
                ]) {
                    sh '''
                        set +x
                        unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
                        export NO_PROXY="172.19.0.5,localhost,127.0.0.1"
                        export no_proxy="$NO_PROXY"
                        set -eu

                        echo "Proxy environment check:"
                        env | grep -i proxy | cut -d= -f1 || true
                        KUBE_TMP="$(mktemp -d)"
                        trap 'rm -rf "$KUBE_TMP"' EXIT
                        export KUBECONFIG="$KUBE_TMP/config"

                        kubectl config set-cluster devops-lab \
                            --server=https://172.19.0.5:6443 \
                            --certificate-authority="$KUBE_CA" \
                            --embed-certs=true

                        kubectl config set-credentials jenkins-deployer \
                            --token="$KUBE_TOKEN"

                        kubectl config set-context jenkins-deploy \
                            --cluster=devops-lab \
                            --user=jenkins-deployer \
                            --namespace=default
                        kubectl patch deployment hello-devops --type=strategic \
                            -p '{"spec":{"template":{"spec":{"containers":[{"name":"hello-devops","imagePullPolicy":"IfNotPresent"}]}}}}'
                        kubectl config use-context jenkins-deploy

                        kubectl get deployment hello-devops
                        kubectl patch deployment hello-devops --type=strategic \
    -p '{"spec":{"template":{"spec":{"containers":[{"name":"hello-devops","imagePullPolicy":"IfNotPresent"}]}}}}'

                        kubectl set image deployment/hello-devops \
                            hello-devops="kind-registry:5000/hello-devops:${BUILD_NUMBER}"

                        kubectl rollout status deployment/hello-devops \
                            --timeout=120s

                        echo "Kubernetes deployment completed successfully."
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Build, test, push, and deployment completed!'
        }

        failure {
            echo 'FAILURE: Check the Console Output for details.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
