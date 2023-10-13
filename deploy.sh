TAG=$(date '+%Y%m%d%H%M%S')
echo "build image"
target=agi-tools:$TAG
echo build image $target
cmd="sudo docker build -t $target -f docker/DockerFile ."
echo $cmd
eval $cmd

echo "stoping old service"
sudo docker ps | grep 8501 | awk '{print $1}' | xargs docker stop
sleep 1
echo "starting new service"
cmd="sudo docker run -idt -p8501:8501 -v ./config:/config -v ./logs:/logs  $target"
echo $cmd
eval $cmd
echo "done"
tail -f ./logs/st_tool.log


