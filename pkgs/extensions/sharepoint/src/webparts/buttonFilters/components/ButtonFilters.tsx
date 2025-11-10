import * as React from 'react';
import styles from './ButtonFilters.module.scss';
import type { IButtonFiltersProps } from './IButtonFiltersProps';
import { EunomiaClient, CheckResponse } from 'eunomia-sdk';

interface IButtonFiltersState {
  isProcessing: boolean;
  errors: string[];
  processedCount: number;
}

export default class ButtonFilters extends React.Component<IButtonFiltersProps, IButtonFiltersState> {
  private eunomiaClient: EunomiaClient | null = null;
  private mutationObserver: MutationObserver | null = null;
  private processedButtons: Set<Element> = new Set();

  constructor(props: IButtonFiltersProps) {
    super(props);
    this.state = {
      isProcessing: true,
      errors: [],
      processedCount: 0
    };
  }

  public async componentDidMount(): Promise<void> {
    await this.initializeAndFilter();
  }

  public componentWillUnmount(): void {
    if (this.mutationObserver) {
      this.mutationObserver.disconnect();
    }
  }

  private async initializeAndFilter(): Promise<void> {
    const { pdpEndpoint, apiKey, buttonSelector } = this.props;

    if (!pdpEndpoint) {
      this.setState({
        errors: ['Please configure the PDP endpoint in the Web Part properties.'],
        isProcessing: false
      });
      return;
    }

    if (!buttonSelector) {
      this.setState({
        errors: ['Please configure the button selector in the Web Part properties.'],
        isProcessing: false
      });
      return;
    }

    try {
      this.eunomiaClient = new EunomiaClient({
        endpoint: pdpEndpoint,
        apiKey: apiKey || undefined
      });

      await this.filterButtons();

      this.setupMutationObserver();

      this.setState({
        errors: [],
        isProcessing: false
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.setState({
        errors: [`Initialization failed: ${errorMessage}`],
        isProcessing: false
      });
    }
  }

  private setupMutationObserver(): void {
    const { buttonSelector } = this.props;

    this.mutationObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const element = node as Element;

            // Check if the added node itself matches the selector
            if (element.matches(buttonSelector)) {
              this.processButton(element as HTMLButtonElement | HTMLAnchorElement).catch(error => {
                console.error('[Eunomia] Error processing button:', error);
              });
            }

            // Check if any children match the selector
            const matchingChildren = element.querySelectorAll<HTMLButtonElement | HTMLAnchorElement>(buttonSelector);
            matchingChildren.forEach((button) => {
              this.processButton(button).catch(error => {
                console.error('[Eunomia] Error processing button:', error);
              });
            });
          }
        });
      });
    });

    this.mutationObserver.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  private async filterButtons(): Promise<void> {
    const { buttonSelector } = this.props;

    const buttons = document.querySelectorAll<HTMLButtonElement | HTMLAnchorElement>(buttonSelector);

    if (buttons.length === 0) {
      this.setState({
        errors: [`No buttons found with selector: ${buttonSelector}`]
      });
      return;
    }

    for (let i = 0; i < buttons.length; i++) {
      await this.processButton(buttons[i]);
    }
  }

  /**
   * Disables a button (both HTMLButtonElement and HTMLAnchorElement)
   */
  private disableButton(button: HTMLButtonElement | HTMLAnchorElement): void {
    // Handle native button disable property
    if (button instanceof HTMLButtonElement) {
      button.disabled = true;
    }
    // Apply visual and interaction styles for both buttons and links
    button.style.opacity = '0.6';
    button.style.pointerEvents = 'none';
    button.style.cursor = 'not-allowed';
    button.setAttribute('aria-disabled', 'true');
  }

  /**
   * Enables a button (both HTMLButtonElement and HTMLAnchorElement)
   */
  private enableButton(button: HTMLButtonElement | HTMLAnchorElement): void {
    // Handle native button enable property
    if (button instanceof HTMLButtonElement) {
      button.disabled = false;
    }
    // Remove visual and interaction styles
    button.style.opacity = '';
    button.style.pointerEvents = '';
    button.style.cursor = '';
    button.removeAttribute('aria-disabled');
  }

  private async processButton(button: HTMLButtonElement | HTMLAnchorElement): Promise<void> {
    const { userEmail } = this.props;

    // Skip if already processed
    if (this.processedButtons.has(button)) {
      return;
    }

    if (!this.eunomiaClient) {
      return;
    }

    if (!userEmail) {
      return;
    }

    // Disable the button by default
    this.disableButton(button);

    try {
      const buttonId = button.id || button.getAttribute('data-button-id') || button.textContent?.trim() || 'unknown';

      const response: CheckResponse = await this.eunomiaClient.check({
        principalUri: `user:${userEmail}`,
        principalAttributes: {
          email: userEmail
        },
        resourceUri: `button:${buttonId}`,
        resourceAttributes: {
          id: buttonId,
          type: 'button',
        },
        action: 'click'
      });

      // Enable the button only if the check is successful
      if (response.allowed) {
        this.enableButton(button);
      }
      // If not allowed, button remains disabled (already set above)

      // Mark as processed
      this.processedButtons.add(button);
      this.setState({ processedCount: this.processedButtons.size });
    } catch (error) {
      console.error('[Eunomia] Error checking button access:', error);
      // In case of error, keep the button disabled for safety
    }
  }

  public render(): React.ReactElement<IButtonFiltersProps> {
    const { showDebug } = this.props;
    const { isProcessing, errors, processedCount } = this.state;

    if (!showDebug) {
      return <div />;
    }

    return (
      <div className={styles.container}>
        {isProcessing && (
          <div className={styles.statusMessage}>
            Checking button permissions...
          </div>
        )}
        {!isProcessing && errors.length === 0 && processedCount > 0 && (
          <div className={styles.statusMessage}>
            Processed {processedCount} button(s)
          </div>
        )}
        {errors.length > 0 && (
          <div className={styles.errorMessage}>
            {errors.join(', ')}
          </div>
        )}
      </div>
    );
  }
}
