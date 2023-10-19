# Docker images

## ISIS/ASP

Build an "ISIS3" image (`singleuser:isis`) using default values:

```bash
docker build -t singleuser:isis -f isis.dockerfile .
```

You can set some attributes to fine-tune the building ("argument: default"):

- `ISIS_VERSION`: `7.1.0`
- `ASP_VERSION`: `3.2.0`
- `BASE_IMAGE`: `jupyter/minimal-notebook:latest`
- `JUPYTERHUB_VERSION`: `3.0.0`

JupyterHub is (minimally) installed at specific version to guarantee compatibily
with a same-versioned JupyterHub spawning _this_ container(s).

For example, to build an (isis/asp) image using instead jupyter `scipy-notebook`:

```bash
docker build -t singleuser:isis-scipy \
    --buil-arg jupyter/scipy-notebook \
    -f isis.dockerfile .
```

## GISPY

To build the "gispy" image, named `singleuser:gispy`:

```bash
docker build -t singleuser:gispy -f gispy.dockerfile .
```
