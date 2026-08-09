import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import {
  AppShell,
  Panel,
  PanelDark,
  PanelDarkHeader,
  PanelHeader,
  PrimaryButton,
  ProgressTrack,
  StatCard,
  TextAreaMock,
} from '../components/ui';
import {
  categories,
  criteria,
  cvSnippet,
  offerSnippet,
  progressMessages,
  streamStatuses,
  summaryStats,
} from '../data/mockAnalysis';
import { fadeIn, slideUp, statusLabel, statusTone } from '../lib/animation';

export const AnalysisDemo: React.FC = () => {
  const frame = useCurrentFrame();

  const offerText =
    frame < 90 ? offerSnippet.slice(0, Math.min(offerSnippet.length, Math.floor(Math.max(0, frame - 8) * 1.1))) : offerSnippet;
  const cvText =
    frame < 90
      ? cvSnippet.slice(0, Math.min(cvSnippet.length, Math.floor(Math.max(0, frame - 35) * 1.1)))
      : cvSnippet;

  const isLoading = frame >= 100 && frame < 210;
  const progress = interpolate(frame, [100, 205], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const progressMsgIndex = Math.min(
    progressMessages.length - 1,
    Math.floor(interpolate(frame, [100, 205], [0, progressMessages.length], { extrapolateRight: 'clamp' })),
  );

  const showResults = frame >= 210;
  const showReport = frame >= 250;
  const focusDocker = frame >= 320;

  const visibleStreamCount = showResults
    ? Math.min(streamStatuses.length, Math.floor(interpolate(frame, [210, 250], [0, streamStatuses.length + 0.99], { extrapolateRight: 'clamp' })))
    : 0;

  const statsOpacity = (i: number) =>
    showResults ? fadeIn(frame, 215 + i * 8) : 0;

  const reportOpacity = showReport ? fadeIn(frame, 250) : 0;
  const reportY = showReport ? slideUp(frame, 250) : 24;

  const dockerHighlight = focusDocker
    ? interpolate(frame, [320, 335], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 0;

  return (
    <AbsoluteFill className="bg-paper font-sans text-ink">
      <AppShell title="comparateur — analyse">
        <div className="mx-auto flex h-full max-w-[1680px] flex-col gap-8">
          {/* Input phase */}
          <div
            className="grid grid-cols-2 gap-6"
            style={{ opacity: frame >= 240 ? interpolate(frame, [240, 260], [1, 0.35], { extrapolateRight: 'clamp' }) : 1 }}
          >
            <Panel>
              <PanelHeader>01 · Offre d&apos;emploi</PanelHeader>
              <div className="p-5">
                <TextAreaMock
                  value={offerText}
                  placeholder="Collez l'offre d'emploi ici..."
                  showCaret={frame >= 8 && frame < 90 && offerText.length < offerSnippet.length}
                />
              </div>
            </Panel>
            <Panel>
              <PanelHeader
                right={
                  <div className="flex gap-1">
                    <span className="rounded bg-ink px-2 py-0.5 text-paper">PDF</span>
                    <span className="rounded px-2 py-0.5 text-ink-soft">Texte</span>
                  </div>
                }
              >
                02 · Mon CV
              </PanelHeader>
              <div className="p-5">
                <TextAreaMock
                  value={cvText}
                  placeholder="Collez le texte de votre CV ici..."
                  showCaret={frame >= 35 && frame < 90 && cvText.length < cvSnippet.length}
                />
              </div>
            </Panel>
          </div>

          {/* CTA + progress */}
          <div className="mx-auto flex w-full max-w-xl flex-col items-center gap-4">
            {isLoading && (
              <div className="w-full space-y-2" style={{ opacity: fadeIn(frame, 100) }}>
                <div className="flex items-center justify-between font-mono text-[11px] uppercase text-ink-soft">
                  <span>{progressMessages[progressMsgIndex]}</span>
                  <span>{Math.round(progress)}%</span>
                </div>
                <ProgressTrack progress={progress} />
                <div className="space-y-1 pt-2">
                  {streamStatuses.slice(0, visibleStreamCount).map((row) => (
                    <div
                      key={row.id}
                      className="flex items-center justify-between border-b border-ink/5 py-1.5 font-mono text-[11px] uppercase"
                    >
                      <span className="text-ink-soft">{row.label}</span>
                      <span className={statusTone(row.status)}>{row.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <PrimaryButton
              disabled={frame < 85}
              loading={isLoading}
              spinFrame={frame}
            >
              {isLoading ? 'Analyse en cours…' : 'Lancer la comparaison'}
            </PrimaryButton>
          </div>

          {/* Results */}
          {showResults && (
            <div className="space-y-6" style={{ opacity: fadeIn(frame, 210), transform: `translateY(${slideUp(frame, 210)}px)` }}>
              <div className="grid grid-cols-4 gap-4">
                {summaryStats.map((stat, i) => (
                  <StatCard
                    key={stat.label}
                    label={stat.label}
                    value={stat.value}
                    color={stat.color}
                    style={{ opacity: statsOpacity(i), transform: `translateY(${slideUp(frame, 215 + i * 8)}px)` }}
                  />
                ))}
              </div>

              <PanelDark style={{ opacity: reportOpacity, transform: `translateY(${reportY}px)` }}>
                <PanelDarkHeader>Rapport détaillé par critère</PanelDarkHeader>
                <div className="grid grid-cols-12">
                  <div className="border-r border-white/10 p-6 lg:col-span-4">
                    <div className="mb-2 text-[11px] uppercase text-paper/40">Score global</div>
                    <div className="mb-6 text-6xl font-medium tabular-nums">88%</div>
                    <div className="space-y-3">
                      {categories.map((cat) => (
                        <div key={cat.label}>
                          <div className="mb-1.5 flex items-baseline justify-between text-[11px] uppercase">
                            <span className="text-paper/60">{cat.label}</span>
                            <span className="tabular-nums text-paper/40">{cat.value}%</span>
                          </div>
                          <div className="h-px w-full bg-white/10">
                            <div className="h-px bg-paper/70" style={{ width: `${cat.value}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-6 lg:col-span-8">
                    <div className="mb-3 text-[11px] uppercase text-paper/40">Détail des critères</div>
                    <div className="space-y-0">
                      {criteria.map((item) => {
                        const isDocker = item.id === '4';
                        const highlight = isDocker ? dockerHighlight : 0;
                        return (
                          <div
                            key={item.id}
                            className="border-b border-white/5 py-3"
                            style={{
                              backgroundColor: `rgba(251, 191, 36, ${highlight * 0.08})`,
                              boxShadow: highlight > 0 ? `inset 0 0 0 1px rgba(251, 191, 36, ${highlight * 0.35})` : undefined,
                            }}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 space-y-1.5">
                                <div className="flex flex-wrap items-center gap-3 text-[11px] uppercase">
                                  <span className="text-paper/40">{item.category}</span>
                                  <span className="text-paper/30">conf. {Math.round(item.confidence * 100)}%</span>
                                </div>
                                <p className="text-[15px] text-paper/90">{item.offerText}</p>
                                {item.cvText && (
                                  <p className="text-[13px] text-paper/50">
                                    <span className="text-paper/70">Extrait CV :</span> {item.cvText}
                                  </p>
                                )}
                                {isDocker && focusDocker && item.suggestions?.[0] && (
                                  <div
                                    className="mt-3 space-y-1.5 border-t border-white/10 pt-3"
                                    style={{ opacity: fadeIn(frame, 340) }}
                                  >
                                    <div className="text-[11px] uppercase text-paper/40">Reformulation proposée</div>
                                    <p className="font-sans text-[14px] leading-relaxed text-paper/80">
                                      « {item.suggestions[0]} »
                                    </p>
                                  </div>
                                )}
                              </div>
                              <div className={`shrink-0 text-[11px] uppercase ${statusTone(item.status)}`}>
                                {statusLabel(item.status)}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </PanelDark>
            </div>
          )}
        </div>
      </AppShell>
    </AbsoluteFill>
  );
};
