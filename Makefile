TOP_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV_DIR := ${TOP_DIR}/venv/
TARGET_DIR := ${TOP_DIR}/target/
SRC_DIR := ${TOP_DIR}/src/
TESTS_DIR := ${TOP_DIR}/tests/
BENCHMARK_DIR := ${TOP_DIR}/benchmark/
SHELL := /bin/bash
ENV := devel
ENDPOINT_ARGS :=
ifeq ($(ENV),devel)
	ENDPOINT_ARGS := --endpoint-url=http://localhost:4566
endif
SCOPE := ${USERNAME}-
COMMITISH := $(shell git describe --no-match --always --dirty)
BUILD_TIMESTAMP := $(shell date --iso-8601=seconds)

usage:
	@echo && \
	echo "make ENV=devel|aws [SCOPE=yourname-] [goal]" && \
	echo && \
	echo "Goals:" && \
	echo " all, build, package, test, benchmark, clean" && \
	echo " start_localstack, stop_localstack, reset_localstack, tail_localstack," && \
	echo " tail_cloudwatch, tail_measurements" && \
	echo " ls_s3_input, ls_s3_work, ls_s3_output"

all:	clean start_localstack package deploy benchmark

test:	build
	@echo "Running unit tests..." && \
	cd ${TOP_DIR} && \
	source ${VENV_DIR}/bin/activate && \
	PYTHONPATH=${SRC_DIR}:${TESTS_DIR} python -m unittest discover -p '*test*.py' ${TESTS_DIR}

init:
	@echo -e "ENV is ${ENV}\nSCOPE is ${SCOPE}\nCOMMITISH is ${COMMITISH}"

__is_devel:	init
	@if [ "${ENV}" != "devel" ]; then \
  		echo "ENV MUST be devel."; \
  	fi

advert:	init
	@if [ -z "$(shell which tfvm 2>/dev/null 1>/dev/null)" ]; then \
  		echo -e "\n  Use https://github.com/cbuschka/tfvm for best terraform experience.\n"; \
  	fi

init_venv:	init
	@cd ${TOP_DIR} && \
	if [ ! -d "${VENV_DIR}" ]; then \
		echo "Creating virtualenv..." && \
		virtualenv ${VENV_DIR} -p $(shell which python3.8); \
	fi

install_requirements:	init_venv
	@echo "Checking requirements..." && \
	cd ${TOP_DIR} && \
	source ${VENV_DIR}/bin/activate && \
	pip install -r requirements.txt -r requirements-dev.txt

build:	install_requirements

package:	test
	@echo "Packaging..." && \
	cd ${TOP_DIR} && \
	rm -rf ${TARGET_DIR} && \
	mkdir -p ${TARGET_DIR}/lambda && \
	source ${VENV_DIR}/bin/activate && \
	pip install -r requirements.txt --target=${TARGET_DIR}/lambda/ && \
	cd ${SRC_DIR} && \
	tar c --exclude='__pycache__' * | tar xv -C ${TARGET_DIR}/lambda/ && \
	cd ${TARGET_DIR}/lambda && \
	echo "{\"commitish\": \"${COMMITISH}\", \"built-at\": \"${BUILD_TIMESTAMP}\"}" > version.json && \
	zip --recurse-paths ${TARGET_DIR}/lambda.zip *

deploy:	deploy_resources deploy_service

deploy_resources:	init advert
	@echo "Deploying resources..." && \
	cd ${TOP_DIR}/infra/${ENV}/resources && \
	terraform init && \
	terraform apply -auto-approve -var="env=${ENV}" -var="commitish=${COMMITISH}" -var="scope=${SCOPE}"

deploy_service:	init advert package
	@echo "Deploying service..." && \
	cd ${TOP_DIR}/infra/${ENV}/service && \
	terraform init && \
	terraform apply -auto-approve -var="env=${ENV}" -var="commitish=${COMMITISH}" -var="scope=${SCOPE}"

destroy_all:	destroy_service destroy_resources

destroy_resources:	init advert
	@echo "DESTROYING resources..." && \
	cd ${TOP_DIR}/infra/${ENV}/resources && \
	terraform destroy -auto-approve -var="env=${ENV}" -var="scope=${SCOPE}"

