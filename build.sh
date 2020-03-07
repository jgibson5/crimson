#! /bin/sh

docker build --build-arg AWS_ACCESS_KEY=$AWS_ACCESS_KEY --build-arg AWS_SECRET_KEY=$AWS_SECRET_KEY -t crimson/site .

$(aws ecr get-login-password | docker login --username AWS --password-stdin 245166042509.dkr.ecr.us-east-1.amazonaws.com)

docker tag crimson/site:latest 245166042509.dkr.ecr.us-east-1.amazonaws.com/crimson/site:latest
docker push 245166042509.dkr.ecr.us-east-1.amazonaws.com/crimson/site:latest