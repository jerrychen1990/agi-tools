TAG=${TAG}
echo "stoping old service"
sudo docker ps | grep 8501 | awk '{print $1}' | xargs docker stop
sleep 1
echo "starting new service"
target=agi-tools:$TAG
cmd="sudo docker run -idt -p8501:8501 -v ./config:/config $target"
echo $cmd
eval $cmd
echo "done"


