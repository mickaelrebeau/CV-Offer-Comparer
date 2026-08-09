import "./index.css";
import { Composition } from "remotion";
import { AnalysisDemo } from "./compositions/AnalysisDemo";
import { InterviewDemo } from "./compositions/InterviewDemo";
import {
  ANALYSIS_DURATION,
  FPS,
  HEIGHT,
  INTERVIEW_DURATION,
  WIDTH,
} from "./theme/talento";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnalysisDemo"
        component={AnalysisDemo}
        durationInFrames={ANALYSIS_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="InterviewDemo"
        component={InterviewDemo}
        durationInFrames={INTERVIEW_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
