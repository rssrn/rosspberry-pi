
So I have: a pi 3B, a 16GB microSD card, an ethernet cable, a power supply, and a linux laptop (with microSD card reader).

1) Download and flash an OS (picked raspbian as the obvious choice) to the microSD using Etcher and the [instructions](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md) from raspberrypi.org.

At time of writing, latest available was 2017-04-10-raspbian-jessie so that's what I installed.  I went with the 'with pixel' version because, hey I've got enough space and it might be useful or interesting.


2) I'm doing a headless install because I don't have a monitor or USB keyboard.  So I need to enable ssh automatically when the pi starts up.  If raspbian sees a file called ssh in the root directory of the boot partition it will enable this, so mount the sd card and:

```touch /media/ross/boot/ssh```

Then unmount and insert the sd card in the pi.

3) Attach power and ethernet to the pi and switch on.  The lights come on!

I now see a 'raspberrypi' device on my router's web interface, so I know the IP address it's been assigned.

```ssh pi@192.168.1.3```

Change the password.

4) For reference: memory and disk stats after a basic install with 16GB card:

```
pi@raspberrypi:~ $ free -h
             total       used       free     shared    buffers     cached
Mem:          925M       410M       515M       6.5M        78M       243M
-/+ buffers/cache:        88M       837M
Swap:          99M         0B        99M
pi@raspberrypi:~ $ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        15G  3.6G   11G  27% /
devtmpfs        459M     0  459M   0% /dev
tmpfs           463M     0  463M   0% /dev/shm
tmpfs           463M  6.3M  457M   2% /run
tmpfs           5.0M  4.0K  5.0M   1% /run/lock
tmpfs           463M     0  463M   0% /sys/fs/cgroup
/dev/mmcblk0p1   41M   21M   21M  51% /boot
tmpfs            93M     0   93M   0% /run/user/1000
```

5) Basic setup

```sudo raspi-config```

My locale is already the default en_GB UTF8.  Set hostname to `oak`.  Reboot.

6) I'm now happy that the pi doesn't have any obvious defects, so I'll put it in a case for protection.

7) Will be useful for the pi to have a static IP address.  Setup router accordingly http://192.168.1.254/expert_user.html - I restricted the DHCP range to 
192.168.1.1 through 192.168.1.199 - leaving me 192.168.1.200+ for static IP addresses.

Then appending to /etc/dhcpcd.conf:

```
interface eth0
static ip_address=192.168.1.200/24
static routers=192.168.1.254
static domain_name_servers=192.168.1.254
```

and reboot

Also add to /etc/resolv.conf on laptop

Also setup ssh via public key

8) Install Nagios to get some basic monitoring going

```apt install nagios3```

Also incidentally installs apache.

(Nagios 4 is more recent but not packaged for raspbian at the time of writing)

http://oak/nagios3
-A --ignore-ereg-path='.*gvfs.*'
Key config file defining services: /etc/nagios3/conf.d/localhost_nagios2.cfg

Had to work around gvfs issue by ignoring gvfs files (edit /etc/nagios-plugins/config/disk.cfg appending something like `-A --ignore-ereg-path='.*gvfs.*'` to the check_disk command lines

Also set the generic service template to check every 60 minutes rather than the default of 5 minutes.

TODO: Shinken, Graphite, Gmail


9) Not sure if I really need to see the raspbian desktop, but installed vnc server anyway.

Note - display resolution can be changed in raspi-config advanced settings


10) Make own nagios plugin to monitor temperature

See [check_temperature](nagios/plugins/check_cpu_temperature)

Put above script in /usr/lib/nagios/plugins/check_cpu_temperature

Create /etc/nagios-plugins/config/cpu_temperature.cfg
Edit /etc/nagios3/conf.d/localhost_nagios2.cfg to add the service


11) Get outgoing mail working using ssmtp and heirloom-mailx.  For filters on the gmail side, note X-Google-Original-From will reflect the sending unix user on the pi (pi, nagios, root etc).

12) Start using ansible for deployment - see [ansible config](ansible)
