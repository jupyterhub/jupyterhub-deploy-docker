FROM ocaml/opam2:debian-stable
ARG JUPYTERHUB_VERSION=1.0.0
ENV OPAM_SWITCH_PREFIX='/home/opam/.opam/4.08' \
    CAML_LD_LIBRARY_PATH='/home/opam/.opam/4.08/lib/stublibs:/home/opam/.opam/4.08/lib/ocaml/stublibs:/home/opam/.opam/4.08/lib/ocaml' \
  OCAML_TOPLEVEL_PATH='/home/opam/.opam/4.08/lib/toplevel' \
  MANPATH=':/home/opam/.opam/4.08/man' \
  PATH='/home/opam/.opam/4.08/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

RUN opam switch 4.08
RUN cd /home/opam/opam-repository && git pull origin master
RUN opam update
RUN sudo apt-get update
RUN sudo apt-get install -y python3-pip vim debianutils libgmp-dev libzmq3-dev m4 perl pkg-config zlib1g-dev pandoc texlive-xetex graphviz imagemagick libpq-dev
RUN pip3 install --no-cache jupyterhub==$JUPYTERHUB_VERSION notebook jupyter_contrib_nbextensions jupyter_nbextensions_configurator RISE nbgrader psycopg2
RUN opam install -y jupyter merlin bos ocamlformat
RUN sudo -E /home/opam/.local/bin/jupyter kernelspec install --name ocaml-jupyter "$(opam config var share)/jupyter"
ENTRYPOINT []
WORKDIR /home/opam
RUN /home/opam/.local/bin/jupyter contrib nbextension install --user
RUN /home/opam/.local/bin/jupyter-nbextension install rise --py --user
RUN /home/opam/.local/bin/jupyter-nbextension enable rise --py --user
RUN /home/opam/.local/bin/jupyter nbextension install nbgrader --py --user
RUN sudo chown opam /home/opam/.jupyter/nbconfig/notebook.json
#RUN /home/opam/.local/bin/jupyter nbextension enable nbgrader --user --py
#RUN /home/opam/.local/bin/jupyter serverextension enable nbgrader --user --py
#COPY notebook.json /home/opam/.jupyter/nbconfig/notebook.json
COPY custom.tar.gz /home/opam/.jupyter/
COPY ocamlinit .ocamlinit
COPY update.sh update.sh
COPY start-custom.sh /home/opam/.local/bin/
COPY start-singleuser-custom.sh /home/opam/.local/bin/
COPY start-single.sh /home/opam/.local/bin/start-single.sh
COPY ./students.csv /tmp/
COPY ./nbgrader_config.py /etc/jupyter/ 
RUN cd /home/opam/.jupyter && tar xvf custom.tar.gz
WORKDIR /home/opam
USER root
ENV OCAML_JUPYTER_LOG debug
CMD /home/opam/.local/bin/start-single.sh

