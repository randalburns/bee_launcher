if [ "$#" -ne 2 ]; then
    echo "usage: $0 lowindx highidx"
fi

#BASEIMAGE=base-mpi.qcow
BASEIMAGE=dkrubu16.qcow2
PORTBASE=8900
VNCBASE=100
MPORT=1234 # multicast port
for i in $(seq $1 $2); do
    ../qemu-2.2.1/qemu-img create -f qcow -o backing_file=$BASEIMAGE $i.qcow
done

for i in $(seq $1 $2); do
    MAC=$(printf '%02x' $i)
	./../qemu-2.2.1/x86_64-softmmu/qemu-system-x86_64 -daemonize -vnc none -m 1024 -net nic,macaddr=02:00:00:00:00:$MAC -net socket,mcast=230.0.0.1:$MPORT\
                     -net nic,vlan=1 -net user,vlan=1,hostfwd=tcp:127.0.0.1:$((PORTBASE+i))-:22 \
                     $i.qcow 
done

echo "launched VMs from $1 to $2"
echo "PORTBASE=$PORTBASE VNCBASE=$VNCBASE"

echo "To delete all VM images:"
echo "rm {$1..$2}.qcow"

for i in $(seq $1 $2); do
    pid=$(ps aux|grep $((PORTBASE+i))-|grep -v grep | awk '{print $2}')
    pids[$i]=$pid
done

echo "To kill all QEMU instances:"
echo "kill ${pids[*]}"
