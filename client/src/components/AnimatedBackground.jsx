/**
 * AnimatedBackground — cinematic liquid morphism layer.
 *
 * Three large, blurred gradient blobs that drift slowly across the viewport.
 * Pure CSS animation (GPU-composited via will-change + transform),
 * no per-frame JS, no canvas overhead, no emoji.
 */

export default function AnimatedBackground() {
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}>
      {/* Blob 1 — cyan, top-left drift */}
      <div className="liquid-blob liquid-blob-1" />

      {/* Blob 2 — purple, bottom-right drift */}
      <div className="liquid-blob liquid-blob-2" />

      {/* Blob 3 — red accent, center drift */}
      <div className="liquid-blob liquid-blob-3" />

      {/* Mesh gradient overlay */}
      <div className="mesh-gradient" />
    </div>
  )
}
