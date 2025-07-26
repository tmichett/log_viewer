# Code Signing Guide for Microsoft Store Submission

## 📋 Overview

This guide will help you set up code signing for your Log Viewer application to meet Microsoft Store Policy 10.2.9 requirements. All apps submitted to the Microsoft Store must be digitally signed with SHA256 or higher code signing certificates.

## 🏪 Microsoft Store Policy 10.2.9

**Requirement**: "Your app must be digitally signed as per this policy with a SHA256 or higher code sign certificate."

**What this means:**
- All executable files must have valid digital signatures
- Must use SHA256 or stronger hashing algorithm
- Certificate must chain to a trusted root certificate authority
- Timestamps must be included to preserve validity beyond certificate expiration

## 🎯 Quick Start

### Option A: Microsoft Trusted Signing (Recommended)

**Pros:**
- Cloud-based, no hardware requirements
- Managed by Microsoft, reliable uptime
- Easy integration with CI/CD pipelines
- Cost-effective at ~$9/month

**Setup Steps:**
1. Sign up for Microsoft Trusted Signing in Azure Portal
2. Create a Trusted Signing account
3. Set up authentication (Azure CLI or Service Principal)
4. Configure build environment with Azure credentials

### Option B: Traditional Code Signing Certificate

**Pros:**
- Works offline
- Full control over certificate
- Can be used for multiple purposes

**Cons:**
- Higher cost ($200-400/year)
- Requires hardware token for EV certificates
- More complex setup

## 🔧 Implementation Guide

### Step 1: Choose Your Certificate Type

#### Microsoft Trusted Signing Setup
```bash
# Install Azure CLI
# Sign in to Azure
az login

# Create Trusted Signing account (replace with your values)
az trustedsigning account create \
  --resource-group myResourceGroup \
  --account-name myTrustedSigningAccount \
  --location "East US"

# Create signing identity
az trustedsigning identity create \
  --account-name myTrustedSigningAccount \
  --resource-group myResourceGroup \
  --identity-name mySigningIdentity \
  --subject-name "CN=Michette Technologies"
```

#### Traditional Certificate Setup
```bash
# If using a PFX file
set CODESIGN_PFX_FILE=C:\path\to\MichetteTech.pfx
set CODESIGN_PASSWORD=your_certificate_password

# If certificate is in Windows Certificate Store
set CODESIGN_IDENTITY="Michette Technologies"
```

### Step 2: Configure Build Environment

Create a batch file `setup_codesigning.bat`:
```cmd
@echo off
REM Code Signing Configuration for Log Viewer
REM Author: travis@michettetech.com

echo Setting up code signing environment...

REM Method 1: Using PFX file
REM set CODESIGN_PFX_FILE=C:\certificates\MichetteTech.pfx
REM set CODESIGN_PASSWORD=your_password_here

REM Method 2: Using Certificate Store (recommended)
set CODESIGN_IDENTITY=Michette Technologies

REM Timestamp server (required for long-term validity)
set CODESIGN_TIMESTAMP=http://timestamp.digicert.com

REM Alternative timestamp servers (use any one):
REM set CODESIGN_TIMESTAMP=http://timestamp.sectigo.com
REM set CODESIGN_TIMESTAMP=http://timestamp.entrust.net/TSS/RFC3161sha2TS

echo Code signing configured!
echo Identity: %CODESIGN_IDENTITY%
echo Timestamp: %CODESIGN_TIMESTAMP%

REM Test certificate access
if defined CODESIGN_PFX_FILE (
    if exist "%CODESIGN_PFX_FILE%" (
        echo ✓ PFX file found: %CODESIGN_PFX_FILE%
    ) else (
        echo ✗ PFX file not found: %CODESIGN_PFX_FILE%
    )
) else (
    REM Test certificate store access
    certlm.msc /s >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Certificate store accessible
    ) else (
        echo ⚠ Run as administrator to access certificate store
    )
)
```

### Step 3: Build with Code Signing

```cmd
# Set up environment
call setup_codesigning.bat

# Build the application
cd rpmbuild/SOURCES
Build_App_Windows.bat
```

### Step 4: Verify Signature

```cmd
# Basic verification
signtool verify /pa LogViewer-3.3.0.exe

# Detailed verification
signtool verify /pa /v LogViewer-3.3.0.exe

# Show all certificate details
signtool verify /pa /v /all LogViewer-3.3.0.exe
```

## 🔍 Troubleshooting

### Common Issues

#### "SignTool Error: No certificates were found that met all the given criteria"

**Cause:** Certificate not found or accessible

**Solutions:**
```cmd
# List available certificates
certlm.msc

# Or via command line
powershell -Command "Get-ChildItem -Path Cert:\CurrentUser\My"
powershell -Command "Get-ChildItem -Path Cert:\LocalMachine\My"

# Check exact certificate subject name
powershell -Command "Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like '*Michette*'}"
```

