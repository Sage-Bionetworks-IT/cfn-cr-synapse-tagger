# it-lambda-set-bucket-tags

Cloudformation Macro that sets tags for a S3 bucket.

Inventory of source code and supporting files:

- set_bucket_tags - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) is used to build and package the lambda code. The [sceptre](https://github.com/Sceptre/sceptre) utility is used to deploy the macro that invokes the lambda as a CloudFormation stack.

## Use in a Cloudformation Template
Insert in your Cloudformation template a block similar to this as a sibling
of the S3 bucket (called in this example `S3Bucket`) :
```yaml
  'Fn::Transform':
    Name: "SetBucketTags"
    Parameters:
      BucketName: !Ref S3Bucket
```

Cloudformation sends the template and params to the lambda. The lambda parses
the template and picks out the S3 bucket. It pulls the current tags, derives a
new tag, then sets the tags again on that bucket. It does not alter the original
template.

## Development

### Contributions
Contributions are welcome.

Requirements:
* Install [pre-commit](https://pre-commit.com/#install) app
* Clone this repo
* Run `pre-commit install` to install the git hook.

### Create a local build

```bash
$ sam build --use-container
```

### Run locally

```bash
$ sam local invoke SetBucketTagsFunction --event events/event.json
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
sam build --build-dir build
```

## Deploy Lambda to S3
This requires the correct permissions to upload to the bucket in `./deploy-template.sh`.

```shell script
sam package --template-file build/template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file build/set-bucket-tags-macro.yaml

./deploy-template.sh
```



## Install Lambda into AWS
Create the following [sceptre](https://github.com/Sceptre/sceptre) file

config/prod/cfn-sc-actions-provider.yaml
```yaml
template_path: "remote/set-bucket-tags-macro.yaml"
stack_name: "set-bucket-tags-macro"
hooks:
  before_launch:
    - !cmd "curl https://s3.amazonaws.com/{{stack_group_config.admincentral_cf_bucket}}/it-lambda-set-bucket-tags/master/set-bucket-tags-macro.yaml --create-dirs -o templates/remote/set-bucket-tags-macro.yaml"
```

Install the lambda using sceptre:
```bash script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/cfn-sc-actions-provider.yaml
```


```

## Author

[Tess Thyer](https://github.com/tthyer); Principal Data Engineer, Sage Bionetworks
