%define name LogViewer
%define version 1.0
%define release 0
%define buildroot %{_tmppath}/%{name}-%{version}-%{release}-root

Summary: Log Viewer
Name: %{name}
Version: %{version}
Release: %{release}
License: Proprietary
Group: Applications/System
BuildArch: noarch
BuildRoot: %{buildroot}
Requires: python3 python-pyqt6 python-pyyaml

%description
Log Viewer

%prep
# No preparation needed for this simple package

%build
# No build process needed

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/LogViewer
mkdir -p $RPM_BUILD_ROOT/usr/share/applications


# Copy application files to the buildroot
cp -p %{_sourcedir}/config.yml $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/log_viewer $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/smallicon.png $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/log_viewer_start.sh $RPM_BUILD_ROOT/opt/LogViewer/

# Copy desktop file
cp -p %{_sourcedir}/LogViewer.desktop $RPM_BUILD_ROOT/usr/share/applications/


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/opt/LogViewer/
/opt/LogViewer/config.yml
/opt/LogViewer/log_viewer
/opt/LogViewer/smallicon.png
%attr(0755,root,root) /opt/LogViewer/log_viewer_start.sh
%attr(0755,root,root) /usr/share/applications/LogViewer.desktop


%changelog
* Mon May 5 2025 Log Viewer Build <tmichett@redhat.com> - 1.0-0
- Initial package build
