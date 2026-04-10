"use client";

import { Maximize2, Minimize2 } from "lucide-react";

export function ChartFullscreenIconButton({
  isFullscreen,
  onToggle,
}: {
  isFullscreen: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onToggle()}
      className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-zinc-200 bg-white text-zinc-600 shadow-sm transition hover:border-zinc-300 hover:bg-zinc-50 hover:text-zinc-900 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:border-zinc-500 dark:hover:bg-zinc-800 dark:hover:text-zinc-50"
      title={isFullscreen ? "Thoát toàn màn hình" : "Xem toàn màn hình"}
      aria-label={isFullscreen ? "Thoát toàn màn hình" : "Xem toàn màn hình"}
    >
      {isFullscreen ? (
        <Minimize2 className="h-4 w-4" strokeWidth={2} aria-hidden />
      ) : (
        <Maximize2 className="h-4 w-4" strokeWidth={2} aria-hidden />
      )}
    </button>
  );
}
