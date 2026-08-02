export default function Logo({ size = 48 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="PedroIA">
      <defs>
        <linearGradient id="pg" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
          <stop stopColor="#7c5cff" />
          <stop offset="1" stopColor="#22d3ee" />
        </linearGradient>
      </defs>
      <path d="M32 3L56 16.5v31L32 61 8 47.5v-31L32 3z" fill="url(#pg)" fillOpacity="0.12" stroke="url(#pg)" strokeWidth="2.2" strokeLinejoin="round" />
      <path d="M22 24l-6 8 6 8M42 24l6 8-6 8M35 19l-6 26" stroke="url(#pg)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
