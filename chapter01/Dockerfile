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