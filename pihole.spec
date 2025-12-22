Name: pihole
Version: 2025.11.1
Release: 0%{?dist}
Summary: Pihole for mada.dk

License: EUPL-1.2
URL: https://github.com/jskov/fedora-iot-pihole

Source0: %{name}-%{version}.tar.gz

# See https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/#_systemd
BuildRequires: systemd-rpm-macros

%description

Pihole installation for mada.dk, running in a Systemd container on Fedora IoT.

%global debug_package %{nil}

%prep
%setup -q

%build

image=$(grep '^FROM' Containerfile | cut -d' ' -f 2)
cat pihole.container | sed -e "s,@PIHOLE_IMAGE@,$image," > %{_builddir}/pihole.container

%install

rm -f %{buildroot}/etc/containers/systemd/users/3020/pihole.container
rm -f %{buildroot}/usr/lib/systemd/system/pihole-prep.service
rm -f %{buildroot}/usr/share/mada/pihole

install -Dp -m644 pihole-prep.service %{buildroot}/usr/lib/systemd/system/pihole-prep.service
install -Dp -m644 %{_builddir}/pihole.container %{buildroot}/etc/containers/systemd/users/3020/pihole.container

%pre

%post
%systemd_post pihole-prep

%preun
%systemd_preun pihole-prep

%postun
%systemd_postun_with_restart pihole-prep

%files

/usr/lib/systemd/system/pihole-prep.service
/etc/containers/systemd/users/3020/pihole.container

%changelog
