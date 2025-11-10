[SharePoint Framework (SPFx)][spfx-github] is Microsoft's development model for building client-side web parts and extensions for SharePoint.

Eunomia provides a SharePoint web part that allows to:

- enforce authorization policies on SharePoint page buttons
- dynamically control button visibility and interactivity based on policy decisions

This extension helps organizations implement fine-grained access control on SharePoint pages without modifying existing content.

## Installation

Download the latest `.sppkg` package from the [GitHub releases][releases] page and deploy it to your SharePoint tenant:

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

[spfx-github]: https://github.com/SharePoint/sp-dev-docs
[releases]: https://github.com/whataboutyou-ai/eunomia/releases
