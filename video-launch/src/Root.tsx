import { Composition, continueRender, delayRender } from "remotion";
import { loadFont as loadCairo } from "@remotion/google-fonts/Cairo";
import { loadFont as loadPlusJakarta } from "@remotion/google-fonts/PlusJakartaSans";
import { loadFont as loadJetBrains } from "@remotion/google-fonts/JetBrainsMono";
import { TawreedLaunch } from "./TawreedLaunch";
import "./index.css";

// Delay render until fonts are loaded
const waitForCairo = delayRender();
const cairoFont = loadCairo("normal", { weights: ["900"] });
cairoFont.waitUntilDone().then(() => continueRender(waitForCairo));

const waitForPlusJakarta = delayRender();
const plusJakartaFont = loadPlusJakarta("normal", { weights: ["500", "800"] });
plusJakartaFont.waitUntilDone().then(() => continueRender(waitForPlusJakarta));

const waitForJetBrains = delayRender();
const jetBrainsFont = loadJetBrains("normal", { weights: ["600", "700"] });
jetBrainsFont.waitUntilDone().then(() => continueRender(waitForJetBrains));

export const RemotionRoot = () => {
  return (
    <Composition
      id="TawreedLaunch"
      component={TawreedLaunch}
      durationInFrames={2700} // 90 seconds @ 30 fps
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
