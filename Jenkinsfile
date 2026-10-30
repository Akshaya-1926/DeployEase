stage('Start Application') {
    steps {
        sh '''
            set -eu

            APP_DIR=/var/lib/jenkins/deployease-app

            # Stop the previous application
            if [ -f "$APP_DIR/app.pid" ]; then
                OLD_PID=$(cat "$APP_DIR/app.pid")

                if [ -n "$OLD_PID" ]; then
                    kill "$OLD_PID" 2>/dev/null || true
                fi
            fi

            # Wait for port 8081 to become free
            for i in $(seq 1 30); do
                if ! ss -ltn | grep -q ':8081 '; then
                    break
                fi
                sleep 1
            done

            if ss -ltn | grep -q ':8081 '; then
                echo "ERROR: Port 8081 is occupied"
                ss -ltnp | grep ':8081' || true
                exit 1
            fi

            # Start application
            nohup env JENKINS_NODE_COOKIE=dontKillMe \
                java -jar "$APP_DIR/app.jar" \
                > "$APP_DIR/app.log" 2>&1 < /dev/null &

            echo $! > "$APP_DIR/app.pid"

            # Wait until the new application responds
            READY=0

            for i in $(seq 1 30); do
                if curl -fsS http://127.0.0.1:8081/ > /dev/null; then
                    READY=1
                    break
                fi

                if ! kill -0 "$(cat "$APP_DIR/app.pid")" 2>/dev/null; then
                    echo "Java process exited unexpectedly"
                    break
                fi

                sleep 1
            done

            if [ "$READY" -ne 1 ]; then
                echo "Application failed to start"
                tail -n 50 "$APP_DIR/app.log" || true
                exit 1
            fi

            echo "DeployEase application started successfully!"
        '''
    }
}
