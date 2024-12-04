import subprocess
import shutil
import os
import json

from flask import session

from commonFunction import send_post_request

def process(app, code_for_onStart, code_for_onProcess, code_for_onEnd, requestid, requestContentInJSON):
    try:
        # Set environment variables
        env = os.environ.copy()
        env['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
        env['AWS_SECRET_ACCESS_KEY'] = app.config['AWS_SECRET_ACCESS_KEY']

        # copy the cloudBatchJobTemplate repository
        if app.config['env'] == 'local':
            shutil.copytree(f"{app.config['clone_of_cloudBatchJobTemplate']}cloudBatchJobTemplateDevelopment", f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}")
        if app.config['env'] in ['ec2instance', 'beanstalkinstance']:
            subprocess.run([f"aws s3 sync s3://git-cloudbatchjobtemplatedevelopment/Cloud_BatchJob_In_Java/ {app.config['clone_of_cloudBatchJobTemplate']}{requestid}"], capture_output=True, text=True, shell=True, env=env)
        
        # Write the main logic file
        if requestContentInJSON["FUT_OPT"] == "F":
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'r') as file:
                file_content = file.read()
            updated_content = file_content
            updated_content = updated_content.replace("/*code_for_onStart*/", code_for_onStart)
            updated_content = updated_content.replace("/*code_for_onProcess*/", code_for_onProcess)
            updated_content = updated_content.replace("/*code_for_onEnd*/", code_for_onEnd)
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'w') as file:
                file.write(updated_content)
            app.logger.info(f"Wrote the main logic file to {app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java")
                    
        # Maven build the project
        project_dir = f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/"
        cmd_prefix = 'sudo ' if app.config['env'] in ['ec2instance'] else ''
        subprocess.run([f"{cmd_prefix}mvn clean install package -f {project_dir}pom.xml"], capture_output=True, text=True, shell=True)
        app.logger.info(f"Ran Maven build in {project_dir}")

        # grant full access to the jat file
        subprocess.run([f"sudo chmod 777 {app.config['clone_of_cloudBatchJobTemplate']}{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar"], capture_output=True, text=True, shell=True)

        # Run the jar file
        if app.config['env'] == 'local':
            # Copy the with-dependencies.jar file to another directory and rename it
            jar_file = os.path.join(project_dir, 'target', 'cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar')
            shutil.copy(jar_file, app.config['clone_of_cloudBatchJobTemplate'])
            os.rename(
                os.path.join(app.config['clone_of_cloudBatchJobTemplate'], 'cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar'),
                os.path.join(app.config['clone_of_cloudBatchJobTemplate'], f'{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar')
            )
            app.logger.info(f"Copied {jar_file} to {app.config['clone_of_cloudBatchJobTemplate']}")

        # Copy the job to S3
        if app.config['env'] in ['ec2instance', 'beanstalkinstance']:
            # create S3 folder for the requestid            
            subprocess.run([f"aws s3 cp {app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ s3://projectbcloudbatchjobprogramfile/{requestid}/ --recursive"], capture_output=True, text=True, shell=True, env=env)            # sync the folder to S3
            subprocess.run([f"aws s3 cp {app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/target/cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar s3://projectbcloudbatchjobprogramfile/{requestid}/"], capture_output=True, text=True, shell=True, env=env)            # sync the folder to S3

        ## Run the jar file in AWS Batch
        # Use existing job definition and submit a new job with a new command
        job_definition_name = 'projectbcloudbatchjobprogramfile-job-defintion'
        job_queue_name = 'projectbcloudbatchjobprogramfile-fargate-job-queue'
        job_name = f"{requestid}"

        # Submit the job with a new command
        command_for_BatchJob = ""
        command_for_BatchJob += "yum -y install java && "
        command_for_BatchJob += "yum -y install awscli && "
        command_for_BatchJob += f"aws s3 cp s3://projectbcloudbatchjobprogramfile/{requestid}/cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar && "
        command_for_BatchJob += f'java -jar cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar AWSBatch {requestid} {requestContentInJSON["FUT_OPT"]} {requestContentInJSON["FROMDATE"]} {requestContentInJSON["FROMTIME"]} && '
        command_for_BatchJob += f"aws s3 cp {requestid}.log s3://projectbcloudbatchjoboutputfile/{requestid}/{requestid}.log"

        command_for_call_aws_batch = ""
        command_for_call_aws_batch += 'aws batch submit-job --job-name '+job_name+' --job-definition '+job_definition_name+' '
        command_for_call_aws_batch += '--job-queue '+job_queue_name+' '
        command_for_call_aws_batch += '--region ap-south-1 '
        command_for_call_aws_batch += '--container-overrides \'{'
        command_for_call_aws_batch += '    "command": ["sh", "-c", "'+command_for_BatchJob+'"], '
        command_for_call_aws_batch += '    "environment": [ '
        command_for_call_aws_batch += '    {"name": "AWS_ACCESS_KEY_ID", "value": "'+app.config['AWS_ACCESS_KEY_ID']+'"}, '
        command_for_call_aws_batch += '    {"name": "AWS_SECRET_ACCESS_KEY", "value": "'+app.config['AWS_SECRET_ACCESS_KEY']+'"}]}\' '
        
        subprocess.run([command_for_call_aws_batch], capture_output=True, text=True, shell=True, env=env)
        
        requestContentInJSON = {
            "CLOUD_BATCHJOB_ID": job_name,
            "DATA_STREAM_ID": requestid
        }
        response = send_post_request(
            'https://vslvilrd63.execute-api.ap-south-1.amazonaws.com/Create_Cloud_BatchJob', requestContentInJSON
        )
        response['requestContentInJSON'] = requestContentInJSON

        app.logger.info(f"Submitted Batch job {job_name} to queue {job_queue_name} with existing job definition {job_definition_name}")

    except Exception as e:
        app.logger.error(e)
    finally:
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}", ignore_errors=True)
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)
        jar_file_path = os.path.join(app.config['clone_of_cloudBatchJobTemplate'], f'{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar')
        if os.path.exists(jar_file_path):
            os.remove(jar_file_path)
            app.logger.info(f"Removed {jar_file_path}")
        
            

