%define name LogViewer
%define version 1.3.1
%define release 0
%define buildroot %{_tmppath}/%{name}-%{version}-%{release}-root

Summary: Log Viewer with ANSI color support and configurable highlighting
Name: %{name}
Version: %{version}
Release: %{release}
License: Proprietary
Group: Applications/System
BuildRoot: %{buildroot}
AutoReqProv: no


%description
Log Viewer is a GUI application for viewing and searching through log files. 
It supports ANSI color codes and provides features like text search, 
font size adjustment, and configurable term highlighting with custom colors.

%prep
# No preparation needed for this simple package

%build
# No build process needed

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/LogViewer
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/LogViewer


# Copy application files to the buildroot
cp -p %{_sourcedir}/config.yml $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/log_viewer $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/smallicon.png $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/log_viewer_start.sh $RPM_BUILD_ROOT/opt/LogViewer/

# Copy documentation
cp -p %{_sourcedir}/Install_README.md $RPM_BUILD_ROOT/usr/share/doc/LogViewer/README.md

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
/usr/share/doc/LogViewer/README.md


%changelog
* Sat May 4 2024 Log Viewer Build <tmichett@redhat.com> - 1.3.1-0
- Major performance improvements for file loading
- Switched to more efficient QPlainTextEdit for text display
- Implemented chunk-based rendering for large files
- Added incremental file loading with live updates
- Optimized search operations for better performance
- Added debounced search to prevent UI freezing

* Fri May 3 2024 Log Viewer Build <tmichett@redhat.com> - 1.3-0
- Added asynchronous file loading for large files
- Added progress bar for file loading operations
- Expanded file type support to include .log, .out, and .txt files
- Improved error handling for file operations

* Tue Apr 30 2024 Log Viewer Build <tmichett@redhat.com> - 1.2-0
- Added configuration GUI for highlighting terms
- Added support for custom config files through GUI
- Added command-line arguments for config files and log files
- Improved documentation

* Mon May 5 2023 Log Viewer Build <tmichett@redhat.com> - 1.0-0
- Initial package build
