#!/bin/bash

cp -avR rpmbuild ~
rpmbuild -ba ~/rpmbuild/SPECS/LogViewer.spec
