/**
 * Central registry of static design assets exported from Figma (node 3:2).
 * Reference these constants instead of hard-coding paths so assets can be
 * swapped or moved to a CDN in one place.
 */
export const assets = {
  logo: "/assets/logo.png",
  profile: "/assets/profile.png",
  iconClaude: "/assets/icon-claude.svg",
  iconCreate: "/assets/icon-create.svg",
  iconSettings: "/assets/icon-settings.svg",
  iconAiScan: "/assets/icon-ai-scan.svg",
  iconChevronDown: "/assets/icon-chevron-down.svg",
  iconVoice: "/assets/icon-voice.svg",
  iconArrowUp: "/assets/icon-arrow-up.svg",
  // Question flow + result screens
  iconSubArrow: "/assets/icon-subarrow.svg",
  bullet: "/assets/bullet.svg",
  checkbox: "/assets/checkbox.svg",
  lineThread: "/assets/line-thread.svg",
  iconSlide: "/assets/icon-slide.svg",
  iconTime: "/assets/icon-time.svg",
  iconDownload: "/assets/icon-download.svg",
  iconClose: "/assets/icon-close.svg",
  iconFollowUpArrow: "/assets/icon-followup-arrow.svg",
} as const;
