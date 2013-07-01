:: make packages that can be built under/for windows
python setup.py sdist --formats=gztar,zip
del .\build\lib\savReaderWriter\spssio\aix64 /s /q
del .\build\lib\savReaderWriter\spssio\hpux_it /s /q
del .\build\lib\savReaderWriter\spssio\lin32 /s /q
del .\build\lib\savReaderWriter\spssio\lin64 /s /q
del .\build\lib\savReaderWriter\spssio\macos /s /q
del .\build\lib\savReaderWriter\spssio\sol64 /s /q
del .\build\lib\savReaderWriter\spssio\win64 /s /q
del .\build\lib\savReaderWriter\spssio\zlinux64 /s /q
python setup.py bdist --formats=wininst
del .\build /s /q