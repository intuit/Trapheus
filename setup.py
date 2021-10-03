from setuptools import setup

setup(name='trapheus', version='0.1.2', author='stationeros (Rohit Kumar)',
      author_email='rite2rohit88@gmail.com',
      url='https://github.com/intuit/Trapheus',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Topic :: System :: Archiving :: Backup',
          'Topic :: System :: Clustering',
          'Topic :: System :: Distributed Computing'
      ],
      keywords='aws backup lambda rds snapshots step-functions state-machine aws-lambda-layer aws-lambda aws',
      packages=['trapheus'],
      install_requires=['boto3', 'aws-sam-cli'],
      python_requires='>=3.7',
      description='Backup and restore manager for AWS RDS instances'
      )
