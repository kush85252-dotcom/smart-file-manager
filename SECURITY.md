# Security Policy

## Supported Versions

Security fixes are currently provided for the latest version of Smart File Manager.

| Version        | Supported |
| -------------- | --------- |
| Latest         | ✅ Yes     |
| Older versions | ❌ No      |

## Reporting a Vulnerability

If you discover a security vulnerability in Smart File Manager, please **do not publicly disclose it through GitHub Issues**.

Instead, report it privately using GitHub's security reporting features, if enabled for this repository.

Please include:

* A clear description of the vulnerability
* Steps to reproduce the issue
* The expected and actual behavior
* The potential security impact
* Relevant logs, screenshots, or code snippets
* A possible fix, if known

Please allow reasonable time for the issue to be investigated and fixed before publicly disclosing it.

## Security-Sensitive Areas

Smart File Manager interacts with the local filesystem. Security reports involving the following areas are especially important:

* Unauthorized file access or modification
* Path traversal vulnerabilities
* Unsafe file or folder operations
* Arbitrary file deletion or movement
* Malicious file handling
* Configuration or settings manipulation
* Unsafe automatic file organization
* File watcher vulnerabilities
* Exposure of sensitive filesystem information
* Code execution caused by malicious input

## What Is Not a Security Vulnerability?

The following should generally be reported through normal GitHub Issues:

* UI bugs
* Visual problems
* Performance issues
* Feature requests
* Normal crashes without a security impact
* Incorrect file categorization
* General usability problems

## Response Process

Security reports will be reviewed and investigated as soon as reasonably possible.

If a vulnerability is confirmed, the project will work toward developing and releasing an appropriate fix.

Depending on the severity of the issue, affected users may be notified through the repository's release notes or other project announcements.

## Responsible Disclosure

Please avoid publicly posting exploit code, proof-of-concept attacks, or detailed instructions for exploiting an unfixed vulnerability.

Responsible disclosure helps protect users while the issue is being investigated and resolved.

## Thank You

Thank you for helping improve the security and reliability of Smart File Manager. 🔐
