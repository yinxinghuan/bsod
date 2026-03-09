import { useCallback, useState } from 'react';
import type {
  GameState, Phase, ActionPhase, StatEffect,
  DeathCause, EndingType, GameAction, StoryChoice, ResponseSpeed, VolatileType,
} from '../types';
import { STORY_EVENTS, pickStreamEvents } from '../data/events';
import { getActionsForPhase } from '../data/actions';

// ── Constants ─────────────────────────────────────────────────────────────────

const TOTAL_DAYS = 13;

const INITIAL_STATS = {
  energy: 65,
  mood: 58,
  focus: 52,
  followers: 1200,
};

// Passive drain each day at morning start
const DAILY_DRAIN = { energy: -12, mood: -8, focus: -5, followers: -40 };

const PHASE_ORDER: ActionPhase[] = ['morning', 'afternoon', 'evening', 'night'];

// ── Helpers ───────────────────────────────────────────────────────────────────

function clamp(v: number, min = 0, max = 100): number {
  return Math.max(min, Math.min(max, v));
}

// Adds viral / crash volatility to raw follower deltas.
// Gains:  4% viral (5-10x) · 10% boost (1.8-2.8x) · 12% flop (0.3-0.6x) · 74% normal
// Losses: 7% controversy (3-5x) · 93% normal
export function volatileFollowers(base: number): { value: number; type: VolatileType } {
  if (base === 0) return { value: 0, type: 'normal' };
  const r = Math.random();
  if (base > 0) {
    if (r < 0.04) return { value: Math.round(base * (5 + Math.random() * 5)),    type: 'viral' };
    if (r < 0.14) return { value: Math.round(base * (1.8 + Math.random())),       type: 'boost' };
    if (r < 0.26) return { value: Math.round(base * (0.3 + Math.random() * 0.3)), type: 'flop' };
    return { value: base, type: 'normal' };
  } else {
    if (r < 0.07) return { value: Math.round(base * (3 + Math.random() * 2)),    type: 'controversy' };
    return { value: base, type: 'normal' };
  }
}

function applyEffect(state: GameState, effect: StatEffect): GameState {
  return {
    ...state,
    energy: clamp(state.energy + (effect.energy ?? 0)),
    mood: clamp(state.mood + (effect.mood ?? 0)),
    focus: clamp(state.focus + (effect.focus ?? 0)),
    followers: Math.max(0, state.followers + (effect.followers ?? 0)),
    connection: Math.min(10, Math.max(0, state.connection + (effect.connection ?? 0))),
    flags: effect.flag ? [...state.flags, effect.flag] : state.flags,
  };
}

function checkDeath(state: GameState): DeathCause | null {
  if (state.energy <= 0) return 'energy';
  if (state.mood <= 0) return 'mood';
  if (state.focus <= 0) return 'focus';
  if (state.followers <= 100) return 'followers';
  return null;
}

function calcEnding(state: GameState): EndingType {
  const { followers, connection } = state;
  if (followers > 3500 && connection >= 6) return 'online';
  if (followers > 3500) return 'offline';
  if (connection >= 6) return 'restart';
  return 'bsod';
}

function getStoryEvent(day: number, phase: ActionPhase, flags: string[]) {
  return STORY_EVENTS.find(
    e => e.day === day && e.phase === phase && !flags.includes(`ev_${e.id}`)
  ) ?? null;
}

function initialState(): GameState {
  return {
    phase: 'start',
    day: 1,
    prevPhase: 'morning',
    ...INITIAL_STATS,
    connection: 0,
    flags: [],
    pendingEvent: null,
    lastAction: null,
    streamQueue: [],
    streamIndex: 0,
    streamFollowersGained: 0,
    streamLastEvent: null,
    streamPendingEnd: false,
    dayLogStart: { ...INITIAL_STATS },
    streamedToday: false,
    deathCause: null,
    endingType: null,
  };
}

