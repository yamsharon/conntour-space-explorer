/**
 * Style utility functions for consistent styling across the application.
 */

/**
 * Returns Tailwind CSS classes for confidence score badges based on the confidence value.
 * 
 * Color scheme:
 * - Green: confidence > 75% (high confidence)
 * - Orange: confidence 50-75% (medium confidence)
 * - Red: confidence < 50% (low confidence)
 * 
 * @param confidence - Confidence value between 0 and 1
 * @returns Tailwind CSS class string for the confidence badge
 * 
 * @example
 * ```tsx
 * const colorClasses = getConfidenceColor(0.85); // Returns green classes
 * const colorClasses = getConfidenceColor(0.60); // Returns orange classes
 * const colorClasses = getConfidenceColor(0.30); // Returns red classes
 * ```
 */
export function getConfidenceColor(confidence: number): string {
  const percentage = confidence * 100;
  if (percentage > 75) return "bg-green-100 text-green-800 border-green-300";
  if (percentage >= 50) return "bg-orange-100 text-orange-800 border-orange-300";
  return "bg-red-100 text-red-800 border-red-300";
}

