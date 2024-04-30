node {
    stage('Pull') {
            git branch: 'deploy', credentialsId: 'bespoke-git-secret-key', url: 'https://github.com/BespokeCreditCard/FlaskServer.git'
    }

    withCredentials([file(credentialsId: 'secret-file-env', variable: 'ENV_FILE')]) {
        stage('Docker build') {
            sh '''
            yes | sudo docker image prune -a
            sudo cp /home/ubuntu/requirements.txt /var/lib/jenkins/workspace/${JOB_NAME}/flask-build/requirements.txt
            sudo docker build -f /var/lib/jenkins/workspace/${JOB_NAME}/flask-build/Dockerfile \
                -t flask-app .

            rm temp_env.sh
            rm cleaned_env.sh 
            '''
        }
    }

    withCredentials([[$class: 'UsernamePasswordMultiBinding', 
        credentialsId: 'docker-hub', 
        usernameVariable: 'DOCKER_USER_ID', 
        passwordVariable: 'DOCKER_USER_PASSWORD']]) {
            stage('Docker Tag') {
                sh(script: 'echo $DOCKER_USER_ID')
                sh(script: 'echo ${DOCKER_USER_ID}')
                sh(script: '''sudo docker tag flask-app ${DOCKER_USER_ID}/flask-app:${BUILD_NUMBER}''') 
            }
            stage('Docker Push') {
                sh(script: 'sudo docker login -u ${DOCKER_USER_ID} -p ${DOCKER_USER_PASSWORD}') 
                sh(script: 'sudo docker push ${DOCKER_USER_ID}/flask-app:${BUILD_NUMBER}') 
            }
    
        withCredentials([file(credentialsId: 'secret-file-env', variable: 'MY_SECRET_FILE')]) {
                stage('Deploy') {
                    sshagent(credentials: ['aws-ssh-pem-key']) {
                        sh(script: 'ssh -o StrictHostKeyChecking=no ubuntu@15.165.82.28 "sudo docker rm -f flask-app"')
                        sh(script: 'scp $MY_SECRET_FILE ubuntu@15.165.82.28:~/.env')
                        sh(script: 'ssh ubuntu@15.165.82.28 "sudo docker run --name flask-app --env-file ~/.env -e TZ=Asia/Seoul -p 80:5000 -d -t \${DOCKER_USER_ID}/flask-app:\${BUILD_NUMBER}"')
                    }
                }
        }
    }
}   
 