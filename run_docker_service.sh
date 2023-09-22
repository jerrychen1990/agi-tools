TAG=${TAG}
echo "stoping old service"
sudo docker ps | grep agi-tools | awk '{print $1}' | xargs docker stop
sleep 1
echo "starting new service"
target=agi-tools:$TAG
cmd="sudo docker run -idt -p8501:8501 $target"
echo $cmd
eval $cmd
echo "done"


