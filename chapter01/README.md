# Hosting a Jupyter environment with Docker
It is out of the scope of this book to discuss all the details of Docker, but briefly, Docker is a tool that allows you to set up virtualized servers that are called containers. 

The main parts of the setup process are several files:
- Dockerfile - a text file that lists the basic setup instructions for the virtual machine
- environment.yml - a file listing the python dependencies as installed by conda
- run_notebook.sh - a script to run your notebook from inside the container

Add the following three files to an empty directory:
## Dockerfile

```bash
#Dockerfile
FROM continuumio/miniconda3
ADD ./run_notebook.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/run_notebook.sh
&& chmod -R 777 /usr/local/*
RUN apt update -qq && apt install -y libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 build-essential vim curl wget libhdf5-dev libhdf5-serial-dev cython3 python-h5py 
RUN useradd -m docker -s /bin/bash -p '*' && chown -R 1000:1000 /opt/conda
USER docker
RUN conda -f /home/docker/tabiri/environment.yml && echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
CMD /bin/bash /usr/local/bin/run_notebook.sh
```

## environment.yml
```bash
# environment.yml
name: env
channels:
 - defaults
dependencies:
 - pip=19.3.1=py37_0
 - protobuf=3.9.2=py37he6710b0_0
 - python=3.7.0=h6e4f718_3
 - setuptools=41.6.0=py37_0
 - sqlite=3.30.1=h7b6447c_0
 - tensorboard=2.0.0
 - tensorflow=2.0.0
 - tensorflow-base=2.0.0
 - tensorflow-estimator=2.0.0
 - pip:
   - torch==1.3.1
   - numpy==1.18.0
   - pandas==0.25.3
   - scikit-learn==0.21.3
   - scipy==1.2.0
prefix: /opt/conda/envs/env
```

## run_notebook.sh
```bash
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
```

You can add mount parameters to the run command with the -v option. This is useful if you want the docker container to share directories with the host machine. Otherwise, you can copy files using the docker-copy command