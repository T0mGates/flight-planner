import { useState, useEffect, useRef } from 'react';
import { Play, Pause } from 'lucide-react';
import { Slider } from '@/components/ui/slider';

// Format unix timestamp to readable date/time
function formatTime(unixSeconds: number) {
  const date = new Date(unixSeconds * 1000);
  return date.toLocaleString('en-US', {
    timeZone: "UTC",
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

interface TimeControlsProps {
  startTimeSeconds: number;
  endTimeSeconds: number;
  currentTimeSeconds: number;
  setCurrentTimeSeconds: (time: number | ((prev: number) => number)) => void;
  timestep: number,
  intervalTimeout: number
}

export default function TimeControls({
  startTimeSeconds,
  endTimeSeconds,
  currentTimeSeconds,
  setCurrentTimeSeconds,
  timestep,
  intervalTimeout,
}: TimeControlsProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const intervalRef = useRef<number | undefined>(undefined);

  const startTime = formatTime(startTimeSeconds);
  const endTime = formatTime(endTimeSeconds);
  const currentTime = formatTime(currentTimeSeconds);

  const totalDurationSeconds = endTimeSeconds - startTimeSeconds;
  const totalSteps = totalDurationSeconds / timestep;

  // Keep slider handle in sync with current time
  const currentStep = Math.floor((currentTimeSeconds - startTimeSeconds) / timestep);

  const handleSliderChange = (value: number[]) => {
    if (isPlaying) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = undefined;
      }
      setIsPlaying(false);
    }
    const newTimeSeconds = startTimeSeconds + (value[0] * timestep);
    setCurrentTimeSeconds(newTimeSeconds);
  };

  const intervalFunction = () => {
    setCurrentTimeSeconds((time: number) => {
      if (time + timestep >= endTimeSeconds) {
        clearInterval(intervalRef.current);
        intervalRef.current = undefined;
        setIsPlaying(false);
        return endTimeSeconds;
      }
      return time + timestep
    });
  }

  const handleClick = () => {
    if (isPlaying) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = undefined;
      }
      setIsPlaying(false);
    } else {
      intervalRef.current = setInterval(intervalFunction, intervalTimeout);
      setIsPlaying(true);
    }
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="absolute bottom-3 left-4 z-[1000]">
      <div className="bg-zinc-950/40 backdrop-blur-md border border-zinc-900 rounded-md shadow-2xl p-4 w-fit">
        <div className="flex flex-col gap-2">
          {/* Header */}
          <div className="flex items-center justify-between">
            <span className="text-lg font-semibold text-zinc-100 leading-tight">
              Time Control
            </span>
          </div>

          {/* Time slider section */}
          <div className="flex items-center gap-2">
            {/* Start time label */}
            <span className="text-xs font-mono text-zinc-500">
              {startTime}
            </span>

            {/* Slider Wrapper */}
            <div className="flex-1 min-w-[200px]">
              <Slider
                value={[currentStep]}
                onValueChange={handleSliderChange}
                min={0}
                max={totalSteps}
                step={1}
                className="w-full"
              />
              {/* Current time display */}
              <div className="text-center mt-1">
                <span className="text-sm font-mono font-bold text-zinc-400">
                  {currentTime}
                </span>
              </div>
            </div>

            {/* End time label */}
            <span className="text-xs font-mono text-zinc-500 min-w-[45px] text-right">
              {endTime}
            </span>

            {/* Play/Pause button */}
            <button
              onClick={handleClick}
              style={{ minWidth: '40px', minHeight: '40px' }}
              className="flex items-center justify-center bg-zinc-900 rounded hover:bg-zinc-800 transition-colors"
            >
              {isPlaying ? (
                <Pause size={20} className="text-zinc-400" />
              ) : (
                <Play size={20} className="text-zinc-400" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
