import React, { useState, useEffect } from 'react';
import ThoughtLine from './ThoughtLine';
import SkeletonGallery from './product/SkeletonGallery';

const STAGES = [
  'Understanding your request...',
  'Finding relevant products...',
  'Comparing matches & applying filters...',
  'Preparing recommendations...',
];

export default function LoadingState() {
  const [stageIdx, setStageIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIdx((prev) => (prev + 1 < STAGES.length ? prev + 1 : prev));
    }, 1100);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-full max-w-5xl mx-auto my-8 sm:my-12 flex flex-col items-center">
      {/* Animated ThoughtLine with breathing shimmer, live timer & collapsible step trace */}
      <div className="mb-8 px-5 py-3 rounded-2xl bg-[#131318]/90 backdrop-blur-md border border-[#27272a] shadow-xl flex flex-col items-center">
        <ThoughtLine
          label={STAGES[stageIdx]}
          glyph="sparkle"
          steps={STAGES}
          activeStepIdx={stageIdx}
          working={true}
          collapsible={true}
          fontSize={14}
          color="#f4f4f5"
          glyphColor="#b39dff"
        />
      </div>

      {/* Skeletons Gallery */}
      <SkeletonGallery />
    </div>
  );
}
