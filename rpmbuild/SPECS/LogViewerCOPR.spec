%define name LogViewer
%define version 3.7.0
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
# No preparation needed for git-based build

%build
# No build process needed

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/LogViewer
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/LogViewer
mkdir -p $RPM_BUILD_ROOT/usr/share/icons/hicolor/32x32/apps

# Debug: Show directory structure during install
echo "=== Install Debug ==="
pwd
echo "Source dir: %{_sourcedir}"
ls -la %{_sourcedir} || echo "sourcedir not found"
echo "Build dir: %{_builddir}"
ls -la %{_builddir} || echo "builddir not found"
echo "Searching for git files:"
find %{_builddir} -name "config.yml" 2>/dev/null || echo "No config.yml found in builddir"
find / -name "config.yml" 2>/dev/null | head -10 || echo "No config.yml found anywhere"

# Copy application files from git repository (COPR git build)
cp -p %{_sourcedir}/../SOURCES/config.yml $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/../SOURCES/log_viewer $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/../SOURCES/smallicon.png $RPM_BUILD_ROOT/opt/LogViewer/
cp -p %{_sourcedir}/../SOURCES/smallicon.png $RPM_BUILD_ROOT/usr/share/icons/hicolor/32x32/apps/LogViewer.png
cp -p %{_sourcedir}/../SOURCES/log_viewer_start.sh $RPM_BUILD_ROOT/opt/LogViewer/

# Copy documentation
cp -p %{_sourcedir}/../SOURCES/Install_README.md $RPM_BUILD_ROOT/usr/share/doc/LogViewer/README.md

# Copy desktop file
cp -p %{_sourcedir}/../SOURCES/LogViewer.desktop $RPM_BUILD_ROOT/usr/share/applications/


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
/usr/share/icons/hicolor/32x32/apps/LogViewer.png


%changelog
* Mon Jan 13 2025 Log Viewer Build <travis@michettetech.com> - 3.7.0-0
- Version bump to 3.7.0
- Updated all build configurations for consistent versioning
- Fixed COPR build configuration issues
- Created COPR-specific spec file for git-based builds

* Sun Dec 15 2024 Log Viewer Build <travis@michettetech.com> - 3.0.0-0
- Enhanced search functionality with entire line highlighting
- Added bidirectional search navigation (Find Next/Find Previous)
- Improved search highlighting with proper cleanup of previous highlights
- Added comprehensive help system with integrated Help menu
- Added professional About dialog with version and company information
- Implemented keyboard shortcuts (Ctrl+F, F1, F3, Shift+F3, Escape)
- Added File menu with Open and Exit options
- Created comprehensive README documentation with installation and usage guides
- Fixed build script issues and improved build process reliability
- Enhanced PyQt version compatibility with multiple fallback approaches
- Added focus management for search functionality
- Improved user interface with tooltips and better navigation
- Added support for clearing search results with Escape key

* Tue Oct 15 2024 Log Viewer Build <travis@michettetech.com> - 1.3.1-0
- Major performance improvements for file loading
- Switched to more efficient QPlainTextEdit for text display
- Implemented chunk-based rendering for large files
- Added incremental file loading with live updates
- Optimized search operations for better performance
- Added debounced search to prevent UI freezing

* Tue Sep 10 2024 Log Viewer Build <travis@michettetech.com> - 1.2-5
- Added configuration GUI for highlighting terms
- Added support for custom config files through GUI
- Added command-line arguments for config files and log files
- Improved documentation


* Fri May 05 2023 Log Viewer Build <travis@michettetech.com> - 1.0-0
- Initial package build
