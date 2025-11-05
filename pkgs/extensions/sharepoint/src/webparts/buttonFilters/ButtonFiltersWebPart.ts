import * as React from 'react';
import * as ReactDom from 'react-dom';
import { Version } from '@microsoft/sp-core-library';
import {
  type IPropertyPaneConfiguration,
  PropertyPaneTextField,
  PropertyPaneCheckbox
} from '@microsoft/sp-property-pane';
import { BaseClientSideWebPart } from '@microsoft/sp-webpart-base';

import * as strings from 'ButtonFiltersWebPartStrings';
import ButtonFilters from './components/ButtonFilters';
import { IButtonFiltersProps } from './components/IButtonFiltersProps';

export interface IButtonFiltersWebPartProps {
  pdpEndpoint: string;
  apiKey: string;
  buttonSelector: string;
  showDebug: boolean;
}

export default class ButtonFiltersWebPart extends BaseClientSideWebPart<IButtonFiltersWebPartProps> {

  public render(): void {
    const element: React.ReactElement<IButtonFiltersProps> = React.createElement(
      ButtonFilters,
      {
        pdpEndpoint: this.properties.pdpEndpoint,
        apiKey: this.properties.apiKey,
        userEmail: this.context.pageContext.user.email,
        buttonSelector: this.properties.buttonSelector,
        showDebug: this.properties.showDebug
      }
    );

    ReactDom.render(element, this.domElement);
  }

  protected onDispose(): void {
    ReactDom.unmountComponentAtNode(this.domElement);
  }

  protected get dataVersion(): Version {
    return Version.parse('1.0');
  }

  protected getPropertyPaneConfiguration(): IPropertyPaneConfiguration {
    return {
      pages: [
        {
          header: {
            description: strings.PropertyPaneDescription
          },
          groups: [
            {
              groupName: strings.BasicGroupName,
              groupFields: [
                PropertyPaneTextField('pdpEndpoint', {
                  label: 'PDP Endpoint URL'
                }),
                PropertyPaneTextField('apiKey', {
                  label: 'API Key'
                }),
                PropertyPaneTextField('buttonSelector', {
                  label: 'Button CSS Selector'
                }),
                PropertyPaneCheckbox('showDebug', {
                  text: 'Show Debug Dashboard'
                })
              ]
            }
          ]
        }
      ]
    };
  }
}
