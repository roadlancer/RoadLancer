import DOMPurify from 'dompurify'

/**
 * Sanitize raw string or HTML input using DOMPurify to prevent XSS attacks.
 * Strips dangerous script tags, event handlers (`onload`, `onerror`), and malicious attributes
 * while preserving safe text and basic HTML formatting.
 */
export function sanitize(input: string | null | undefined): string {
  if (!input) return ''
  if (typeof window === 'undefined' || !DOMPurify) {
    return String(input).replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
  return DOMPurify.sanitize(input, {
    USE_PROFILES: { html: true },
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li',
      'code', 'pre', 'span', 'blockquote', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
  })
}

/**
 * Sanitize plain text, stripping out all HTML tags completely (`<script>`, `<b>`, etc.).
 * Ideal for subjects, sender names, usernames, and titles where no HTML should ever be parsed.
 */
export function sanitizeText(input: string | null | undefined): string {
  if (!input) return ''
  if (typeof window === 'undefined' || !DOMPurify) {
    return String(input).replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  }).trim()
}
