import argparse
import configparser
import os
import subprocess
from flask import Flask

from applogging import init_logging

def create_app():
    app = Flask(__name__)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run the Flask app with a specific environment.')
    parser.add_argument('--env', type=str, default='beanstalkinstance', help='Environment to run the app in (local, cloud)')
    args = parser.parse_args()
    env = args.env

    # load the config file
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        app.config['env'] = env
        app.config['https_of_cloudBatchJobTemplateDevelopment'] = config.get(env, 'https_of_cloudBatchJobTemplateDevelopment')
        app.config['clone_of_cloudBatchJobTemplate'] = config.get(env, 'clone_of_cloudBatchJobTemplate')
        app.config['logDirectory_of_cloudBatchJobTemplate'] = config.get(env, 'logDirectory_of_cloudBatchJobTemplate')
        app.config['logDirectory_of_webforpublic'] = config.get(env, 'logDirectory_of_webforpublic')
        app.config['AWS_ACCESS_KEY_ID'] = config.get(env, 'AWS_ACCESS_KEY_ID')
        app.config['AWS_SECRET_ACCESS_KEY'] = config.get(env, 'AWS_SECRET_ACCESS_KEY')
        app.config['path_of_interfaceOnly_javap'] = config.get(env, 'path_of_interfaceOnly_javap')
    except Exception as e:
        app.logger.error(e)

    # create necessary directory
    if not os.path.exists(app.config['clone_of_cloudBatchJobTemplate']):
        os.makedirs(app.config['clone_of_cloudBatchJobTemplate'])
        os.chmod(app.config['clone_of_cloudBatchJobTemplate'], 0o777)
    if not os.path.exists(app.config['logDirectory_of_cloudBatchJobTemplate']):
        os.makedirs(app.config['logDirectory_of_cloudBatchJobTemplate'])
        os.chmod(app.config['logDirectory_of_cloudBatchJobTemplate'], 0o777)
    if not os.path.exists(app.config['logDirectory_of_webforpublic']):
        os.makedirs(app.config['logDirectory_of_webforpublic'])
        os.chmod(app.config['logDirectory_of_webforpublic'], 0o777)

    # download necessary the file
    if app.config['env'] != 'local':
        # Set environment variables
        env = os.environ.copy()
        env['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
        env['AWS_SECRET_ACCESS_KEY'] = app.config['AWS_SECRET_ACCESS_KEY']
        subprocess.run([f"aws s3 cp s3://git-cloudbatchjobtemplatedevelopment/interfaceOnly_javap.txt {app.config['path_of_interfaceOnly_javap']}"], capture_output=True, text=True, shell=True)

    # initialize logging
    init_logging(app)
    app.logger.info('Initialized logging')

    # Configure your app and register blueprints here
    return app