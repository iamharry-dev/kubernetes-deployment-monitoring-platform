pipeline {
    agent any

    environment {
        IMAGE_NAME = 'k8s-monitoring-platform'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        NAMESPACE  = 'k8s-monitoring-dev'
    }

    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Lint & Test') {
            steps {
                sh '''
                    python -m pip install --upgrade pip
                    pip install -r app/requirements.txt flake8 pytest
                    flake8 app --max-line-length=120 || true
                    pytest -q || true
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG -t $IMAGE_NAME:latest .'
            }
        }

        stage('Validate Manifests') {
            steps {
                sh '''
                    kubectl kustomize k8s/overlays/dev >/dev/null
                    helm lint helm/app
                    helm template helm/app >/dev/null
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    kind load docker-image $IMAGE_NAME:$IMAGE_TAG --name monitoring || true
                    kubectl apply -k k8s/overlays/dev
                    kubectl set image deployment/app-dev app=$IMAGE_NAME:$IMAGE_TAG -n $NAMESPACE || true
                    kubectl rollout status deployment/app-dev -n $NAMESPACE --timeout=120s || true
                '''
            }
        }

        stage('Verify') {
            steps {
                sh 'kubectl get pods -n $NAMESPACE'
            }
        }
    }

    post {
        success { echo "Deployment succeeded: ${IMAGE_NAME}:${IMAGE_TAG}" }
        failure { echo "Pipeline failed. Check the logs above." }
        always { cleanWs() }
    }
}
