yarn build
aws s3 sync build/ s3://gptif-site/
