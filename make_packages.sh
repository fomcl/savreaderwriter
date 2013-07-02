#!/bin/bash

savReaderWriter=~/Desktop/savReaderWriter
cd $savReaderWriter
version=$(cat VERSION)

echo "***********************************************************************"
echo "Start running setup.py with bdist_deb option"
echo "***********************************************************************"

# temporarily stash the irrelevant I/O files in /tmp
folders="aix64 hpux_it lin64 sol64  zlinux64 macos win32 win64"
for folder in $folders; do mv $savReaderWriter/savReaderWriter/spssio/$folder /tmp; done
python setup.py --command-packages=stdeb.command bdist_deb
src=$savReaderWriter/deb_dist/python-savreaderwriter_$version-1_all.deb
dst=$savReaderWriter/dist/savReaderWriter-$version.lin32.deb
mv $src $dst
for folder in $folders; do mv /tmp/$folder $savReaderWriter/savReaderWriter/spssio; done
rm -r $savReaderWriter/deb_dist

echo "***********************************************************************"
echo "Start running setup.py with bdist_wininst option (correct???)"
echo "***********************************************************************"
folders="aix64 hpux_it lin32 lin64 sol64  zlinux64 macos win64"
for folder in $folders; do mv $savReaderWriter/savReaderWriter/spssio/$folder /tmp; done
python setup.py bdist_wininst
for folder in $folders; do mv /tmp/$folder $savReaderWriter/savReaderWriter/spssio; done

echo "***********************************************************************"
echo "Start running setup.py with sdist gztar,zip"
echo "***********************************************************************"

python setup.py sdist --formats=gztar,zip

echo "***********************************************************************"
echo "Start running setup.py with build_sphinx (documentation)"
echo "***********************************************************************"

python setup.py check build_sphinx --source-dir=savReaderWriter/documentation -v


