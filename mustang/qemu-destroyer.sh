
if [ "$#" -ne 2 ]; then
    echo "usage: $0 lowindx highidx"
fi


PORTBASE=8900


#echo "To kill all QEMU instances:"
#echo "kill ${pids[*]}"
echo "killing all QEMU instances..."


for i in $(seq $1 $2); do
    pid=$(ps aux|grep $((PORTBASE+i))-|grep -v grep | awk '{print $2}')
    pids[$i]=$pid
    kill $pid
done
