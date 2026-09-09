/**
 * Formats integers with comma grouping (e.g. 128421 -> "128,421")
 */
export function formatNumber(value?: number | null): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '—';
  }

  return new Intl.NumberFormat('en-US').format(value);
}

/**
 * Formats decimal numbers to specified precision (e.g. 0.9123 -> "0.912")
 */
export function formatDecimal(
  value?: number | null,
  decimals = 3
): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '—';
  }

  return value.toFixed(decimals);
}

/**
 * Formats ratios as percentages (e.g. 0.72428 -> "72.4%")
 */
export function formatPercent(
  value?: number | null,
  decimals = 1
): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '—';
  }

  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Returns color classes and labels for predictions.
 *
 * Supports both:
 * - "BOT" / "HUMAN"
 * - 1 / 0 from the backend ML model
 *
 * Backend mapping:
 * 1 = Bot
 * 0 = Human
 */
export function getPredictionBadgeConfig(
  prediction?: string | number
) {
  const normalizedPrediction =
    typeof prediction === 'number'
      ? prediction === 1
        ? 'BOT'
        : prediction === 0
          ? 'HUMAN'
          : ''
      : prediction?.toUpperCase();

  switch (normalizedPrediction) {
    case 'BOT':
      return {
        label: 'Bot Account',
        badgeClass:
          'bg-red-500/10 text-red-400 border border-red-500/30',
        dotClass: 'bg-red-500',
        textClass: 'text-red-400',
      };

    case 'HUMAN':
      return {
        label: 'Human Account',
        badgeClass:
          'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
        dotClass: 'bg-emerald-500',
        textClass: 'text-emerald-400',
      };

    default:
      return {
        label: 'Unclassified',
        badgeClass:
          'bg-slate-500/10 text-slate-400 border border-slate-500/30',
        dotClass: 'bg-slate-400',
        textClass: 'text-slate-400',
      };
  }
}

/**
 * Returns color badge styling for community risk statuses
 */
export function getCommunityRiskConfig(status?: string) {
  switch (status?.toLowerCase()) {
    case 'potentially_coordinated':
    case 'potentially coordinated':
      return {
        label: 'Potentially Coordinated',
        badgeClass:
          'bg-amber-500/10 text-amber-400 border border-amber-500/30',
        dotClass: 'bg-amber-500 animate-pulse',
      };

    case 'bot_heavy':
    case 'bot-heavy':
      return {
        label: 'Bot-Heavy Cluster',
        badgeClass:
          'bg-red-500/10 text-red-400 border border-red-500/30',
        dotClass: 'bg-red-500',
      };

    case 'moderate_risk':
      return {
        label: 'Moderate Risk',
        badgeClass:
          'bg-orange-500/10 text-orange-400 border border-orange-500/30',
        dotClass: 'bg-orange-400',
      };

    case 'low_risk':
    default:
      return {
        label: 'Low Risk',
        badgeClass:
          'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
        dotClass: 'bg-emerald-400',
      };
  }
}

/**
 * Format ISO dates for analytics logs
 */
export function formatDate(dateString?: string): string {
  if (!dateString) return '—';

  try {
    const d = new Date(dateString);

    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
}