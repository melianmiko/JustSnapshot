%global srcname copr-tito-quickdoc

Name: justsnapshot
Version: 0.1
Release: 1%{?dist}
License: BSD
Summary: BTRFS System Snapshot tool
Url: https://github.com/melianmiko/JustSnapshot
Source0: %{name}-%{version}.tar.gz

BuildArch: noarch

BuildRequires: python3-devel
BuildRequires: python3-setuptools
Requires: btrfs-progs
Requires: python3

%description
Simple CLI tool that can create, manage and restore BTRFS subvolume snapshots.
Run 'jsnapshot-setup' to configure.

#-- PREP, BUILD & INSTALL -----------------------------------------------------#
%prep
%autosetup

%build
%py3_build

%install
%py3_install

#-- FILES ---------------------------------------------------------------------#
%files
%{_bindir}/jsnapshot-*
%{python3_sitelib}/JustSnapshot-*.egg-info/
%{python3_sitelib}/jsnapshot_core/
%{python3_sitelib}/jsnapshot_cron/

#-- CHANGELOG -----------------------------------------------------------------#
%changelog
* Mon Nov 08 2021 MelianMiko <melianmiko@gmail.com> 0.1-1
- new package built with tito


