# cfn-cr-synapse-tagger

Cloudformation Custom Resource that sets tags Synapse tags on AWS resources.

Inventory of source code and supporting files:

- set_bucket_tags - Function to set tags on S3 buckets.
- set_instance_tags - Function to set tags on EC2 instances.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) is used to build and package the lambda code. The [sceptre](https://github.com/Sceptre/sceptre)
utility is used to deploy the macro that invokes the lambda as a CloudFormation stack.

## Use in a Cloudformation Template

### S3 Bucket

Create a custom resource in your cloudformation template. Here's an example:
```yaml
  TagBucket:
    Type: Custom::SynapseTagger
    Properties:
      ServiceToken: !ImportValue
        'Fn::Sub': '${AWS::Region}-cfn-cr-synapse-tagger-SetBucketTagsFunctionArn'
      BucketName: !Ref MyBucket
```

The creation of the custom resource triggers the lambda, which pulls the current
tags from `S3Bucket`, derives new tags, and sets those on the bucket. Currently
the only new tag added is an `OwnerEmail` tag, whose value looks like
`janedoe@synapse.org`, where the `janedoe` is a
[Synapse](https://www.synapse.org/) user name. Synapse provides email addresses
for all user names.

### EC2 Instance

Create a custom resource in your cloudformation template. Here's an example:
```yaml
  TagInstance:
    Type: Custom::SynapseTagger
    Properties:
      ServiceToken: !ImportValue
        'Fn::Sub': '${AWS::Region}-cfn-cr-synapse-tagger-SetInstanceTagsFunctionArn'
      InstanceId: !Ref MyEC2
```

The creation of the custom resource triggers the lambda, which pulls the current
tags from `MyEC2` instance, derives new tags, and sets those on the instance.

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

```bash
$ sam build --use-container
```

### Run locally

```bash
$ sam local invoke SetBucketTagsFunction --event events/create.json
```

### Run unit tests
Tests are defined in the `tests` folder in this project. Use PIP to install the
[pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
$ python -m pytest tests/ -v
```

## Deployment

### Build

```shell script
sam build
```

## Deploy Lambda to S3
This requires the correct permissions to upload to bucket
`bootstrap-awss3cloudformationbucket-19qromfd235z9`.

```shell script
sam package --template-file template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file .aws-sam/build/cfn-cr-synapse-tagger.yaml

aws s3 cp .aws-sam/build/cfn-cr-synapse-tagger.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/cfn-cr-synapse-tagger/master
```

## Install Lambda into AWS
Create the following [sceptre](https://github.com/Sceptre/sceptre) file

config/prod/cfn-cr-synapse-tagger.yaml
```yaml
template_path: "remote/cfn-cr-synapse-tagger.yaml"
stack_name: "cfn-cr-synapse-tagger"
hooks:
  before_launch:
    - !cmd "curl https://s3.amazonaws.com/essentials-awss3lambdaartifactsbucket-x29ftznj6pqw/it-lambda-set-bucket-tags/master/cfn-cr-synapse-tagger.yaml --create-dirs -o templates/remote/cfn-cr-synapse-tagger.yaml"
```

Install the lambda using sceptre:
```bash script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/cfn-cr-synapse-tagger
```


```

## Author

[Tess Thyer](https://github.com/tthyer); Principal Data Engineer, Sage Bionetworks
