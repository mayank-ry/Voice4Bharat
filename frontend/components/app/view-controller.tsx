'use client';

import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentSessionView_01 } from '@/components/agents-ui/blocks/agent-session-view-01';
import { WelcomeView } from '@/components/app/welcome-view';
import { useEffect, useRef, useState } from 'react';
import { CallEndedView } from '@/components/app/call-ended-view';


const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(AgentSessionView_01);

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
    },
    hidden: {
      opacity: 0,
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.2,
    ease: 'linear',
  },
};

interface ViewControllerProps {
  appConfig: AppConfig;
}

export function ViewController({ appConfig }: ViewControllerProps) {
  const { isConnected, start } = useSessionContext();
  const [hasEnded, setHasEnded] = useState(false);
const wasConnected = useRef(false);

useEffect(() => {
  if (isConnected) {
    wasConnected.current = true;
    setHasEnded(false);
  } else if (wasConnected.current) {
    setHasEnded(true);
    wasConnected.current = false;
  }
}, [isConnected]);

const handleStartAgain = () => {
  setHasEnded(false);
  start();
};
const handleDismiss = () => {
  setHasEnded(false);
};
  const { resolvedTheme } = useTheme();

  return (
    <AnimatePresence mode="wait">
      {/* Welcome view */}
      {!isConnected && !hasEnded && (
  <MotionWelcomeView
    key="welcome"
    {...VIEW_MOTION_PROPS}
    startButtonText={appConfig.startButtonText}
    onStartCall={start}
  />
)}
{!isConnected && hasEnded && (
  <motion.div key="ended" {...VIEW_MOTION_PROPS}>
    <CallEndedView onStartAgain={handleStartAgain} onDismiss={handleDismiss} />
  </motion.div>
)}
      {/* Session view */}
      {isConnected && (
        <MotionSessionView
          key="session-view"
          {...VIEW_MOTION_PROPS}
          supportsChatInput={appConfig.supportsChatInput}
          supportsVideoInput={appConfig.supportsVideoInput}
          supportsScreenShare={appConfig.supportsScreenShare}
          isPreConnectBufferEnabled={appConfig.isPreConnectBufferEnabled}
          audioVisualizerType={appConfig.audioVisualizerType}
          audioVisualizerColor={
            resolvedTheme === 'dark'
              ? appConfig.audioVisualizerColorDark
              : appConfig.audioVisualizerColor
          }
          audioVisualizerColorShift={appConfig.audioVisualizerColorShift}
          audioVisualizerBarCount={appConfig.audioVisualizerBarCount}
          audioVisualizerGridRowCount={appConfig.audioVisualizerGridRowCount}
          audioVisualizerGridColumnCount={appConfig.audioVisualizerGridColumnCount}
          audioVisualizerRadialBarCount={appConfig.audioVisualizerRadialBarCount}
          audioVisualizerRadialRadius={appConfig.audioVisualizerRadialRadius}
          audioVisualizerWaveLineWidth={appConfig.audioVisualizerWaveLineWidth}
          className="absolute inset-0"
        />
      )}
    </AnimatePresence>
  );
}