#### "SignTool Error: An error occurred while attempting to load the signing certificate"

**Cause:** Incorrect password or corrupted PFX file

**Solutions:**
```cmd
# Test PFX file access
certutil -dump "path\to\certificate.pfx"

# Verify password
openssl pkcs12 -info -in certificate.pfx -noout
```

#### "Timestamp Server Error"

**Cause:** Network issues or timestamp server unavailable

**Solutions:**
```cmd
# Try alternative timestamp servers
set CODESIGN_TIMESTAMP=http://timestamp.sectigo.com
set CODESIGN_TIMESTAMP=http://timestamp.entrust.net/TSS/RFC3161sha2TS
set CODESIGN_TIMESTAMP=http://timestamp.globalsign.com/tsa/r6advanced1

# Test network connectivity
ping timestamp.digicert.com
```

### Testing Certificate Validity

```cmd
# Check certificate expiration
powershell -Command "Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object {$_.Subject -like '*Michette*'} | Select-Object Subject, NotAfter"

# Verify certificate chain
signtool verify /pa /v /all LogViewer-3.3.0.exe | findstr "Chain"
```

## 🏭 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Sign Windows

on:
  push:
    tags: ['v*']

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install PyInstaller
    
    - name: Set up code signing
      env:
        CODESIGN_IDENTITY: ${{ secrets.CODESIGN_IDENTITY }}
        CODESIGN_PASSWORD: ${{ secrets.CODESIGN_PASSWORD }}
        CODESIGN_TIMESTAMP: ${{ secrets.CODESIGN_TIMESTAMP }}
      run: |
        echo "Code signing configured"
    
    - name: Build and sign executable
      env:
        CODESIGN_IDENTITY: ${{ secrets.CODESIGN_IDENTITY }}
        CODESIGN_PASSWORD: ${{ secrets.CODESIGN_PASSWORD }}
        CODESIGN_TIMESTAMP: ${{ secrets.CODESIGN_TIMESTAMP }}
      run: |
        cd rpmbuild/SOURCES
        Build_App_Windows.bat
    
    - name: Verify signature
      run: |
        signtool verify /pa rpmbuild/SOURCES/LogViewer-*.exe
```

## 💰 Cost Analysis

| Option | Initial Cost | Annual Cost | Hardware Required | Best For |
|--------|-------------|-------------|------------------|----------|
| Microsoft Trusted Signing | $0 | ~$108/year | None | CI/CD, Cloud-first |
| Standard Certificate | $200-300 | $200-300 | None | Basic signing |
| EV Certificate | $300-500 | $300-500 | Hardware token | Instant reputation |

## 📚 Additional Resources

### Official Documentation
- [Microsoft Store Policy 10.2.9](https://docs.microsoft.com/en-us/windows/uwp/publish/store-policies#102-security)
- [SignTool Documentation](https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool)
- [Microsoft Trusted Signing](https://learn.microsoft.com/en-us/azure/trusted-signing/)

### Certificate Authorities
- [DigiCert Code Signing](https://www.digicert.com/code-signing/)
- [Sectigo Code Signing](https://sectigo.com/ssl-certificates-tls/code-signing)
- [Entrust Code Signing](https://www.entrust.com/digital-security/certificate-solutions/products/digital-certificates/code-signing-certificates)

### Timestamp Servers
- DigiCert: `http://timestamp.digicert.com`
- Sectigo: `http://timestamp.sectigo.com`
- Entrust: `http://timestamp.entrust.net/TSS/RFC3161sha2TS`
- GlobalSign: `http://timestamp.globalsign.com/tsa/r6advanced1`

## ✅ Checklist for Microsoft Store Submission

- [ ] Code signing certificate obtained from trusted CA
- [ ] Build environment configured with signing credentials
- [ ] Executable built and automatically signed
- [ ] Signature verified with `signtool verify /pa`
- [ ] Timestamp included in signature
- [ ] Certificate chains to trusted root CA
- [ ] Uses SHA256 or stronger hash algorithm
- [ ] No signature errors or warnings

## 🎯 Next Steps

1. **Choose Certificate Option**: Decide between Microsoft Trusted Signing or traditional certificate
2. **Obtain Certificate**: Follow the setup process for your chosen option
3. **Configure Environment**: Set up environment variables and test signing
4. **Update Build Process**: Use the updated build scripts provided
5. **Test and Verify**: Build and verify signatures before submitting to Microsoft Store
6. **Submit to Store**: Upload signed executable to Microsoft Store

---

**Need Help?**
- Email: travis@michettetech.com
- Organization: Michette Technologies
- Date Created: December 2024
- Last Updated: December 2024 