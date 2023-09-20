echo "initializing apt packages..."
apt update && \
    apt install -yq tzdata && \
    apt install -y git ninja-build openssh-server && \
    apt install -y pdsh vim rsync net-tools && \
    apt install -y libibverbs-dev && \
    apt clean

echo "setting timezone"
ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && dpkg-reconfigure -f noninteractive tzdata
