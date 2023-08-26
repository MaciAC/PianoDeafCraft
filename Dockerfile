FROM mtgupf/essentia

RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install jupyter
RUN pip3 install mir_eval

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]
