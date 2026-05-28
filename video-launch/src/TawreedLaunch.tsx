import { AbsoluteFill, Audio, staticFile, Sequence } from "remotion";
import { Captions } from "./components/Captions";
import { Scene1 } from "./scenes/Scene1";
import { Scene2 } from "./scenes/Scene2";
import { Scene3 } from "./scenes/Scene3";
import { Scene4 } from "./scenes/Scene4";
import { Scene5 } from "./scenes/Scene5";
import { Scene6 } from "./scenes/Scene6";
import { Scene7 } from "./scenes/Scene7";
import { Scene8 } from "./scenes/Scene8";

export const TawreedLaunch = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0f0f15", overflow: "hidden" }}>
      {/* Audio Mixing */}
      <Audio src={staticFile("assets/narration.wav")} volume={1.0} />
      <Audio src={staticFile("assets/music.mp3")} volume={0.15} />

      {/* Scene Sequences (overlapping by 15 frames for blur transitions) */}
      <Sequence durationInFrames={255}>
        <Scene1 />
      </Sequence>
      <Sequence from={240} durationInFrames={375}>
        <Scene2 />
      </Sequence>
      <Sequence from={600} durationInFrames={315}>
        <Scene3 />
      </Sequence>
      <Sequence from={900} durationInFrames={375}>
        <Scene4 />
      </Sequence>
      <Sequence from={1260} durationInFrames={405}>
        <Scene5 />
      </Sequence>
      <Sequence from={1650} durationInFrames={405}>
        <Scene6 />
      </Sequence>
      <Sequence from={2040} durationInFrames={315}>
        <Scene7 />
      </Sequence>
      <Sequence from={2340} durationInFrames={360}>
        <Scene8 />
      </Sequence>

      {/* Captions Overlay */}
      <Captions />
    </AbsoluteFill>
  );
};
