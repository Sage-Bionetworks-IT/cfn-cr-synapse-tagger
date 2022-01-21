# cfn-cr-synapse-tagger

Cloudformation Custom Resource used to apply tags to resources provisioned using the
Sage Service Catalog.

## Inventory of source code and supporting files:

- set_tags - Function to set tags on resources.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) is used to build and package the lambda code. The [sceptre](https://github.com/Sceptre/sceptre)
utility is used to deploy the macro that invokes the lambda as a CloudFormation stack.

## Prerequisites

This custom resource only works with when used with the
[Synapse IDP](https://github.com/Sage-Bionetworks/synapse-login-scipool) and the
[AWS Service Catalog](https://aws.amazon.com/servicecatalog).

AWS will apply the following tags when resources are provisioned with the Service Catalog:

|Key                                        |Value (something like)                                                    |
|-------------------------------------------|--------------------------------------------------------------------------|
|aws:servicecatalog:provisioningPrincipalArn|arn:aws:sts::123456712:assumed-role/ServiceCatalogEndusers/1234567        |
|aws:servicecatalog:provisionedProductArn   |arn:aws:servicecatalog:us-east-1:123456712:stack/my-product/pp-mycpuogt2i45s|

This custom resource uses these tags to retrieve more information and applies
them as additional tags on the provisioned resource.

### Supported Tags

#### All Resources
* Synapse tags - Retrieve the [Synapse userProfile](https://docs.synapse.org/rest/org/sagebionetworks/repo/model/UserProfile.html)
info and apply a subset of that data as tags to resources.

#### EC2 Only
* AccessApprovedCaller tag - Generate the info to allow role access to an instance and apply it as a tag on the resource.

### Parameters

This custom resource assumes the existence of the following SSM parameters:

* `/service-catalog/TeamToRoleArnMap` - used to determine and apply the Synapse team tag

The specification for these parameters are defined by the
[synapse login app](https://github.com/Sage-Bionetworks/synapse-login-scipool#configurations).

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

### Scheduled Jobs (Batch)

Create a custom resource in your cloudformation template. Here's an example:
```yaml
  BatchTagger:
    Type: Custom::SynapseTagger
    Properties:
      ServiceToken: !ImportValue
        'Fn::Sub': '${AWS::Region}-cfn-cr-synapse-tagger-SetBatchTagsFunctionArn'
      BatchResources:
        JobDefinitionArn: !Ref JobDefinition
        JobQueueArn: !Ref JobQueue
        ComputeEnvironmentArn: !Ref ComputeEnvironment
        SchedulingPolicyArn: !Ref SchedulingPolicy
```

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

```bash
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
  --output-template-file .aws-sam/build/cfn-cr-synapse-tagger.yaml

aws s3 cp .aws-sam/build/cfn-cr-synapse-tagger.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/cfn-cr-synapse-tagger/master/
```

## Publish Lambda

### Private access
Publishing the lambda makes it available in your AWS account.  It will be accessible in
the [serverless application repository](https://console.aws.amazon.com/serverlessrepo).

```shell script
sam publish --template .aws-sam/build/cfn-cr-synapse-tagger.yaml
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

### Sceptre
Create the following [sceptre](https://github.com/Sceptre/sceptre) file

config/prod/cfn-cr-synapse-tagger.yaml
```yaml
template:
  type: http
  url: "https://s3.amazonaws.com/essentials-awss3lambdaartifactsbucket-x29ftznj6pqw/it-lambda-set-bucket-tags/master/cfn-cr-synapse-tagger.yaml"
stack_name: "cfn-cr-synapse-tagger"
```

Install the lambda using sceptre:
```bash script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/cfn-cr-synapse-tagger
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
