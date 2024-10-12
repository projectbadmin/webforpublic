import subprocess
import shutil
import os
import json

def process(app, code_for_onStart, code_for_onProess, code_for_onEnd, requestid, requestContentInJSON):
    try:
        # copy the cloudBatchJobTemplate repository
        shutil.copytree(f"{app.config['clone_of_cloudBatchJobTemplate']}cloudBatchJobTemplateDevelopment", f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}")
        app.logger.info(f"Copied {app.config['clone_of_cloudBatchJobTemplate']}cloudBatchJobTemplateDevelopment to {app.config['clone_of_cloudBatchJobTemplate']}{requestid}")
        
        # Write the main logic file
        if requestContentInJSON["FUT_OPT"] == "F":
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'w') as file:
                file_content = file.read()
            updated_content = file_content.replace("/*code_for_onStart*/", code_for_onStart)
            updated_content = file_content.replace("/*code_for_onProess*/", code_for_onProess)
            updated_content = file_content.replace("/*code_for_onEnd*/", code_for_onEnd)
            with open(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java", 'w') as file:
                file.write(updated_content)
        app.logger.info(f"Wrote the main logic file to {app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava/src/main/java/main/logiclibrary/ForFutureData.java")
                    
        # Maven build the project
        project_dir = f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}/cloudBatchJobInJava"
        result = subprocess.run(['mvn', 'clean', 'install', 'package'], cwd=project_dir, capture_output=True, text=True)
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
        # Set environment variables
        env = os.environ.copy()
        env['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
        env['AWS_SECRET_ACCESS_KEY'] = app.config['AWS_SECRET_ACCESS_KEY']

        # Run the jar file with the environment variables
        result = subprocess.run(
            ['java', '-jar', f'{destination_dir}{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar', requestid, json.dumps(requestContentInJSON)],
            capture_output=True,
            text=True,
            env=env
        )
        app.logger.info(f"Ran {destination_dir}{requestid}-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
    
    except Exception as e:
        app.logger.error(e)
    finally:
        shutil.rmtree(f"{app.config['clone_of_cloudBatchJobTemplate']}{requestid}", ignore_errors=True)
        

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