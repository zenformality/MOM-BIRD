[app]
title = MOM BIRD
package.name = mombird
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,jpeg,wav,ogg,mp3,ttf,json

version = 0.1

requirements = python3,pygame

orientation = portrait
fullscreen = 1

android.permissions = INTERNET
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
