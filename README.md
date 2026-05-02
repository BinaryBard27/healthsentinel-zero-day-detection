# Phishing Attack Simulation Guide

## Overview
This project provides tools and documentation for running legitimate phishing attack simulations for security awareness training and testing purposes.

**⚠️ IMPORTANT: Only use these tools for authorized security testing and training within your own organization or with explicit written permission.**

## What is Phishing Simulation?
Phishing simulation is a security awareness training technique where organizations send simulated phishing emails to employees to:
- Test security awareness
- Train employees to recognize phishing attempts
- Measure the effectiveness of security training programs
- Identify areas that need improvement

## Legal and Ethical Considerations
- ✅ **DO**: Use only on systems you own or have explicit written permission to test
- ✅ **DO**: Obtain proper authorization before running simulations
- ✅ **DO**: Use for legitimate security awareness training
- ❌ **DON'T**: Use against systems you don't own or have permission to test
- ❌ **DON'T**: Use for malicious purposes
- ❌ **DON'T**: Violate any laws or regulations

## Tools and Methods

### 1. Commercial Phishing Simulation Platforms
- **KnowBe4**: Enterprise-grade platform with templates and analytics
- **Proofpoint Security Awareness**: Comprehensive training and simulation
- **Gophish**: Open-source phishing framework
- **Microsoft Defender for Office 365**: Built-in simulation capabilities

### 2. Open-Source Tools

#### Gophish
- **Website**: https://getgophish.com/
- **GitHub**: https://github.com/gophish/gophish
- **Features**: 
  - Email campaign management
  - Landing page builder
  - Results tracking
  - User-friendly web interface

#### Social Engineering Toolkit (SET)
- **Website**: https://github.com/trustedsec/social-engineer-toolkit
- **Features**: Multiple attack vectors including phishing

### 3. Custom Python Scripts
This repository includes a basic Python-based phishing simulation framework.

## Setup Instructions

### Prerequisites
- Python 3.7+
- SMTP server access (for sending emails)
- Web server (for hosting landing pages)

### Installation
```bash
pip install -r requirements.txt
```

## Usage

### Basic Email Simulation
```bash
python phishing_simulator.py --help
```

### Creating Campaigns
1. Edit `templates/` directory with your email templates
2. Configure `config.json` with your SMTP settings
3. Run the simulation script

## Best Practices
1. **Start Small**: Begin with a small group before company-wide campaigns
2. **Educate First**: Provide security training before running simulations
3. **Provide Feedback**: Give immediate feedback when users click links
4. **Track Metrics**: Monitor click rates, report rates, and improvement over time
5. **Follow Up**: Provide additional training for users who fall for simulations
6. **Document Everything**: Keep records of authorization and results

## Reporting
After running simulations, document:
- Number of emails sent
- Click-through rates
- Users who reported suspicious emails
- Training needs identified
- Improvement over time

## Resources
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [SANS Security Awareness](https://www.sans.org/security-awareness-training/)

## Disclaimer
This tool is for authorized security testing and educational purposes only. Unauthorized use of phishing techniques is illegal and unethical. Users are solely responsible for ensuring they have proper authorization before using these tools.

