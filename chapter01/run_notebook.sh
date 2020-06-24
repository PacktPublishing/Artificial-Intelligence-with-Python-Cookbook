#!/bin/bash
# run_notebook.sh 
## Don't attempt to run if we are not root
## EUID stands for Effective User ID
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi 

## Set defaults for environmental variables in case they are undefined 
USER=${USER:=jupyter}
PASS=${PASS:=jupyter}
USERID=${USERID:=1000}
USERGID=${USERGID:=1000}
CONFIG=".jupyter/jupyter_notebook_config.py" 

if [ "$USERID" -ne 0 ]; then
  echo "creating new $USER with UID $USERID" 
  groupadd -g $USERGID $USER
  useradd -m -u $USERID -g $USERGID $USER 
  echo "$USER added to sudoers"
fi
cd /home/$USER
mkdir -p .jupyter
/bin/cat <<EOF >$CONFIG
from notebook.auth import passwd
c = get_config()
passw = passwd('$PASS')
c.NotebookApp.password = passw
c.IPKernelApp.pylab = 'inline'
c.NotebookManager.save_script = True
c.NotebookApp.open_browser = False
c.NotebookApp.port = 9999
c.NotebookApp.ip = '0.0.0.0'
# avoid restart on slow connections:
c.NotebookApp.tornado_settings = {'kernel_info_timeout': 60}
EOF
chown -R $USER:$USER .jupyter
su $USER -c "jupyter notebook"
Then build your container and run it:
docker build -t jupyter .
Once that's finished you can run your container like this:
PORT=5050 docker run -d \
--runtime=nvidia \ # optionally: if you rely on the nvidia docker binaries
--name "jupyter_${USER}_${PORT}" \
-p $PORT:9999 \ 
-e USER=$USER \ 
-e USERGID=$(id -g $1) \ 
-e USERID=$(id -u $1) \ 
-e PASS=$PASS jupyter \ 
/usr/local/bin/run_notebook.sh