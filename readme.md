# Scatter gather with AWS lambda

## The Task
Implement batch processing on AWS.

* Receive a single batch of tasks
* Process tasks as parallel as possible
* Write a result summary into s3 when all tasks processed

## Prerequisites
* python 3.8
* GNU make
* docker
* [awscli](https://docs.aws.amazon.com/de_de/cli/latest/userguide/cli-chap-install.html)
* [tfvm](https://github.com/cbuschka/tfvm) or terraform
* [cw >= v3.3.0](https://github.com/lucagrulla/cw)

## Usage

### Start localstack, deploy and run benchmark
```
make clean start_localstack deploy benchmark report
```

### Stop and cleanup
```
make stop_localstack clean
```

### Variants
The task has been implemented in various variants:
* s3-sqs-lambda-sync
* s3-sqs-lambda-async (to come)
![s3-sqs-lambda](./doc/s3_sqs_lambda.png)
* s3-sqs-lambda-dynamodb (to come)
* s3-sqs-sfn (to come)

### Repository structure
* [infra](./infra) - Resources and service infrastructure
* [src](./src) - Service sources
* [resources](./resources) - Service resources
* [tests](./tests) - Service tests
* [benchmark](./benchmark) - Benchmark sources

### Documentation
* [Learnings](./doc/learnings.md)
* [Links](./doc/links.md)
* [Troubleshooting](./doc/troubleshooting.md)

## License
Copyright 2020 by Cornelius Buschka. All rights reserved.

[Apache Public License 2.0](./license.txt)
