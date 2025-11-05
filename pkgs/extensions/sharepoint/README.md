# Eunomia Extension for SharePoint

A [SharePoint Framework (SPFx)][spfx-github] web part that integrates [Eunomia][eunomia-github] authorization to dynamically control button visibility and interactivity on SharePoint pages based on policy decisions.

## Overview

This extension provides a production-ready web part for SharePoint that enforces authorization policies on page buttons. The web part monitors buttons on SharePoint pages and makes real-time authorization checks against the Eunomia policy decision point.

### Features

- 🔒 **Policy-Based Button Control**: Enforce authorization policies on SharePoint buttons
- ⚡ **Real-Time Authorization**: Authorization checks happen on page load
- 🔄 **Dynamic Content Support**: Uses `MutationObserver` to handle dynamically loaded buttons
- 🎨 **Fluent UI Integration**: Seamless integration with SharePoint's design system
- 🔧 **Configurable**: Flexible CSS selectors and debug options

## Installation

Download the latest `.sppkg` package from the [GitHub releases][releases] page.

Deploy to your SharePoint tenant:

1. Upload the `.sppkg` file to your SharePoint tenant App Catalog
2. Deploy the solution when prompted
3. Add the "Button Filters" web part to a SharePoint page
4. Configure the web part properties in the property pane

## Configuration

Configure the web part through the property pane:

- **PDP Endpoint**: URL of your Eunomia PDP (e.g., `http://localhost:8421`)
- **API Key**: Authentication key for the Eunomia server
- **Button Selector**: CSS selector to target buttons (e.g.: `a.button, button`)
- **Show Debug**: Enable debug logging in the browser console

## How It Works

The web part monitors the page for buttons matching the configured selector. For each button, it makes an authorization check to the Eunomia decision node, sending the current user's email and the button's `href` or text content as context.

Based on the policy decision:
- **Allow**: Button remains interactive
- **Deny**: Button is disabled and styled to indicate it's not available

## Building from Source

Install the dependencies:

```bash
npm install
```

Build for development:

```bash
npm run build
```

Build and package for production:

```bash
npm run build:production
```

This generates the `.sppkg` file in `solution/sharepoint-button.sppkg`.

Test locally:

```bash
npm run serve
```

## Documentation

For detailed usage and policy configuration, check out the [Eunomia documentation][eunomia-docs].

[spfx-github]: https://github.com/SharePoint/sp-dev-docs
[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[eunomia-docs]: https://whataboutyou-ai.github.io/eunomia/
[releases]: https://github.com/whataboutyou-ai/eunomia/releases
