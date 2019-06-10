#!/usr/bin/python

import sys,time
import boto3

if len(sys.argv) == 1 or len(sys.argv) < 3:
  print "Command: python ebs.py <'instance-id'> <'volume-id'>"
  print "Perform the following steps before executing the script"
  print "1) unmount the /apps mount"
  print "2) execute: vgchange -an rootvg "
  quit()
else:
  instanceId=sys.argv[1]
  volumeId=sys.argv[2]

#Establishing a connection
ec2 = boto3.resource('ec2')
volume = ec2.Volume(volumeId)
instance = ec2.Instance(instanceId)

try:
  az = volume.availability_zone
except:
  print "Enter the correct VolumeID"
  quit()

#Detaching the Volume

print "Make sure the volume is unmounted in the instance and the command 'vgchange -an rootvg' was executed, Enter 'Yes' to proceed"
userresponse=raw_input()
if userresponse == "yes":
   print "Detaching the Volume: "+volumeId+" from the instanceID: "+instanceId
   try:
       response = volume.detach_from_instance(InstanceId=instanceId)
   except:
       print "\nVolume: "+volumeId+"  Already detached ?? Please check\n"
       quit()
   if response['ResponseMetadata']['HTTPStatusCode'] == 200:
       print "Volume detached successfully\n"
   else:
      print "Volume not detached, Please check\n"
      quit()

else:
   print "Exiting"
   quit()


#Snapshot Creation

print "\nCreating the Snapshot for "+volumeId+":"
Descrip = "Initial snapshot for WCMS Instance "+instanceId
snap = volume.create_snapshot(Description=Descrip)
snapshotStatus = snap.state
while snapshotStatus == "pending":
     print "snapshot ID: "+snap.id+" creation in progress"
     time.sleep(5)
     snapshot = ec2.Snapshot(snap.id)
     snapshotStatus = snapshot.state
if snapshotStatus == "completed":
     print "Snapshot "+snap.id+" created successfully\n"
else:
    print "Snapshot creation failed"
    quit()


#gp2 volume creation

print "Creating gp2 volume from snapshot "+snap.id+":"
client = boto3.client('ec2')
volresponse = client.create_volume(SnapshotId=snap.id,AvailabilityZone=az,VolumeType='gp2')
newVolumeID = volresponse['VolumeId']
volumeStatus = volresponse['State']
while volumeStatus == "creating":
     print "Volume ID: "+newVolumeID+" creation in progress"
     time.sleep(5)
     newVol = ec2.Volume(newVolumeID)
     volumeStatus = newVol.state
if volumeStatus == "available":
    print "gp2 Volume "+newVolumeID+" created successfully\n"
else:
    print "Error in creating the Volume"
    quit()


#Attach the newly created gp2 volume to the instance

print "Attaching Volume "+newVolumeID+" to the instance "+instanceId+":"
attachResponse = instance.attach_volume(VolumeId=newVolumeID,Device="/dev/sdc")
attachStatus = attachResponse['State']
while attachStatus == "attaching":
    print "Attachment in progress"
    time.sleep(5)
    vol = ec2.Volume(newVolumeID)
    attachStatus = vol.state
if attachStatus == "in-use":
   print "Volume: "+newVolumeID+" successfully attached to instance "+instanceId+"\n"
else:
   print "Error in attaching the Volume, please check"
   quit ()

#Delete the Magnetic volume
print "Deleting the Volume ID "+volumeId+":"
volMagnetic = ec2.Volume(volumeId)
response = volume.delete()
print "Executed the Volume delete command, it should disapper in few moments !\n"

#Delete the Snapshot
print "Deleting the snapshot "+snap.id+":"
snapDelete = ec2.Snapshot(snap.id)
response = snapshot.delete()
print "Executed the snapshot delete command, it should disapper in few moments !\n"
