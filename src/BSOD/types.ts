export type Phase =
  | 'start'
  | 'morning'
  | 'afternoon'
  | 'evening'
  | 'night'
  | 'actionResult'
  | 'event'
  | 'stream'
  | 'dayEnd'
  | 'ending'
  | 'dead';

export type ActionStyle = 'surveillance';

export type SvFootage = 'rest' | 'eat' | 'phone' | 'desk' | 'walk' | 'setup' | 'relax' | 'video' | 'game';

export type ActionPhase = 'morning' | 'afternoon' | 'evening' | 'night';

export type DeathCause = 'energy' | 'mood' | 'followers' | 'focus';

export type EndingType = 'online' | 'offline' | 'restart' | 'bsod';

export type LaisaEmotion = 'normal' | 'happy' | 'sad' | 'surprised' | 'tired' | 'focused';

export interface StatEffect {
  energy?: number;
  mood?: number;
  focus?: number;
  followers?: number;
  connection?: number;
  flag?: string;
}

export interface GameAction {
  id: string;
  phase: ActionPhase;
  labelZh: string;
  labelEn: string;
  descZh: string;
  descEn: string;
  effect: StatEffect;
  emotion?: LaisaEmotion;
  /** visual style for action result screen */
  style: ActionStyle;
  /** which surveillance footage clip to show */
  svFootage?: SvFootage;
  /** action triggers stream mini-game instead of direct effect */
  isStream?: true;
  /** action not available if this returns false */
  condition?: (state: GameStats & { flags: string[] }) => boolean;
}

export interface GameStats {
  energy: number;
  mood: number;
  focus: number;
  followers: number;
}

export interface StoryEvent {
  id: string;
  day: number;
  phase: ActionPhase;
  textZh: string;
  textEn: string;
  laisaEmotion?: LaisaEmotion;
  choices?: StoryChoice[];
  /** Visitor character sprite shown on the left during this event */
  visitorImg?: string;
  /** Visitor's display name shown above the event card */
  visitorName?: string;
}

export interface StoryChoice {
  labelZh: string;
  labelEn: string;
  effect: StatEffect;
  emotion?: LaisaEmotion;
}

export interface StreamEvent {
  id: string;
  textZh: string;
  textEn: string;
  choices: StreamChoice[];
}

export interface StreamChoice {
  labelZh: string;
  labelEn: string;
  effect: StatEffect;
  emotion?: LaisaEmotion;
}

/** How quickly the player responded — affects follower bonus */
export type ResponseSpeed = 'fast' | 'normal' | 'slow' | 'timeout';

/** What kind of volatility event fired on a follower change */
export type VolatileType = 'viral' | 'boost' | 'normal' | 'flop' | 'controversy';

export interface DayLog {
  energyDelta: number;
  moodDelta: number;
  focusDelta: number;
  followersDelta: number;
  streamedToday: boolean;
  lineZh: string;
  lineEn: string;
}

export interface GameState {
  phase: Phase;
  day: number;                     // 1–13
  prevPhase: ActionPhase;          // phase to return to after event overlay
  lastAction: GameAction | null;   // action being shown in actionResult screen
  energy: number;
  mood: number;
  focus: number;
  followers: number;
  connection: number;              // hidden, 0–10
  flags: string[];
  pendingEvent: StoryEvent | null; // story event waiting to fire
  streamQueue: StreamEvent[];      // events for current stream session
  streamIndex: number;
  streamFollowersGained: number;
  streamLastEvent: { delta: number; type: VolatileType; key: number } | null;
  streamPendingEnd: boolean;       // last event chosen, waiting for player to confirm
  dayLogStart: GameStats;          // stats snapshot at day start (for delta)
  streamedToday: boolean;
  deathCause: DeathCause | null;
  endingType: EndingType | null;
}
