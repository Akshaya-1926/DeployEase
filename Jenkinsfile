
pipeline {
    agent any

    stages {
        stage('Checkout GitHub') {
            steps {
                checkout scm
            }
        }

        stage('Build Java Application') {
            steps {
                dir('sample-app') {
                    sh 'mvn clean package'
                }
            }
        }

        stage('Deploy with Ansible') {
            steps {
                sh 'ansible-playbook -i localhost, -c local deploy.yml'
            }
        }

        stage('Start Application') {
            steps {
                sh '''
                    APP_DIR=/var/lib/jenkins/deployease-app
                    mkdir -p "$APP_DIR"

                    if [ -f "$APP_DIR/app.pid" ]; then
                        OLD_PID=$(cat "$APP_DIR/app.pid")
                        if [ -n "$OLD_PID" ]; then
                            kill "$OLD_PID" 2>/dev/null || true
                        fi
                    fi

                    nohup env JENKINS_NODE_COOKIE=dontKillMe \
                        java -jar "$APP_DIR/app.jar" \
                        > "$APP_DIR/app.log" 2>&1 &

                    echo $! > "$APP_DIR/app.pid"

                    sleep 3
                    curl --fail http://127.0.0.1:8081/
                '''
            }
        }
    }

    post {
        success {
            echo 'DeployEase deployment successful!'
        }
        failure {
            echo 'DeployEase deployment failed!'
        }
    }
}
