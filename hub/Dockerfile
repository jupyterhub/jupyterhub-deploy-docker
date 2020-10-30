FROM debian:9

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential curl git libcap-dev sudo
RUN git config --global user.email nobody@nowhere.com
RUN git config --global user.name Nobody

RUN git clone -b 2.0 git://github.com/ocaml/opam /tmp/opam
RUN cd /tmp/opam && make cold && mkdir -p /usr/local/bin && cp /tmp/opam/opam /usr/local/bin/opam && chmod a+x /usr/local/bin/opam && rm -rf /tmp/opam
RUN ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime
RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/mirror-retry 
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install rsync unzip nano libcap-dev libx11-dev m4
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN adduser --uid 4224 --disabled-password --gecos '' instructor
RUN passwd -l instructor
USER instructor
ENV HOME=/home/instructor
WORKDIR /home/instructor
RUN mkdir .ssh
RUN chmod 700 .ssh

RUN echo 'wrap-build-commands: []' > ~/.opamrc
RUN echo 'wrap-install-commands: []' >> ~/.opamrc
RUN echo 'wrap-remove-commands: []' >> ~/.opamrc
RUN echo 'required-tools: []' >> ~/.opamrc
RUN git config --global user.email nobody@nowhere.com
RUN git config --global user.name Nobody

RUN git clone git://github.com/ocaml/opam-repository /home/instructor/opam-repository
RUN opam init -k git --disable-sandboxing -a /home/instructor/opam-repository --bare && opam switch create 4.10 ocaml-base-compiler.4.10.0 && opam switch 4.10
RUN opam install -y depext

ARG JUPYTERHUB_VERSION=1.0.0
ENV OPAM_SWITCH_PREFIX='/home/instructor/.opam/4.10' \
    CAML_LD_LIBRARY_PATH='/home/instructor/.opam/4.10/lib/stublibs:/home/instructor/.opam/4.10/lib/ocaml/stublibs:/home/instructor/.opam/4.10/lib/ocaml' \
  OCAML_TOPLEVEL_PATH='/home/instructor/.opam/4.10/lib/toplevel' \
  MANPATH=':/home/instructor/.opam/4.10/man' \
  PATH='/home/instructor/.opam/4.10/bin:/home/instructor/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'

USER root
RUN apt-get install -y python3-pip vim debianutils libgmp-dev libzmq3-dev m4 perl pkg-config zlib1g-dev pandoc texlive-xetex graphviz imagemagick libpq-dev

USER instructor
RUN pip3 install --no-cache jupyterhub==$JUPYTERHUB_VERSION notebook jupyter_contrib_nbextensions jupyter_nbextensions_configurator RISE nbgrader psycopg2 nbconvert
RUN pip3 install git+https://github.com/jonludlam/nbgrader.git@ocaml-autograder-fixes2
RUN opam install -y merlin bos ocamlformat
#ENTRYPOINT []
RUN sh -c 'jupyter contrib nbextension install --user'
RUN sh -c 'jupyter-nbextension install rise --py --user'
RUN sh -c 'jupyter-nbextension enable rise --py --user'
RUN sh -c 'jupyter nbextension install nbgrader --py --user'
RUN opam pin add -y jupyter -k git https://github.com/jonludlam/ocaml-jupyter#setsid
RUN git clone https://github.com/jonludlam/focs-support.git
RUN cd focs-support && dune build && dune install
RUN rm -rf focs-support
COPY custom.tar.gz .jupyter/
COPY ocamlinit .ocamlinit
COPY update.sh .local/bin/update.sh
COPY start-custom.sh /usr/local/bin/
COPY start-singleuser-custom.sh .local/bin/
COPY start-single.sh .local/bin/start-single.sh
COPY ./students.csv /tmp/

USER root
COPY ./nbgrader_config.py /etc/jupyter/ 
RUN cd .jupyter && tar xvf custom.tar.gz
RUN ocaml-jupyter-opam-genspec
RUN .local/bin/jupyter kernelspec install --name ocaml-jupyter "$(opam config var share)/jupyter"

ENV OCAML_JUPYTER_LOG debug
ENTRYPOINT []
CMD /home/instructor/.local/bin/start-single.sh

RUN echo 4
#RUN pip3 install git+https://github.com/jonludlam/jupyter_client.git@test

