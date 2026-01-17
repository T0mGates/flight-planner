import { useState } from 'react';
import { Play, Pause } from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import logo from '../../assets/plane_logo.png';

interface TimeControlsProps {
  startTimeSeconds: number; // Unix timestamp in seconds
  endTimeSeconds: number;   // Unix timestamp in seconds
  currentTimeSeconds: number; // Current time as unix timestamp
  setCurrentTimeSeconds: (time: number) => void; // Setter for current time
}
// Format unix timestamp to readable date/time
function formatTime(unixSeconds: number) {
  // Convert to milliseconds
  const date = new Date(unixSeconds * 1000);
  console.log(date);
  console.log(unixSeconds);
  return date.toLocaleString('en-US', {
    timeZone: "UTC",
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export default function TimeControls({
  startTimeSeconds,
  endTimeSeconds,
  currentTimeSeconds,
  setCurrentTimeSeconds
}: TimeControlsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const startTime = formatTime(startTimeSeconds);
  const endTime = formatTime(endTimeSeconds);
  const currentTime = formatTime(currentTimeSeconds);

  // Calculate the total duration in hours
  const totalDurationSeconds = endTimeSeconds - startTimeSeconds;
  const totalHours = totalDurationSeconds / 3600;

  // Handle slider change - convert hours back to unix seconds
  const handleSliderChange = (value: number[]) => {
    const newTimeSeconds = startTimeSeconds + (value[0] * 3600);
    setCurrentTimeSeconds(newTimeSeconds);
  };

  return (
    <div className="absolute bottom-3 left-0 z-[1000] flex items-center gap-0">
      {/* Logo - clickable */}
      <div onClick={() => setIsOpen(!isOpen)}>
        <img
          src={logo}
          alt="Flight Planner Logo"
          className="h-30 w-auto opacity-80 grayscale contrast-125 hover:opacity-100 transition-opacity"
        />
      </div>

      {/* Slide-out panel */}
      <div
        className={`
          bg-zinc-950 border border-zinc-800 rounded-md
          shadow-2xl
          transition-all duration-100 ease-in-out
          ${isOpen ? 'w-fit opacity-100 ml-2 p-4' : 'w-0 opacity-0 overflow-hidden'}
        `}
      >
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

            {/* Slider */}
            <div className="flex-1">
              <Slider
                defaultValue={[totalHours / 2]}
                onValueChange={handleSliderChange}
                min={0}
                max={totalHours}
                step={1}
                className="w-full"
              />
              {/* Current time display */}
              <div className="text-center mt-1">
                <span className="text-sm font-mono font-bold text-sinc-400">
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
              onClick={() => setIsPlaying(!isPlaying)}
              style={{ minWidth: '40px', minHeight: '40px' }}
              className="flex items-center justify-center bg-zinc-900"
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
