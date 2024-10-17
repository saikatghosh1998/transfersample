provider "aws" {
  region = "us-east-1"  # Adjust region as needed
}

# Create an IAM role for CodeBuild
resource "aws_iam_role" "codebuild_role" {
  name = "codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          Service = "codebuild.amazonaws.com"
        },
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

# Attach policies to the CodeBuild role
resource "aws_iam_role_policy" "codebuild_policy" {
  name   = "codebuild-policy"
  role   = aws_iam_role.codebuild_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = "*"
      }
    ]
  })
}

# Define the CodeBuild project with inline buildspec
resource "aws_codebuild_project" "app1_build" {
  name          = "app1-build"
  description   = "CodeBuild project triggered by S3 put events"
  service_role  = aws_iam_role.codebuild_role.arn

  source {
    type            = "NO_SOURCE"
    buildspec       = <<BUILD_SPEC
version: 0.2

phases:
  install:
    commands:
      - echo "Installing dependencies"
  pre_build:
    commands:
      - echo "Running pre-build commands"
  build:
    commands:
      - echo "Running build steps"
  post_build:
    commands:
      - echo "Build complete"
BUILD_SPEC
  }

  artifacts {
    type            = "NO_ARTIFACTS"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/standard:5.0"  # Use the latest image or as needed
    type            = "LINUX_CONTAINER"
  }

  build_timeout  = 30
}

# S3 bucket (for the trigger)
resource "aws_s3_bucket" "stati_file" {
  bucket = "stati_file"
}

# EventBridge rule for triggering the build on S3 put object event
resource "aws_cloudwatch_event_rule" "s3_put_event" {
  name        = "s3-put-object-trigger"
  description = "Triggers CodeBuild on S3 put object"
  event_pattern = jsonencode({
    "source": ["aws.s3"],
    "detail-type": ["AWS API Call via CloudTrail"],
    "detail": {
      "eventSource": ["s3.amazonaws.com"],
      "eventName": ["PutObject"],
      "requestParameters": {
        "bucketName": ["stati_file"]
      },
      "requestParameters": {
        "key": [{
          "prefix": "app1/"
        }]
      }
    }
  })
}

# EventBridge target (CodeBuild)
resource "aws_cloudwatch_event_target" "codebuild_target" {
  rule      = aws_cloudwatch_event_rule.s3_put_event.name
  arn       = aws_codebuild_project.app1_build.arn
}

# Grant permissions for EventBridge to invoke CodeBuild
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_codebuild_project.app1_build.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.s3_put_event.arn
}
