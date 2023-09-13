# Eraserr

![image](https://github.com/everettsouthwick/Eraserr/assets/8216991/a45ae766-6a59-4d8d-b4e0-5237a3ffb3c9)

Eraserr is a Python script designed to help keep your Plex servers clean. It deletes unwatched or stale media by leveraging the functionality of Radarr, Sonarr, and Overseerr.

## Table of Contents
* [Installation](#installation)
    * [Prerequisites](#prerequisites)
* [Usage](#usage)
    * [Docker](#docker)
        * [Pulling the image](#pulling-the-image)
        * [Running the Container](#running-the-container)
* [Configuration](#configuration)

## Installation

### Prerequisites

- [Python 3.7+][0]
- [Pip][1]

1. First, clone the script to your machine and navigate to the resulting directory:

```shell
git clone https://github.com/everettsouthwick/Eraserr.git
cd Eraserr
```
2. Then, install the required packages to run the script:

```shell
pip install -r requirements.txt
```

## Usage

To use the script, run the following command:
```shell
python eraserr.py
```

### Docker

#### Pulling the image

You can pull the latest container image from the [Docker repository][2] by running the following command:

```shell
docker pull ecsouthwick/eraserr
```
To pull the develop branch from the Docker repository, add the `:develop` tag to the above command:

```shell
docker pull ecsouthwick/eraserr:develop
```

#### Running the Container

Once you have pulled the image from docker, you may use the following command to run the container:

```shell
docker run -d --name eraserr --volume /path/to/config.json:/app/config.json ecsouthwick/eraserr
```

**Note**: The recommended restart policy for the container is `on-failure` or `no`.

## Configuration

1. Copy `config.example.json` to `config.json`. 
2. See [CONFIGURATION.md](CONFIGURATION.md) for detailed instructions on setting up `config.json`.

[0]: https://www.python.org/downloads/ "Python 3.7+"
[1]: https://pip.pypa.io/en/stable/installation/ "Pip"
[2]: https://hub.docker.com/r/ecsouthwick/eraserr "Docker repository"
