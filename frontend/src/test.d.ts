declare module 'vitest' {
  interface Assertion<T = any> {
    toBeDisabled(): T
    toBeEnabled(): T
    toBeEmptyDOMElement(): T
    toBeInTheDocument(): T
    toBeInvalid(): T
    toBeRequired(): T
    toBeValid(): T
    toBeVisible(): T
    toContainElement(element: Element | null): T
    toContainHTML(htmlText: string): T
    toHaveAccessibleDescription(expected?: string | RegExp): T
    toHaveAccessibleName(expected?: string | RegExp): T
    toHaveAttribute(attr: string, value?: unknown): T
    toHaveClass(...classNames: string[]): T
    toHaveFocus(): T
    toHaveFormValues(expectedValues: Record<string, unknown>): T
    toHaveStyle(css: string | Record<string, unknown>): T
    toHaveTextContent(text: string | RegExp, options?: { normalizeWhitespace?: boolean }): T
    toHaveValue(value?: string | string[] | number | null): T
    toHaveDisplayValue(value: string | RegExp | (string | RegExp)[]): T
    toBeChecked(): T
    toBePartiallyChecked(): T
    toHaveErrorMessage(expected?: string | RegExp): T
  }
}
export {}
