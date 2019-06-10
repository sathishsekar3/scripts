#!/bin/bash
## LVM snapshot script - ssathish

function delete_snapshot {
echo "Checking for snapshot older than 3 day's"
OLDDATE=`/bin/date --date='3 day ago' "+%y-%m-%d"`
OLDSNAP=`/sbin/lvs | grep $OLDDATE | /bin/awk '{print $1}'`
if [ ${#OLDSNAP[0]} -eq 0 ]
 then
 echo "Snapshot not present"
 else
   for OLDSNAP in ${OLDSNAP[@]}
    do
     echo "Deleting the snapshot $OLDSNAP" | tee -a /apps/scripts/lvm/wcms-apps-`date "+%y-%m-%d"`.log
     /sbin/lvremove -f /dev/rootvg/$OLDSNAP | tee -a /apps/scripts/lvm/wcms-apps-`date "+%y-%m-%d"`.log
    done
fi
}

function check_space {
AVAILABLE=`/sbin/vgs | grep rootvg | awk '{print $7}' | cut -d . -f1`
 if [ $AVAILABLE -gt 20 ]
  then
   echo "Space available, proceeding" | tee -a /apps/scripts/lvm/wcms-apps-`date "+%y-%m-%d"`.log
  else
   echo "Snapshot not taken due to insufficient VG space" | /bin/mail -s "`hostname`: Insufficient VG space" ssathish@adobe.com
   exit 1
 fi
}

function pretasks {
 if [ -d /mnt/backup ]
  then
   if /bin/mount | grep -i /mnt/backup > /dev/null
    then
     echo "Unmounting /mnt/backup" | tee -a /apps/scripts/lvm/wcms-apps-`date "+%y-%m-%d"`.log
     /bin/umount /mnt/backup
    fi
  else
    mkdir -p /mnt/backup
 fi
}

function create_snapshot {
DATE=`/bin/date "+%y-%m-%d-%H-%M"`
/sbin/lvcreate --size 20G --snapshot --name wcms-apps-$DATE /dev/rootvg/apps > /dev/null
if [ `/bin/echo $?` -eq 0 ]
 then
 mount -o ro /dev/rootvg/wcms-apps-$DATE /mnt/backup
 echo "created snapshot: wcms-apps-$DATE and mounted under /mnt/backup" | tee -a /apps/scripts/lvm/wcms-apps-`date "+%y-%m-%d"`.log
 else
 echo "Snapshot creation failed" | /bin/mail -s "`hostname`: Snapshot creation failed" ssathish@adobe.com
fi
}

delete_snapshot
check_space
pretasks
create_snapshot
