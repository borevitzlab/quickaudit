# quickaudit

Does a quick audit of images


```
# install zbar C library. sudo apt install libzbar-dev on debian, sudo pacman 
pip3 install zbarlight numpy rawpy pillow
find -type f -iname \*.jpg | python3 ./quickaudit.py | tee image_audit.tsv
```
