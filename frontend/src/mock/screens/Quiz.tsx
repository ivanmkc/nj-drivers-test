import { HomeIndicator, StatusBar } from '../PhoneFrame';
import { SourceCitation } from '../SourceCitation';

const CHOICES = [
  { letter: 'A', text: 'Slow down and pass with caution.' },
  {
    letter: 'B',
    text: 'Stop and remain stopped until the red lights stop flashing.',
    selected: true,
  },
  { letter: 'C', text: 'Honk to alert the children.' },
  { letter: 'D', text: 'Speed up to clear the area.' },
];

export function Quiz({ variant }: { variant: 'light' | 'dark' }) {
  const isDark = variant === 'dark';
  const body = isDark ? 'text-ink-inverse' : 'text-ink';
  const subtle = isDark ? 'text-slate-400' : 'text-ink-subtle';
  const choiceBg = isDark ? 'bg-surface-card-dark border-line-dark' : 'bg-white border-line-light';
  const choiceLetterBg = isDark
    ? 'bg-surface-dark border-line-dark'
    : 'bg-slate-100 border-line-light';
  const choiceLetterText = isDark ? 'text-slate-200' : 'text-ink-muted';

  return (
    <div className="h-full flex flex-col">
      <StatusBar variant={variant} />

      {/* Top bar */}
      <div className="px-xl pt-md flex items-center justify-between">
        <button className={`${isDark ? 'text-accent-light' : 'text-primary'} text-sm font-medium`}>
          ← Exit
        </button>
        <div className={`${subtle} text-xs font-medium`}>12 / 25</div>
      </div>

      {/* Progress */}
      <div className="px-xl mt-sm">
        <div
          className={`${isDark ? 'bg-line-dark' : 'bg-line-light'} h-1 rounded-pill overflow-hidden`}
        >
          <div className="bg-accent h-full rounded-pill" style={{ width: '48%' }} />
        </div>
      </div>

      {/* Source citation */}
      <div className="px-xl mt-lg">
        <SourceCitation
          state="CA"
          agency="DMV"
          edition="2025 Driver Handbook"
          ref="§4 p.32"
          variant={variant}
        />
      </div>

      {/* Question */}
      <div className="px-xl mt-2xl flex-1">
        <div className={`${subtle} text-[11px] font-bold tracking-eyebrow uppercase mb-md`}>
          Safe driving rules
        </div>
        <h1 className={`${body} font-display text-[22px] font-semibold leading-snug`}>
          You are driving on a two-lane road and a school bus ahead has stopped with its red lights
          flashing. What must you do?
        </h1>

        <div className="space-y-md mt-xl">
          {CHOICES.map((c) =>
            c.selected ? (
              <div
                key={c.letter}
                className={
                  isDark
                    ? 'bg-accent rounded-lg p-md flex items-center gap-md'
                    : 'bg-primary rounded-lg p-md flex items-center gap-md'
                }
              >
                <div
                  className={`w-7 h-7 rounded-full bg-white flex items-center justify-center font-bold text-sm ${
                    isDark ? 'text-accent' : 'text-primary'
                  }`}
                >
                  {c.letter}
                </div>
                <span
                  className={`${
                    isDark ? 'text-ink' : 'text-white'
                  } text-sm font-semibold leading-snug flex-1`}
                >
                  {c.text}
                </span>
              </div>
            ) : (
              <div
                key={c.letter}
                className={`${choiceBg} border rounded-lg p-md flex items-center gap-md`}
              >
                <div
                  className={`${choiceLetterBg} ${choiceLetterText} w-7 h-7 rounded-full border flex items-center justify-center font-semibold text-sm`}
                >
                  {c.letter}
                </div>
                <span className={`${body} text-sm leading-snug flex-1`}>{c.text}</span>
              </div>
            ),
          )}
        </div>
      </div>

      {/* Submit */}
      <div className="px-xl pb-xl">
        <button
          className={`w-full rounded-lg py-md text-base font-semibold ${
            isDark ? 'bg-accent text-ink' : 'bg-primary text-white'
          }`}
        >
          Submit answer
        </button>
      </div>

      <HomeIndicator variant={variant} />
    </div>
  );
}
