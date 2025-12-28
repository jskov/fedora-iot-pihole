# Reverse Proxy RPM for mada.dk on Fedora IOT

I use this RPM for layering in Fedora IOT.

It runs [pihole](https://pi-hole.net/) in a [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) with a preliminary service to fix the integration with the system (user setup).

>[!NOTE]
>This project is Open Source. But I am not interested in providing support or help in any form.
>You are welcome to fork it though!

# Dev notes

## Build RPM

Set up toolbox:

```console
$ distrobox create -i registry.fedoraproject.org/fedora:43 -n fedora-tito --pre-init-hooks "dnf install -y diceware copr-cli copr-rpmbuild rpmbuild selinux-policy-devel tito"
```

Build rpm locally (note that this builds on *committed GIT data only!*):

```console
$ distrobox enter fedora-tito
$ cd ROOT OF REPOSITORY
$ rpmlint pihole.spec
$ rm -rf /tmp/tito/x86_64/ ; tito build --rpm --test
```

Update spec version (--keep-version to keep manually maintained version in spec file):

```console
$ export EDITOR=vi
$ tito tag --keep-version

# This will result in a tag on the git repository, named 'reverse-proxy-$WHATEVER'
# And an updated file .tito/packages/reverse-proxy

# Note that without the above, the build command will fail with the message:
#  ERROR: Unable to lookup latest package info.
#  Perhaps you need to tag first?

$ git push --follow-tags origin
$ rm -rf /tmp/tito/x86_64/ ; tito build --rpm
```


## Installation

### RPM

Install the RPM; the --uninstall allows updating an existing layered rpm (older version):

```console
# Store the RPM locally - do not delete, as long as the RPM is included
$ scp /tmp/tito/x86_64/pihole* mada:/tmp/

$ mv /tmp/pihole-2025.11.1-1.git.1.9b738e6.fc42.x86_64.rpm ~/_local_layers/pihole/
$ sudo rpm-ostree install /var/home/jskov/_local_layers/pihole/pihole-2025.11.1-1.git.1.9b738e6.fc42.x86_64.rpm --uninstall pihole
```

Enable the prep-service; the systemd policy for enabling a service does not appear to work (on Atom?):

```console
$ sudo systemctl enable pihole-prep
$ sudo systemctl reboot
```

The user process should be running after restart:

```console
$ sudo systemctl --user -M pihole@ status pihole
● pihole.service
     Loaded: loaded (/etc/containers/systemd/users/3020/pihole.container; generated)
    Drop-In: /usr/lib/systemd/user/service.d
             └─10-timeout-abort.conf
     Active: active (running) since Sun 2025-12-28 11:57:57 CET; 2min 13s ago
 Invocation: 166765845413463db9445ba25ccfefb0
   Main PID: 1126
      Tasks: 19 (limit: 9127)
     Memory: 123.7M (peak: 129.6M)
        CPU: 2.819s
     CGroup: /user.slice/user-3020.slice/user@3020.service/app.slice/pihole.service
             ├─libpod-payload-8dfe50a6231edd323d9893fc36f0c9a19e5a82ce23485c449d9fc1b150e5622d
             │ ├─1129 /bin/bash /usr/bin/start.sh
             │ ├─1174 /usr/sbin/crond
             │ ├─1223 /bin/bash -c "/usr/bin/pihole-FTL no-daemon >/dev/null"
             │ ├─1227 /usr/bin/pihole-FTL no-daemon
             │ └─1365 tail -F -c +121 -- /var/log/pihole/FTL.log
             └─runtime
               ├─1117 /usr/bin/pasta --config-net -t 11053-11053:53-53 -t 11443-11443:443-443 -u 11053-11053:53-53 --dns-forward 169.254.1.1 -T none -U none --no-map-gw --quiet --netns /run/user/3020/netns/netns-d7f8afef-0696-79aa-4978-3cf0805ee193 --map>
               └─1126 /usr/bin/conmon --api-version 1 -c 8dfe50a6231edd323d9893fc36f0c9a19e5a82ce23485c449d9fc1b150e5622d -u 8dfe50a6231edd323d9893fc36f0c9a19e5a82ce23485c449d9fc1b150e5622d -r /usr/bin/crun -b /var/home/pihole/.local/share/containers/sto>
```

See its log output with:

```console
$ journalctl -f -n 1000 | grep pihole
```

### Firewall

Forward port 53 (TCP+UDP) on the host to the container.

```console
$ sudo firewall-cmd --add-forward-port=port=53:proto=udp:toport=11053 --permanent
$ sudo firewall-cmd --add-forward-port=port=53:proto=tcp:toport=11053 --permanent
```

(the web console is accessed via the reverse-proxy).

## Notes

### Debugging

Start the container manually to play with its options like this:

```console
$ sudo su - pihole
[pihole]$ /usr/lib/systemd/user-generators/podman-user-generator --dryrun
(shows the ExecStart command that will be run)
[pihole]$ podman stop pihole
(run the ExecStart command - but remove -d)
[pihole]$ /usr/bin/podman --log-level=warn run --name pihole --replace --rm --cgroups=split --tmpfs /docker-entrypoint.d --sdnotify=conmon -v /opt/data/pihole/etc-dnsmasq.d:/etc/dnsmasq.d/:Z,rw -v /opt/data/pihole/etc-pihole:/etc/pihole:Z,rw --publish 11443:443 --publish 11053:53/udp --publish 11053:53 --env TZ=Europe/Copenhagen --group-add=keep-groups --cidfile=/var/run/user/3020/pihole.cid docker.io/pihole/pihole@sha256:91dc91ddd413bf461c283204558f8f21839851e9824799075a7ceff7c77eea40
```

### Systemd

Tried to use systemd-sysusers but it does not work properly with ostree.

So create users/groups in `pihole-prep` service.

### RPM sources

Built by Tito from last commit,


### TLS

```console
$ cp pihole.mada.dk.fullchain.pem pihole-combined-full.pem
$ cat pihole.mada.dk.key >> pihole-combined-full.pem

$ scp pihole-combined-full.pem mada:/tmp/
$ sudo chmod go-r /opt/data/pihole/etc-pihole/tls.pem
$ sudo chown 656359:656359 /opt/data/pihole/etc-pihole/tls.pem
```
