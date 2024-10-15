import subprocess
import shutil
import os
import json

def process(app, code_for_onStart, code_for_onProess, code_for_onEnd, requestid, requestContentInJSON):
    try:
        # Set environment variables
        env = os.environ.copy()
        env['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
        env['AWS_SECRET_ACCESS_KEY'] = app.config['AWS_SECRET_ACCESS_KEY']

        # copy the cloudBatchJobTemplate repository
        if app.config['env'] == 'local':
            shutil.copytree(f"{app.config['clone_of_cloudBatchJobTemplate']}cloudBatchJobTemplateDevelopment", f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}")
        if app.config['env'] == 'cloud':
            subprocess.run([f"aws s3 sync s3://git-cloudbatchjobtemplatedevelopment/Cloud_BatchJob_In_Java/ {app.config['clone_of_cloudBatchJobTemplate']}{requestid}"], capture_output=True, text=True, shell=True, env=env)
        
        # Write the main logic file
        if requestContentInJSON["FUT_OPT"] == "F":
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'r') as file:
                file_content = file.read()
            updated_content = file_content
            updated_content = updated_content.replace("/*code_for_onStart*/", code_for_onStart)
            updated_content = updated_content.replace("/*code_for_onProess*/", code_for_onProess)
            updated_content = updated_content.replace("/*code_for_onEnd*/", code_for_onEnd)
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'w') as file:
                file.write(updated_content)
            app.logger.info(f"Wrote the main logic file to {app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java")
                    
        # Maven build the project
        project_dir = f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava"
        subprocess.run(['sudo', 'mvn', 'clean', 'install', 'package'], cwd=project_dir, capture_output=True, text=True)
        app.logger.info(f"Ran Maven build in {project_dir}")
        
        # Copy the with-dependencies.jar file to another directory and rename it
        jar_file = os.path.join(project_dir, 'target', 'cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar')
        destination_dir = app.config['clone_of_cloudBatchJobTemplate']
        shutil.copy(jar_file, destination_dir)
        os.rename(
            os.path.join(destination_dir, 'cloudBatchJobInJava-0.0.1-SNAPSHOT-jar-with-dependencies.jar'),
            os.path.join(destination_dir, f'{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar')
        )
        app.logger.info(f"Copied {jar_file} to {destination_dir}")
        
        # Run the jar file
        result = subprocess.run(
            ['sudo', 'java', '-jar', f'{destination_dir}{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar', requestid, json.dumps(requestContentInJSON)],
            capture_output=True,
            text=True,
            env=env
        )
        app.logger.info(f"Ran {destination_dir}{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
    
    except Exception as e:
        app.logger.error(e)
    finally:
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}", ignore_errors=True)
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)
        jar_file_path = os.path.join(app.config['clone_of_cloudBatchJobTemplate'], f'{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar')
        if os.path.exists(jar_file_path):
            os.remove(jar_file_path)
            app.logger.info(f"Removed {jar_file_path}")
        
            

def realTimeUpdateLog(app, requestid):
    output = ""
    try:
        if requestid is not None:
            log_file_path = os.path.join(app.config['logDirectory_of_cloudBatchJobTemplate'], f"{requestid}.log.0")
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as file:
                    output += file.read()
    except Exception as e:
        app.logger.error(e)
    return output

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
            if app.config['env'] == 'cloud':
                subprocess.run([f"aws s3 sync s3://git-cloudbatchjobtemplatedevelopment/interfaceOnly/ {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly"], capture_output=True, text=True, shell=True, env=env)
        else:
            if requestContentInJSON["FUT_OPT"] == "F":
                shutil.copy(
                    f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData(Original).java",
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
                updated_content = updated_content.replace("/*code_for_onProess*/", code)
            if part_of_code == "onEnd":
                updated_content = updated_content.replace("/*code_for_onEnd*/", code)
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'w') as file:
                file.write(updated_content)
            file.close()
            app.logger.info(f"Wrote the main logic file to {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java")
        
        # javac compile all java files inside requestid_interfaceOnly folder
        result = subprocess.run(f"sudo javac $(find {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java -name '*.java')", capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            errors = result.stderr
            return errors
        
        # run the Main
        result = subprocess.run([f"sudo java -classpath {app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly/cloudBatchJobInJava/src/main/java Main"], capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            errors = result.stderr
            return errors

        return ""
    except Exception as e:
        app.logger.error(e)
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)

