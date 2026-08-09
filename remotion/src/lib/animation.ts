import { interpolate } from 'remotion';

export const fadeIn = (frame: number, start: number, duration = 12) =>
  interpolate(frame, [start, start + duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const fadeOut = (frame: number, start: number, duration = 12) =>
  interpolate(frame, [start, start + duration], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const slideUp = (frame: number, start: number, distance = 24) =>
  interpolate(frame, [start, start + 18], [distance, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const statusTone = (status: 'match' | 'missing' | 'unclear' | string) => {
  if (status === 'match' || status === 'couvert') return 'text-emerald-400';
  if (status === 'missing' || status === 'manquant') return 'text-rose-400';
  return 'text-amber-400';
};

export const statusLabel = (status: 'match' | 'missing' | 'unclear') => {
  if (status === 'match') return 'couvert';
  if (status === 'missing') return 'manquant';
  return 'partiel';
};
