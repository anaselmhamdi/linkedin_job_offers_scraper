# Linkedin Job offer scraper

## Description

Scrapes job offers from Linkedin everyday.

## Installation

You need to have serverless installed globally and configured to run with AWS.

Run `npm i -g serverless` and `serverless config` afterwards.

Run `npm i` to install the app requirements.

For the app to work you need to edit the lambda execution role (`role: arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/lambda-execution-role`) to a lambda execution role that has the [right to invoke lambda functions.](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)

Run `sls deploy` to deploy it.
