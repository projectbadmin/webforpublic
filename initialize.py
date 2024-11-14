# Parse command-line arguments 
import argparse
import configparser
import os
import subprocess

from applogging import init_logging

def initialize(application):
    parser = argparse.ArgumentParser(description='Run the Flask app with a specific environment.')
    parser.add_argument('--env', type=str, help='Environment to run the app in (local, cloud)')
    args = parser.parse_args()
    if args.env is not None:
        env = args.env
    else:
        env = 'beanstalkinstance'

    # load the config file
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        application.config['env'] = env
        application.config['https_of_cloudBatchJobTemplateDevelopment'] = config.get(env, 'https_of_cloudBatchJobTemplateDevelopment')
        application.config['clone_of_cloudBatchJobTemplate'] = config.get(env, 'clone_of_cloudBatchJobTemplate')
        application.config['logDirectory_of_cloudBatchJobTemplate'] = config.get(env, 'logDirectory_of_cloudBatchJobTemplate')
        application.config['logDirectory_of_webforpublic'] = config.get(env, 'logDirectory_of_webforpublic')
        application.config['AWS_ACCESS_KEY_ID'] = config.get(env, 'AWS_ACCESS_KEY_ID')
        application.config['AWS_SECRET_ACCESS_KEY'] = config.get(env, 'AWS_SECRET_ACCESS_KEY')
        application.config['path_of_interfaceOnly_javap'] = config.get(env, 'path_of_interfaceOnly_javap')
        application.config['SECRET_KEY'] = config.get(env, 'SECRET_KEY')
    except Exception as e:
        print(e)
        
    # Set the secret key
    application.secret_key = os.environ.get('SECRET_KEY', application.config['SECRET_KEY'])  # Load from environment variable or use a default

    # Create necessary directories
    directories = [
        application.config['clone_of_cloudBatchJobTemplate'],
        application.config['logDirectory_of_cloudBatchJobTemplate'],
        application.config['logDirectory_of_webforpublic']
    ]

    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                if env in ['local', 'ec2instance']:
                    subprocess.run([f"sudo mkdir {directory}"], capture_output=True, text=True, shell=True)
                    subprocess.run([f"sudo chmod 777 {directory}"], capture_output=True, text=True, shell=True)
                    print(f"Directory {directory} created with permissions 777.")
                else:
                    os.makedirs(directory, exist_ok=True)
                    print(f"Directory {directory} created.")
            except Exception as e:
                print(f"Failed to create directory {directory}: {e}")

    # download necessary the file
    if application.config['env'] != 'local':
        # Set environment variables
        env = os.environ.copy()
        env['AWS_ACCESS_KEY_ID'] = application.config['AWS_ACCESS_KEY_ID']
        env['AWS_SECRET_ACCESS_KEY'] = application.config['AWS_SECRET_ACCESS_KEY']
        subprocess.run([f"aws s3 cp s3://git-cloudbatchjobtemplatedevelopment/interfaceOnly_javap.txt {application.config['path_of_interfaceOnly_javap']}"], capture_output=True, text=True, shell=True, env=env)

    # initialize logging
    init_logging(application)
    application.logger.info('Initialized logging')

    # Configure your application and register blueprints here