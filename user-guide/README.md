# YorkU Multi-DB API - HTML User Guide

## 📚 Overview

This folder contains a comprehensive HTML user guide for the YorkU Multi-Database REST API. The guide is designed for both developers and non-technical users.

## 📁 Files Included

- **index.html** - Main landing page with overview and features
- **getting-started.html** - Step-by-step guide to making your first requests
- **endpoints.html** - Complete documentation for all API endpoints
- **examples.html** - Real-world examples and use cases
- **security.html** - Security best practices and authentication guide
- **troubleshooting.html** - Common issues and solutions
- **faq.html** - Frequently asked questions
- **styles.css** - Styling for all pages

## 🚀 How to Use

### Option 1: Open Directly in Browser

Simply open `index.html` in any web browser:

```bash
# On Linux/Mac
open user-guide/index.html

# On Windows
start user-guide/index.html

# Or just double-click index.html
```

### Option 2: Serve with Python HTTP Server

For the best experience, serve the files through a local web server:

```bash
# Navigate to the user-guide folder
cd user-guide

# Start a simple HTTP server
python3 -m http.server 8000

# Open in browser
# Visit: http://localhost:8000
```

### Option 3: Deploy to Web Server

Copy the entire `user-guide` folder to your web server:

```bash
# Example: Copy to nginx web root
cp -r user-guide /var/www/html/api-docs

# Access at: http://yourserver.com/api-docs/
```

## 🎯 Target Audience

- **Non-Developers**: Easy-to-follow visual guide with examples
- **Developers**: Complete API reference with code samples
- **System Administrators**: Setup and troubleshooting information

## 🎨 Features

- ✅ Clean, modern, responsive design
- ✅ Easy navigation with sidebar menu
- ✅ Color-coded sections for different topics
- ✅ Copy-paste ready code examples
- ✅ Interactive examples with curl commands
- ✅ Works offline (no external dependencies)
- ✅ Mobile-friendly responsive layout
- ✅ Printable documentation

## 📖 Page Descriptions

### Home (index.html)
- Welcome message and overview
- Feature highlights
- Supported databases
- Quick start steps
- Security features overview

### Getting Started (getting-started.html)
- Prerequisites
- First API request (health check)
- Authentication setup
- Discovering databases
- Making your first data request
- Understanding request structure
- Link to interactive docs

### Endpoints (endpoints.html)
- Complete documentation for all 7 endpoints
- Request/response examples
- Parameter descriptions
- Error handling
- Use cases for each endpoint

### Examples (examples.html)
- Real-world scenarios
- Copy-paste examples
- Common use cases
- Integration examples
- Python code samples

### Security (security.html)
- API key management
- Best practices
- SQL injection protection
- Safe deletion practices
- Error handling

### Troubleshooting (troubleshooting.html)
- Common errors and solutions
- Connection issues
- Authentication problems
- Query debugging
- Performance tips

### FAQ (faq.html)
- Frequently asked questions
- Quick answers
- Common scenarios
- Tips and tricks

## 🔧 Customization

To customize the guide for your environment:

1. **Update API URL**: Search and replace `http://localhost:8082` with your actual server URL
2. **Update Branding**: Edit the logo and footer text in each HTML file
3. **Add Examples**: Add your own examples to `examples.html`
4. **Modify Styles**: Edit `styles.css` to change colors, fonts, etc.

## 📱 Mobile Support

The guide is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones

## 🖨️ Printing

All pages are print-friendly with optimized print styles. Use your browser's print function to create PDFs.

## 🔗 Links

- API Server: http://localhost:8082
- Interactive Docs: http://localhost:8082/docs
- Health Check: http://localhost:8082/health

## 📞 Support

For questions or issues with the API itself, refer to the main project documentation or contact your system administrator.

## ✨ Updates

Last Updated: December 2024
Version: 1.0
Compatible with: YorkU Multi-DB API v1.0+

---

**Built with ❤️ for York University**

