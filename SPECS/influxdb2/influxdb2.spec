%define project github.com/influxdata/influxdb/v2

Name:           influxdb2
Summary:        Scalable datastore for metrics, events, and real-time analytics
License:        MIT
Group:          Productivity/Databases/Servers
Vendor:         Microsoft Corporation
Distribution:   Mariner
Version:        2.4.0
Release:        1%{?dist}
URL:            https://github.com/influxdata/influxdb
Source0:        %{url}%archive/refs/tags/v%{version}#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.gz
BuildRequires:  fdupes
BuildRequires:  go >= 1.18
BuildRequires:  golang-packaging >= 15.0.8
BuildRequires:  build-essential
BuildRequires:  pkg-config >= 0.171.0
BuildRequires:  protobuf-devel
BuildRequires:  kernel-headers
BuildRequires:  make
BuildRequires:  rust
BuildRequires:  clang
BuildRequires:  tzdata

# Below is a manually created tarball, no download link.
# We're using pre-populated Go modules from this tarball, since network is disabled during build time.
# How to re-build this file:
#   1. wget https://github.com/influxdata/influxdb/archive/refs/tags/v%%{version}.tar.gz -O %%{name}-%%{version}.tar.gz
#   2. tar -xf %%{name}-%%{version}.tar.gz
#   3. cd %%{name}-%%{version}
#   4. go mod vendor
#   5. tar  --sort=name \
#           --mtime="2021-04-26 00:00Z" \
#           --owner=0 --group=0 --numeric-owner \
#           --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
#           -cf %%{name}-%%{version}-vendor.tar.gz vendor
#

%description
InfluxDB is an distributed time series database with no external dependencies.
It's useful for recording metrics, events, and performing analytics.

%package        devel
Summary:        InfluxDB development files
Group:          Development/Languages/Golang
Requires:       go
Conflicts:      influxdb 

%description devel
Go sources and other development files for InfluxDB

%prep
%setup -q

%build
export GO111MODULE=on
export GOPATH=$HOME/go
tar -xf %{SOURCE1} --no-same-owner

# Build influxdb
mkdir -pv $HOME/go/src/%{project}
rm -rf $HOME/go/src/%{project}/*
cp -avr * $HOME/go/src/%{project}
cd $HOME/go/src/%{project}
go build -mod=vendor -tags 'sqlite_foreign_keys,sqlite_json' -ldflags="-X main.version=%{version}" -o bin/linux/influxd ./cmd/influxd


%install
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
cd $HOME/go/src/%{project}

mkdir -p %{buildroot}%{_localstatedir}/log/influxdb
mkdir -p %{buildroot}%{_localstatedir}/lib/influxdb
install -D -m 0755 bin/linux/influxd %{buildroot}/%{_bindir}/influxd

%fdupes %{buildroot}/%{_prefix}

%check
go test ./...

%files
%license LICENSE
%dir %{_sysconfdir}/influxdb2
%{_bindir}/influxd
%{_bindir}/telemetryd
%{_datadir}/influxdb2
%dir %{_tmpfilesdir}
%attr(0755, influxdb, influxdb) %dir %{_localstatedir}/log/influxdb
%attr(0755, influxdb, influxdb) %dir %{_localstatedir}/lib/influxdb

%files devel
%license LICENSE
%dir %{go_contribsrcdir}/github.com
%dir %{go_contribsrcdir}/github.com/influxdata
%{go_contribsrcdir}/github.com/influxdata/influxdb

%changelog