# lambda-sc-bucket-cleanup
An application to clean up S3 buckets after it has been terminated from the Service Catalog.

We allow self service provisioning of S3 buckets in our AWS Service Catalog.  We have configured the SC to retain the bucket when users terminate an S3 bucket product from the Service catalog.  This means that the S3 bucket SC product will be removed however the S3 bucket resource remains in the account.  The buckets are orphaned from our Service Catalog which essentially puts them into an `archived` state.  The purpose of this app is to delete the archived buckets along with all of the data in the bucket after a certain number of days (archived period) after it's been archived. This lambda does not support cleaning up buckets with versioning enabled.

## Development

### Contributions
Contributions are welcome.

### Requirements
Run `pipenv install --dev` to install both production and development
requirements, and `pipenv shell` to activate the virtual environment. For more
information see the [pipenv docs](https://pipenv.pypa.io/en/latest/).

After activating the virtual environment, run `pre-commit install` to install
the [pre-commit](https://pre-commit.com/) git hook.

### Create a local build

```shell script
$ sam build
```

### Run unit tests
Tests are defined in the `tests` folder in this project. Use PIP to install the
[pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```shell script
$ python -m pytest tests/ -v
```

### Run integration tests
Running integration tests
[requires docker](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-start-api.html)

```shell script
$ sam local invoke HelloWorldFunction --event events/event.json
```

## Deployment

### Deploy Lambda to S3
Deployments are sent to the
[Sage cloudformation repository](https://bootstrap-awss3cloudformationbucket-19qromfd235z9.s3.amazonaws.com/index.html)
which requires permissions to upload to Sage
`bootstrap-awss3cloudformationbucket-19qromfd235z9` and
`essentials-awss3lambdaartifactsbucket-x29ftznj6pqw` buckets.

```shell script
sam package --template-file .aws-sam/build/template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file .aws-sam/build/lambda-sc-bucket-cleanup.yaml

aws s3 cp .aws-sam/build/lambda-sc-bucket-cleanup.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/lambda-sc-bucket-cleanup/master/
```

## Publish Lambda

### Private access
Publishing the lambda makes it available in your AWS account.  It will be accessible in
the [serverless application repository](https://console.aws.amazon.com/serverlessrepo).

```shell script
sam publish --template .aws-sam/build/lambda-sc-bucket-cleanup.yaml
```

### Public access
Making the lambda publicly accessible makes it available in the
[global AWS serverless application repository](https://serverlessrepo.aws.amazon.com/applications)

```shell script
aws serverlessrepo put-application-policy \
  --application-id <lambda ARN> \
  --statements Principals=*,Actions=Deploy
```

## Install Lambda into AWS

### Parameters
This lambda has the following parameters:

* __ArchivedPeriod__:  The number of days from the current date that
  the archived bucket should be deleted.  Note that [Cloudformation will retain
  stack info for only 90 days after it has been deleted](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stacks)
* __EnableScheule__:  true to run on a schedule, false to disable. If enabled a valid Schedule must be provided
* __Schedule__:  Schedule to execute the lambda, can be a [rate or a cron schedule](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)

### Sceptre
Create the following [sceptre](https://github.com/Sceptre/sceptre) file
config/prod/lambda-sc-bucket-cleanup.yaml

```yaml
template_path: "remote/lambda-sc-bucket-cleanup.yaml"
stack_name: "lambda-sc-bucket-cleanup"
stack_tags:
  Department: "Platform"
  Project: "Infrastructure"
  OwnerEmail: "it@sagebase.org"
parameters:
  ArchivedPeriod: "60"
hooks:
  before_launch:
    - !cmd "curl https://bootstrap-awss3cloudformationbucket-19qromfd235z9.s3.amazonaws.com/lambda-sc-bucket-cleanup/master/lambda-sc-bucket-cleanup.yaml --create-dirs -o templates/remote/lambda-sc-bucket-cleanup.yaml"
```

Install the lambda using sceptre:
```shell script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/lambda-sc-bucket-cleanup.yaml
```

### AWS Console
Steps to deploy from AWS console.

1. Login to AWS
2. Access the
[serverless application repository](https://console.aws.amazon.com/serverlessrepo)
-> Available Applications
3. Select application to install
4. Enter Application settings
5. Click Deploy

## Releasing

We have setup our CI to automate a releases.  To kick off the process just create
a tag (i.e 0.0.1) and push to the repo.  The tag must be the same number as the current
version in [template.yaml](template.yaml).  Our CI will do the work of deploying and publishing
the lambda.
