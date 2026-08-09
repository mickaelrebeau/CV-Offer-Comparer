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
  analysisResult,
  interviewCv,
  interviewOffer,
  questions,
  sampleAnswer,
} from '../data/mockInterview';
import { fadeIn, slideUp } from '../lib/animation';

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
};

export const InterviewDemo: React.FC = () => {
  const frame = useCurrentFrame();

  const step1 = frame < 120;
  const showQuestions = frame >= 70 && frame < 150;
  const interviewStarted = frame >= 150;
  const showResults = frame >= 330;

  const offerText =
    frame < 50
      ? interviewOffer.slice(0, Math.min(interviewOffer.length, Math.floor(Math.max(0, frame - 5) * 1.2)))
      : interviewOffer;
  const cvText =
    frame < 50
      ? interviewCv.slice(0, Math.min(interviewCv.length, Math.floor(Math.max(0, frame - 20) * 1.2)))
      : interviewCv;

  const questionProgress = interviewStarted
    ? interpolate(frame, [150, 300], [1, 10], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 0;
  const currentQ = Math.min(9, Math.floor(questionProgress) - 1);
  const displayQ = Math.max(0, Math.min(questions.length - 1, currentQ >= 0 ? 0 : 0));
  const timerSeconds = interviewStarted
    ? Math.floor(interpolate(frame, [150, 330], [0, 432], { extrapolateRight: 'clamp' }))
    : 0;

  const answerText =
    frame >= 180 && frame < 300
      ? sampleAnswer.slice(0, Math.min(sampleAnswer.length, Math.floor((frame - 180) * 1.4)))
      : frame >= 300
        ? sampleAnswer
        : '';

  const progressPct = interviewStarted
    ? interpolate(frame, [150, 300], [10, 100], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 0;

  return (
    <AbsoluteFill className="bg-paper font-sans text-ink">
      <AppShell title="simulateur — entretien">
        <div className="mx-auto flex h-full max-w-[1680px] flex-col gap-6">
          {/* Step 1: inputs */}
          {step1 && !showResults && (
            <div style={{ opacity: frame >= 130 ? interpolate(frame, [130, 150], [1, 0], { extrapolateRight: 'clamp' }) : 1 }}>
              <div className="mb-6 grid grid-cols-2 gap-6">
                <Panel>
                  <PanelHeader>01 · Offre d&apos;emploi</PanelHeader>
                  <div className="p-5">
                    <TextAreaMock value={offerText} placeholder="Collez l'offre d'emploi..." minHeight={180} />
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
                    <TextAreaMock value={cvText} placeholder="Collez le texte de votre CV..." minHeight={180} />
                  </div>
                </Panel>
              </div>

              {frame >= 55 && frame < 130 && (
                <div className="flex justify-center" style={{ opacity: fadeIn(frame, 55) }}>
                  <PrimaryButton loading={frame >= 60 && frame < 100} spinFrame={frame}>
                    {frame >= 60 && frame < 100 ? 'Génération…' : 'Générer les questions'}
                  </PrimaryButton>
                </div>
              )}
            </div>
          )}

          {/* Questions list */}
          {showQuestions && !interviewStarted && (
            <div className="space-y-3" style={{ opacity: fadeIn(frame, 100), transform: `translateY(${slideUp(frame, 100)}px)` }}>
              {questions.map((q, idx) => (
                <Panel
                  key={idx}
                  className="p-5"
                  style={{
                    opacity: fadeIn(frame, 105 + idx * 12),
                    transform: `translateY(${slideUp(frame, 105 + idx * 12)}px)`,
                  }}
                >
                  <div className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase">
                    <span className="text-ink-soft">Question {idx + 1}</span>
                    <span className="text-ink/30">{q.category}</span>
                  </div>
                  <p className="text-[15px] font-medium text-ink">{q.text}</p>
                </Panel>
              ))}
              <div className="flex justify-center pt-4" style={{ opacity: fadeIn(frame, 140) }}>
                <PrimaryButton>Lancer la simulation</PrimaryButton>
              </div>
            </div>
          )}

          {/* Active interview */}
          {interviewStarted && !showResults && (
            <div className="space-y-6" style={{ opacity: fadeIn(frame, 150) }}>
              <Panel className="flex items-center justify-between p-5">
                <span className="font-mono text-[11px] uppercase text-ink-soft">Session en cours</span>
                <span className="font-mono text-[11px] uppercase text-ink-soft">~20 min · 10 questions</span>
              </Panel>

              <PanelDark>
                <PanelDarkHeader
                  right={<span>⏱ {formatTime(timerSeconds)}</span>}
                >
                  Question 01 / 10 · {questions[displayQ].category}
                </PanelDarkHeader>
                <div className="space-y-5 p-6">
                  <p className="font-sans text-[22px] font-medium leading-snug text-paper">
                    {questions[displayQ].text}
                  </p>
                  <div className="space-y-2">
                    <label className="font-mono text-[11px] uppercase text-paper/40">Votre réponse</label>
                    <div className="min-h-[140px] whitespace-pre-wrap rounded-md border border-white/10 bg-ink-deep p-4 font-sans text-[15px] leading-relaxed text-paper">
                      {answerText}
                      {frame >= 180 && frame < 300 && Math.floor(frame / 15) % 2 === 0 && (
                        <span className="ml-0.5 inline-block h-[1.1em] w-[2px] bg-paper/70 align-text-bottom" />
                      )}
                    </div>
                  </div>
                </div>
              </PanelDark>

              <div className="space-y-2">
                <div className="flex justify-between font-mono text-[11px] uppercase text-ink-soft">
                  <span>Progression</span>
                  <span>{Math.round(progressPct)}%</span>
                </div>
                <ProgressTrack progress={progressPct} />
              </div>
            </div>
          )}

          {/* Results */}
          {showResults && (
            <div className="space-y-6" style={{ opacity: fadeIn(frame, 330), transform: `translateY(${slideUp(frame, 330)}px)` }}>
              <div className="grid grid-cols-4 gap-4">
                <StatCard
                  label="Score global"
                  value={`${analysisResult.score_global}/10`}
                  color="text-ink"
                  style={{ gridColumn: 'span 2', opacity: fadeIn(frame, 335) }}
                />
                <StatCard label="Questions" value="10" style={{ opacity: fadeIn(frame, 343) }} />
                <StatCard label="Durée" value="7:12" style={{ opacity: fadeIn(frame, 351) }} />
              </div>

              <Panel className="space-y-4 p-6" style={{ opacity: fadeIn(frame, 360) }}>
                <h3 className="font-mono text-[13px] uppercase tracking-wide text-ink">Points forts</h3>
                <div className="space-y-2">
                  {analysisResult.points_forts.map((pf, idx) => (
                    <div
                      key={idx}
                      className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-[14px] text-emerald-800"
                      style={{ opacity: fadeIn(frame, 365 + idx * 10) }}
                    >
                      {pf}
                    </div>
                  ))}
                </div>
              </Panel>

              <Panel className="space-y-4 p-6" style={{ opacity: fadeIn(frame, 385) }}>
                <h3 className="font-mono text-[13px] uppercase tracking-wide text-ink">Pistes d&apos;amélioration</h3>
                <div className="space-y-2">
                  {analysisResult.points_amelioration.map((pa, idx) => (
                    <div
                      key={idx}
                      className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3 text-[14px] text-amber-800"
                      style={{ opacity: fadeIn(frame, 390 + idx * 10) }}
                    >
                      {pa}
                    </div>
                  ))}
                </div>
              </Panel>
            </div>
          )}
        </div>
      </AppShell>
    </AbsoluteFill>
  );
};