def realTimeUpdateLog(app, tempPageRequestID):
    output = ""
    try:
        if tempPageRequestID is not None:
            tempPageRequestID_value = session.get(tempPageRequestID, 'No requestid found')
            requestid = tempPageRequestID_value['requestid']
            log_file_path = os.path.join(app.config['logDirectory_of_cloudBatchJobTemplate'], f"{requestid}.log.0")
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as file:
                    output += file.read()
    except Exception as e:
        app.logger.error(e)
    return output

def checkSyntaxBeforeCompile(app, onStartCode, onProcessCode, onEndCode, requestid, requestContentInJSON):
    try:
        # Set environment variables
        env = os.environ.copy()
        env['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
        env['AWS_SECRET_ACCESS_KEY'] = app.config['AWS_SECRET_ACCESS_KEY']

        # delete the interfaceOnly directory first
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)
        
        # copy the cloudBatchJobTemplate repository
        if app.config['env'] == 'local':
            shutil.copytree(f"{app.config['clone_of_cloudBatchJobTemplate']}cloudBatchJobTemplateDevelopment_interfaceOnly", f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly")
        if app.config['env'] in ['ec2instance', 'beanstalkinstance']:
            subprocess.run([f"aws s3 sync s3://git-cloudbatchjobtemplatedevelopment/interfaceOnly/ {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly"], capture_output=True, text=True, shell=True, env=env)
            subprocess.run([f"sudo chmod -R 777 {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly"], capture_output=True, text=True, shell=True)

        # Write the main logic file   
        if requestContentInJSON["FUT_OPT"] == "F":
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'r') as file:
                    file_content = file.read()
            updated_content = file_content
            updated_content = updated_content.replace("/*code_for_onStart*/", onStartCode)
            updated_content = updated_content.replace("/*code_for_onProcess*/", onProcessCode)
            updated_content = updated_content.replace("/*code_for_onEnd*/", onEndCode)
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'w') as file:
                file.write(updated_content)
            file.close()
            app.logger.info(f"Wrote the main logic file to {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java")
        
        # javac compile all java files inside requestid_interfaceOnly folder
        cmd_prefix = 'sudo ' if app.config['env'] in ['ec2instance'] else ''
        result = subprocess.run(f"{cmd_prefix}javac $(find {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java -name '*.java')", capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            errors = result.stderr
            return errors
        
        # run the Main
        cmd_prefix = 'sudo ' if app.config['env'] in ['ec2instance'] else ''
        result = subprocess.run([f"{cmd_prefix}java -classpath {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java Main"], capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            errors = result.stderr
            return errors

        return ""
    except Exception as e:
        app.logger.error(e)
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)

def checkSyntax(app, part_of_code, code, requestid, requestContentInJSON):
    try:
        # Set environment variables
        env = os.environ.copy()
        env['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
        env['AWS_SECRET_ACCESS_KEY'] = app.config['AWS_SECRET_ACCESS_KEY']

        # copy the cloudBatchJobTemplate repository
        if os.path.exists(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly")==False:
            if app.config['env'] == 'local':
                shutil.copytree(f"{app.config['clone_of_cloudBatchJobTemplate']}cloudBatchJobTemplateDevelopment_interfaceOnly", f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly")
            if app.config['env'] in ['ec2instance', 'beanstalkinstance']:
                subprocess.run([f"aws s3 sync s3://git-cloudbatchjobtemplatedevelopment/interfaceOnly/ {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly"], capture_output=True, text=True, shell=True, env=env)
                subprocess.run([f"sudo chmod -R 777 {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly"], capture_output=True, text=True, shell=True)
        else:
            if requestContentInJSON["FUT_OPT"] == "F":
                shutil.copy(
                    f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java.original",
                    f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java"
                )

        # Write the main logic file   
        if requestContentInJSON["FUT_OPT"] == "F":
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'r') as file:
                    file_content = file.read()
            updated_content = file_content
            if part_of_code == "onStart":
                updated_content = updated_content.replace("/*code_for_onStart*/", code)
            if part_of_code == "onProcess":
                updated_content = updated_content.replace("/*code_for_onProcess*/", code)
            if part_of_code == "onEnd":
                updated_content = updated_content.replace("/*code_for_onEnd*/", code)
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'w') as file:
                file.write(updated_content)
            file.close()
            app.logger.info(f"Wrote the main logic file to {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java")
        
        # javac compile all java files inside requestid_interfaceOnly folder
        cmd_prefix = 'sudo ' if app.config['env'] in ['ec2instance'] else ''
        result = subprocess.run(f"{cmd_prefix}javac $(find {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java -name '*.java')", capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            errors = result.stderr
            return errors
        
        # run the Main
        cmd_prefix = 'sudo ' if app.config['env'] in ['ec2instance'] else ''
        result = subprocess.run([f"{cmd_prefix}java -classpath {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java Main"], capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            errors = result.stderr
            return errors

        return ""
    except Exception as e:
        app.logger.error(e)
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)

