import { HomeIndicator, StatusBar } from '../PhoneFrame';

export function Home({ variant }: { variant: 'light' | 'dark' }) {
  const isDark = variant === 'dark';
  const body = isDark ? 'text-ink-inverse' : 'text-ink';
  const subtle = isDark ? 'text-slate-400' : 'text-ink-subtle';
  const cardBg = isDark ? 'bg-surface-card-dark' : 'bg-surface-card-light';
  const cardBorder = isDark ? 'border-line-dark' : 'border-line-light';
  const secondaryBg = isDark
    ? 'bg-surface-card-dark border-line-dark'
    : 'bg-white border-line-light';
  const secondaryText = isDark ? 'text-ink-inverse' : 'text-primary';
  const divider = isDark ? 'border-line-dark' : 'border-line-light';

  return (
    <div className="h-full flex flex-col">
      <StatusBar variant={variant} />

      {/* Hero */}
      <div className="bg-gradient-to-b from-primary to-primary-hover px-xl pt-xl pb-2xl">
        <div className="text-accent text-[11px] font-bold tracking-eyebrow mb-md">
          DRIVER&apos;S TEST PREP
        </div>
        <h1 className="font-display text-[44px] leading-tight font-semibold text-white">
          Study from
        </h1>
        <h1 className="font-display text-[44px] leading-tight font-semibold text-white">
          the real manual.
        </h1>
        <p className="text-slate-300 text-sm mt-md leading-snug">
          Practice tests grounded in official driver handbooks from 50 US jurisdictions.
        </p>
      </div>

      <div className="h-[3px] bg-accent" />

      {/* State card */}
      <div className="px-xl pt-xl pb-md">
        <div className={`${subtle} text-[11px] font-bold tracking-eyebrow uppercase mb-sm`}>
          Your state
        </div>
        <div className={`${cardBg} ${cardBorder} border rounded-lg flex overflow-hidden`}>
          <div className="w-1 bg-accent" />
          <div className="p-md flex-1">
            <div className="flex items-center gap-md mb-sm">
              <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center font-display font-bold text-white text-[13px]">
                CA
              </div>
              <div>
                <div className={`${body} font-display font-semibold text-lg`}>California</div>
                <div className={`${subtle} text-xs`}>Department of Motor Vehicles</div>
              </div>
            </div>
            <div className="text-accent-dark text-[11px] tracking-wider">
              CA · DMV · 2025 Driver Handbook
            </div>
            <div className={`${subtle} text-[11px] mt-1`}>284 questions · EN · ES · JA</div>
          </div>
        </div>
      </div>

      {/* CTAs */}
      <div className="px-xl space-y-md">
        <button className="w-full bg-primary text-white font-semibold rounded-lg py-md text-base">
          Begin practice test
        </button>
        <div className="grid grid-cols-2 gap-md">
          <button
            className={`${secondaryBg} border rounded-md py-md text-sm font-medium ${secondaryText}`}
          >
            Change state
          </button>
          <button
            className={`${secondaryBg} border rounded-md py-md text-sm font-medium ${secondaryText}`}
          >
            Your stats
          </button>
        </div>
      </div>

      {/* Trust footer */}
      <div className="mt-auto px-xl pb-xl">
        <div className={`${divider} border-t pt-md`}>
          <div className="text-accent-dark text-[11px] font-bold tracking-eyebrow uppercase mb-1">
            Sourced from official .gov manuals
          </div>
          <div className={`${subtle} text-[11px]`}>
            Every question traces to a real DMV publication.{' '}
            <span className={isDark ? 'text-accent-light' : 'text-primary'}>View sources →</span>
          </div>
        </div>
      </div>

      <HomeIndicator variant={variant} />
    </div>
  );
}