destroy_service:	init advert
	@echo "DESTROYING service..." && \
	cd ${TOP_DIR}/infra/${ENV}/service && \
	terraform destroy -auto-approve -var="env=${ENV}" -var="scope=${SCOPE}"

kill_terraform:
	@pids="$(shell ps auwxf | grep -v grep | grep -v make | grep terraform | perl -pe 's#^[^\s]+\s+(\d+)\s+.*$$#$$1#g')"; \
	for pid in $${pids}; do \
	  kill -TERM $${pid}; \
	done

benchmark:	install_requirements
	@echo "Running benchmark..." && \
	cd ${TOP_DIR} && \
	source ${VENV_DIR}/bin/activate && \
	case ${ENV} in \
		devel) \
			LOCALSTACK_HOSTNAME=localhost SCOPE=${SCOPE} PYTHONPATH=${SRC_DIR}:${TESTS_DIR}:${BENCHMARK_DIR} python3 ${BENCHMARK_DIR}/aws_scatter_gather/benchmark/benchmark.py; \
			;; \
		aws|*) \
			SCOPE=${SCOPE} PYTHONPATH=${SRC_DIR}:${TESTS_DIR}:${BENCHMARK_DIR} python3 ${BENCHMARK_DIR}/aws_scatter_gather/benchmark/benchmark.py; \
			;; \
	esac

report:	install_requirements
	@echo "Running benchmark report..." && \
	cd ${TOP_DIR} && \
	source ${VENV_DIR}/bin/activate && \
	case ${ENV} in \
		devel) \
			LOCALSTACK_HOSTNAME=localhost SCOPE=${SCOPE} PYTHONPATH=${SRC_DIR}:${TESTS_DIR}:${BENCHMARK_DIR} python3 ${BENCHMARK_DIR}/aws_scatter_gather/benchmark/report.py; \
			;; \
		aws|*) \
			SCOPE=${SCOPE} PYTHONPATH=${SRC_DIR}:${TESTS_DIR}:${BENCHMARK_DIR} python3 ${BENCHMARK_DIR}/aws_scatter_gather/benchmark/report.py; \
			;; \
	esac

tail_cloudwatch:	init
	# https://github.com/lucagrulla/cw/releases/download/v3.3.0/cw_3.3.0_Linux_x86_64.tar.gz
	@cw ${ENDPOINT_ARGS} tail --follow --start=3m --group-name --timestamp --event-id --local \
		/aws/lambda/${SCOPE}s3-sqs-lambda-sync-scatter: \
		/aws/lambda/${SCOPE}s3-sqs-lambda-sync-process: \
		/aws/lambda/${SCOPE}s3-sqs-lambda-sync-gather: \
		/aws/lambda/${SCOPE}s3-sqs-lambda-async-scatter: \
		/aws/lambda/${SCOPE}s3-sqs-lambda-async-process: \
		/aws/lambda/${SCOPE}s3-sqs-lambda-async-gather:

start_localstack:	__is_devel
	@docker-compose rm -f
	@docker-compose up -d --force-recreate && \
	echo "Waiting for localstack to come up..." && \
	done="" && \
	while [ "$${done}" != "0" ]; do \
		aws --cli-connect-timeout=1 --cli-read-timeout=1 ${ENDPOINT_ARGS} logs describe-log-groups >/dev/null 2>&1; \
		done=$${?}; \
		echo -n "."; \
	done; \
	echo " Localstack is up."

stop_localstack:	__is_devel
	@docker-compose down -v --remove-orphans

tail_localstack:	init
	@docker-compose logs -f

clean:	init
	@echo "Cleaning up..." && \
	rm -rf ${TARGET_DIR} && \
	find . -name 'terraform.tfstate*' -print | grep devel | xargs -I FILE rm 'FILE'

reset_localstack:	stop_localstack clean start_localstack

ls_s3_output:	init
	@aws ${ENDPOINT_ARGS} s3 ls s3://${SCOPE}s3-sqs-lambda-sync-output

ls_s3_input:	init
	@aws ${ENDPOINT_ARGS} s3 ls s3://${SCOPE}s3-sqs-lambda-sync-input

ls_s3_work:	init
	@aws ${ENDPOINT_ARGS} s3 ls s3://${SCOPE}s3-sqs-lambda-sync-work