function enterPhase(state: GameState, phase: ActionPhase): GameState {
  let next = { ...state, phase: phase as Phase, prevPhase: phase };

  // Daily drain at morning start
  if (phase === 'morning') {
    next = {
      ...next,
      energy: clamp(next.energy + DAILY_DRAIN.energy),
      mood: clamp(next.mood + DAILY_DRAIN.mood),
      focus: clamp(next.focus + DAILY_DRAIN.focus),
      followers: Math.max(0, next.followers + DAILY_DRAIN.followers),
      streamedToday: false,
      dayLogStart: {
        energy: next.energy,
        mood: next.mood,
        focus: next.focus,
        followers: next.followers,
      },
    };
    const death = checkDeath(next);
    if (death) return { ...next, phase: 'dead', deathCause: death };
  }

  // Check for story event
  const event = getStoryEvent(next.day, phase, next.flags);
  if (event) {
    return {
      ...next,
      phase: 'event',
      prevPhase: phase,
      pendingEvent: event,
      flags: [...next.flags, `ev_${event.id}`],
    };
  }

  return next;
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useBSOD() {
  const [state, setState] = useState<GameState>(initialState);

  const startGame = useCallback(() => {
    setState(s => enterPhase({ ...s, phase: 'start' }, 'morning'));
  }, []);

  const chooseEventOption = useCallback((choice: StoryChoice) => {
    setState(s => {
      if (s.phase !== 'event' || !s.pendingEvent) return s;
      let next = applyEffect(s, choice.effect);
      const death = checkDeath(next);
      if (death) return { ...next, phase: 'dead', deathCause: death };
      // Return to the phase this event triggered in
      return enterPhase({ ...next, pendingEvent: null }, s.prevPhase);
    });
  }, []);

  const dismissEvent = useCallback(() => {
    setState(s => {
      if (s.phase !== 'event' || !s.pendingEvent) return s;
      return enterPhase({ ...s, pendingEvent: null }, s.prevPhase);
    });
  }, []);

  const chooseAction = useCallback((action: GameAction) => {
    setState(s => {
      const currentPhase = s.phase as ActionPhase;
      if (!PHASE_ORDER.includes(currentPhase)) return s;
      // Apply follower volatility now so ActionResultScreen shows the real number
      const volatileAction: GameAction =
        action.effect.followers
          ? { ...action, effect: { ...action.effect, followers: volatileFollowers(action.effect.followers).value } }
          : action;
      return {
        ...s,
        phase: 'actionResult' as Phase,
        lastAction: volatileAction,
        prevPhase: currentPhase,
      };
    });
  }, []);

  const dismissActionResult = useCallback(() => {
    setState(s => {
      if (s.phase !== 'actionResult' || !s.lastAction) return s;
      const action = s.lastAction;
      const currentPhase = s.prevPhase;

      if (action.isStream) {
        const queue = pickStreamEvents(3);
        let next = applyEffect(s, action.effect);
        return {
          ...next,
          phase: 'stream' as Phase,
          lastAction: null,
          streamQueue: queue,
          streamIndex: 0,
          streamFollowersGained: 0,
          streamLastEvent: null,
          streamedToday: true,
        };
      }

      let next = applyEffect({ ...s, lastAction: null }, action.effect);
      const death = checkDeath(next);
      if (death) return { ...next, phase: 'dead', deathCause: death };

      return advancePhase(next, currentPhase);
    });
  }, []);

  const chooseStreamOption = useCallback((choiceIndex: number, speed: ResponseSpeed) => {
    setState(s => {
      if (s.phase !== 'stream') return s;
      const event = s.streamQueue[s.streamIndex];
      if (!event) return s;
      const choice = event.choices[choiceIndex];
      if (!choice) return s;

      // Apply follower volatility to stream choices
      let volatileType: VolatileType = 'normal';
      const volatileEffect: typeof choice.effect = (() => {
        if (!choice.effect.followers) return choice.effect;
        const { value, type } = volatileFollowers(choice.effect.followers);
        volatileType = type;
        return { ...choice.effect, followers: value };
      })();

      // Apply base effect
      let next = applyEffect(s, volatileEffect);

      // Speed bonus/penalty applied to followers only
      const speedBonus: Record<ResponseSpeed, number> = {
        fast:    0.5,   // +50% followers
        normal:  0,
        slow:    -0.5,  // -50% followers
        timeout: -1.0,  // -100% followers gain + mood penalty
      };
      const bonus = speedBonus[speed];
      if (bonus !== 0 && volatileEffect.followers) {
        const extra = Math.round(volatileEffect.followers * Math.abs(bonus));
        next = applyEffect(next, {
          followers: bonus > 0 ? extra : -extra,
          mood: speed === 'timeout' ? -5 : 0,
        });
      }

      const death = checkDeath(next);
      if (death) return { ...next, phase: 'dead', deathCause: death };

      const gained = next.followers - s.followers;
      const lastEvent = volatileEffect.followers
        ? { delta: volatileEffect.followers, type: volatileType, key: (s.streamLastEvent?.key ?? 0) + 1 }
        : s.streamLastEvent;
      next = { ...next, streamFollowersGained: s.streamFollowersGained + Math.max(0, gained), streamLastEvent: lastEvent };

      const nextIndex = s.streamIndex + 1;
      if (nextIndex >= s.streamQueue.length) {
        // Last event — stay in stream phase so flash has time to display
        return { ...next, streamPendingEnd: true };
      }
      return { ...next, streamIndex: nextIndex };
    });
  }, []);

  const confirmStreamEnd = useCallback(() => {
    setState(s => {
      if (s.phase !== 'stream' || !s.streamPendingEnd) return s;
      return advancePhase({ ...s, streamPendingEnd: false }, s.prevPhase);
    });
  }, []);

  const confirmDayEnd = useCallback(() => {
    setState(s => {
      if (s.phase !== 'dayEnd') return s;
      if (s.day >= TOTAL_DAYS) {
        const endingType = calcEnding(s);
        return { ...s, phase: 'ending', endingType };
      }
      return enterPhase({ ...s, day: s.day + 1 }, 'morning');
    });
  }, []);

  const restart = useCallback(() => {
    setState(initialState());
  }, []);

  return {
    state,
    actions: {
      startGame,
      chooseEventOption,
      dismissEvent,
      chooseAction,
      dismissActionResult,
      chooseStreamOption,
      confirmStreamEnd,
      confirmDayEnd,
      restart,
    },
    // Derived helpers
    currentPhaseActions: PHASE_ORDER.includes(state.phase as ActionPhase)
      ? getActionsForPhase(state.phase as ActionPhase).filter(
          a => !a.condition || a.condition({ ...state })
        )
      : [],
  };
}

// ── Phase advancement ─────────────────────────────────────────────────────────

function advancePhase(state: GameState, currentPhase: ActionPhase): GameState {
  const idx = PHASE_ORDER.indexOf(currentPhase);
  if (idx < PHASE_ORDER.length - 1) {
    return enterPhase(state, PHASE_ORDER[idx + 1]);
  }
  // End of night → day end
  return { ...state, phase: 'dayEnd' };
}
