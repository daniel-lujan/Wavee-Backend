# Wavee Backend
This is a demo Python-Flask backend implementation for Music Identification. Implements Shazam algorithm as described in [An Industrial-Strength Audio Search Algorithm](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf).
- [Main notebook]( https://colab.research.google.com/drive/1w5HK-IM3Xicz4tUH1ZckwTCUDeDXX-Ln)
- [Wavee Frontend](https://github.com/daniel-lujan/Wavee-Frontend)
## Quick Start with Pip
> <font color="#ff2a00">**Note**: </font> Built with Python 3.10, using other versions might lead to incompatibility issues.  [Use Docker instead](#quick-start-with-docker).
### 1. Clone the repository
```console
root@user:~$ git clone https://github.com/daniel-lujan/Wavee-Backend.git
root@user:~$ cd Wavee-Backend
```
### 2. Create virtual environment
You can now optionally create a virtual environment.
```console
root@user:~$ python -m venv venv
root@user:~$ venv/Scripts/activate.bat
```
### 3. Install dependencies
```console
root@user:~$ pip install -r "requirements.txt"
```
### 4. Start server
```console
root@user:~$ python app.py
```
The API is should now be available at `http://localhost:5000`.

## Quick Start with Docker
### 1. Clone the repository
```console
root@user:~$ git clone https://github.com/daniel-lujan/Wavee-Backend.git
root@user:~$ cd Wavee-Backend
```
### 2. Build and start container
```console
root@user:~$ docker build -t wavee-backend .
root@user:~$ docker run -p 8080:8080 wavee-backend
```
The API is should now be available at `http://localhost:8080`.
