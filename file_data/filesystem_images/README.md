## Mount/Umount Filesystem Images ##
Will handle partition offsets with in the image file, and multiple partitions.
These will be mounted in *mounted_\<image filename\>/\<partition label\>*

### Mount ###
    sudo ./img_mount /path/to/image

### Unmount image ###
    sudo ./img_mount /path/to/image


### Issues ###
Script will stop on error. If problem occurs use *sudo losetup -a* and *mount* to check for what has been created to this point, or not cleaned up so far. Use *umount* and *losetup -d \<loop\>* for clean up.
