## adbSync

[![Build Status](http://build.eberlein.io:8080/job/adbSync/badge/icon)](http://build.eberlein.io:8080/job/adbSync/)

- sync (specific) sdcard (folders / files)
- sync (specific) installed apps
- sync wifi configuration

### how to ...

#### ... use it
```
./sync.py --help
-a   | --apps
-m   | --media
-w   | --wifi               | needs su enabled for adb

e.g:
./sync.py -a -m -w
           |>>|>>\>saves wifi stuff (passwords/etc)
           |>>\>copies /sdcard/
            \>pulls all non system apps
```