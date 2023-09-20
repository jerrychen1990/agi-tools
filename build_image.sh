TAG=${TAG}
target=agi-tools:$TAG
echo build image $target
cmd="sudo docker build -t $target -f docker/DockerFile ."
echo $cmd
eval $cmd


