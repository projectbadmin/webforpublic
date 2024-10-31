from setuptools import setup, find_packages

setup(
    name='webforpublic',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        # Add other dependencies here
    ],
	entry_points={
        'console_scripts': [
            'webforpublic=app:main',  # Replace `app:main` with your entry point
        ],
    }
)