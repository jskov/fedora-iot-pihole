# Reverse Proxy RPM for mada.dk on Fedora IOT

[![Copr build status](https://copr.fedorainfracloud.org/coprs/jskov/iot-pihole/package/pihole/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/jskov/iot-reverse-proxy/package/pihole/)

I use this RPM for layering in Fedora IOT.

It runs [pihole](https://pi-hole.net/) in a [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) with a preliminary service to fix the integration with the system (user setup).

>[!NOTE]
>This project is Open Source. But I am not interested in providing support or help in any form.
>You are welcome to fork it though!

# Dev notes

## Build RPM

Set up toolbox:

```console
$ distrobox create -i registry.fedoraproject.org/fedora:43 -n fedora-tito --pre-init-hooks "dnf install -y rpmbuild selinux-policy-devel tito"
```

Build rpm locally (note that this builds on *committed GIT data only!*):

```console
$ distrobox enter fedora-rev-proxy
$ cd ROOT OF REPOSITORY
$ rpmlint pihole.spec
$ rm -rf /tmp/tito/x86_64/ ; tito build --rpm --test
```

Testing the rpm locally is hard to do on an Atomic OS.
Installation can be tested on a container containing init:

```console
$ distrobox create -i registry.fedoraproject.org/fedora:42 --init --additional-packages "systemd" -n fedora-test
$ distrobox enter fedora-test

$ sudo rpm -i /tmp/tito/x86_64/reverse-proxy-1.0.0-0.git.3.2d74dcb.fc41.x86_64.rpm
```

But `systemctl` does not work with the --machine/--user in this setup.

So test the image installation/system-d interaction on plain Fedora (in a box).
Remember to make `/tmp/tito` available to the Flatpak Boxes application.

Update spec version (--keep-version to keep manually maintained version in spec file):

```console
$ export EDITOR=vi
$ tito tag --keep-version

# This will result in a tag on the git repository, named 'reverse-proxy-$WHATEVER'
# And an updated file .tito/packages/pihole

# Note that without the above, the build command will fail with the message:
#  ERROR: Unable to lookup latest package info.
#  Perhaps you need to tag first?
```

Build from repo:

```console
$ copr-cli buildscm --clone-url https://github.com/jskov/fedora-iot-pihole.git --method tito jskov/iot-pihole
```


## Installation

### RPM

Install the RPM; the --uninstall allows updating an existing layered rpm (older version):


```console
# Store the RPM locally - do not delete, as long as the RPM is included
$ mv /tmp/reverse-proxy-1.29.4-0.git.16.b7c4604.fc43.x86_64.rpm ~/_local_layers/pihole/

$ sudo rpm-ostree install /var/home/jskov/layers/reverse-proxy-1.0.0-0.fc42.x86_64.rpm --uninstall reverse-proxy
```

Enable the prep-service; the systemd policy for enabling a service does not appear to work (on Atom?):

```console
$ sudo systemctl enable pihole-prep
$ sudo systemctl reboot
```

The user process should be running after restart:

```console
$ sudo systemctl --user -M pihole@ status pihole
TODO TODO
```


### Firewall

```console
TODO TODO
$ sudo firewall-cmd --add-forward-port=port=80:proto=tcp:toport=8000 --permanent
```

## Notes

### Systemd

Tried to use systemd-sysusers but it does not work properly with ostree.

So create users/groups in `pihole-prep` service.

### RPM sources

Built by Tito from last commit,
