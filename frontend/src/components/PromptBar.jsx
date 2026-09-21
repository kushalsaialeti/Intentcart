import { isValidElement, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { animate, useMotionValue, useMotionValueEvent, useReducedMotion } from 'framer-motion';
import {
  ChevronDown,
  Paperclip,
  X,
  FileText,
  Globe,
  Plus,
  Check,
  ShoppingBag,
  Tag
} from 'lucide-react';
import './PromptBar.css';

const ARROW_UP = [12, 4.5, 18.5, 11, 14.25, 11, 14.25, 19.5, 9.75, 19.5, 9.75, 11, 5.5, 11];
const SQUARE = [12, 6, 18, 6, 18, 12, 18, 18, 6, 18, 6, 12, 6, 6];
const EASE_IN_OUT = [0.77, 0, 0.175, 1];
const LINE = 22;

const DEFAULT_SOURCES = [
  {
    key: 'files',
    name: 'Photos & styles',
    description: 'Upload outfit reference',
    icon: Paperclip,
    attach: true
  },
  { key: 'catalog', name: 'Store Catalog', description: '1,200+ indexed items', icon: ShoppingBag },
  { key: 'trends', name: 'Style Trends', description: 'Live aesthetic signals', icon: Globe },
  { key: 'deals', name: 'Budget deals', description: 'Under ₹1,500 filters', icon: Tag }
];

const DEFAULT_COMMANDS = [
  { key: 'casual', name: '/casual', description: 'Relaxed everyday aesthetics' },
  { key: 'formal', name: '/formal', description: 'Office & business wear' },
  { key: 'ethnic', name: '/ethnic', description: 'Kurtas, sarees & festive' },
  { key: 'party', name: '/party', description: 'Evening & party glam' },
  { key: 'summer', name: '/summer', description: 'Breathable lightweight cotton' }
];

const DEFAULT_MODELS = [
  { key: 'auto', name: 'Auto ', tag: 'Fastest' },
  { key: 'groq', name: 'Groq LLaMA 3.3', tag: 'Fast' },
  { key: 'gemini', name: 'Gemini 1.5 Flash', tag: 'Smart' }
];

const mix = (a, b, t) => a + (b - a) * t;
const pathAt = (a, b, t) => {
  let d = '';
  for (let i = 0; i < a.length; i += 2) {
    d += `${i ? 'L' : 'M'}${mix(a[i], b[i], t).toFixed(2)} ${mix(a[i + 1], b[i + 1], t).toFixed(2)}`;
  }
  return `${d}Z`;
};

const parseToken = draft => {
  const m = /(^|\s)([@/])([\w-]*)$/.exec(draft);
  if (!m) return null;
  return { kind: m[2] === '@' ? 'at' : 'slash', query: m[3].toLowerCase(), start: m.index + m[1].length };
};

const renderIcon = (IconComponent, size = 15) => {
  if (!IconComponent) return null;
  if (isValidElement(IconComponent)) return IconComponent;
  return <IconComponent size={size} strokeWidth={1.8} />;
};

function SendGlyph({ busy, morphDuration, squash, tilt }) {
  const reduce = useReducedMotion();
  const svgRef = useRef(null);
  const pathRef = useRef(null);
  const dir = useRef(busy ? 1 : -1);
  const t = useMotionValue(busy ? 1 : 0);

  useEffect(() => {
    const target = busy ? 1 : 0;
    dir.current = busy ? 1 : -1;
    if (t.get() === target) return undefined;
    const controls = animate(
      t,
      target,
      reduce ? { duration: 0 } : { duration: morphDuration / 1000, ease: EASE_IN_OUT }
    );
    return () => controls.stop();
  }, [busy, morphDuration, reduce, t]);

  useMotionValueEvent(t, 'change', v => {
    pathRef.current?.setAttribute('d', pathAt(ARROW_UP, SQUARE, v));
    const goo = reduce ? 0 : Math.sin(v * Math.PI);
    const sx = 1 - squash * goo;
    if (svgRef.current) {
      svgRef.current.style.transform = goo ? `rotate(${dir.current * tilt * goo}deg) scale(${sx}, ${1 / sx})` : '';
    }
  });

  return (
    <svg
      ref={svgRef}
      className="prompt-bar__glyph"
      viewBox="0 0 24 24"
      aria-hidden="true"
      fill="currentColor"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinejoin="round"
    >
      <path ref={pathRef} d={pathAt(ARROW_UP, SQUARE, t.get())} />
    </svg>
  );
}

export default function PromptBar({
  value,
  onChange,
  placeholder = 'Describe what you need in natural language...',
  sources = DEFAULT_SOURCES,
  commands = DEFAULT_COMMANDS,
  models = DEFAULT_MODELS,
  defaultModel = 'auto',
  busy = false,
  onSend,
  onStop,
  onAttach,
  background = '#1c1c1f',
  color = '#f5f5f5',
  menuBackground = '#28282c',
  width = 680,
  radius = 20,
  maxRows = 5,
  morphDuration = 240,
  squash = 0.12,
  tilt = 8,
  pressScale = 0.96,
  className = ''
}) {
  const rootRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const glowRef = useRef(null);
  const rowRefs = useRef([]);
  const lastOpen = useRef(null);
  const latest = useRef({});
  latest.current = { onSend, onStop, onAttach };

  const [draft, setDraft] = useState(value || '');
  const [attachments, setAttachments] = useState([]);
  const [modelKey, setModelKey] = useState(defaultModel);
  const [plusOpen, setPlusOpen] = useState(false);
  const [modelOpen, setModelOpen] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [active, setActive] = useState(0);
  const [pressed, setPressed] = useState(false);

  // Synchronize internal draft when external `value` prop changes
  useEffect(() => {
    if (value !== undefined && value !== draft) {
      setDraft(value);
    }
  }, [value]);

  const model = models.find(m => m.key === modelKey) ?? models[0];
  const token = dismissed ? null : parseToken(draft);
  const open = plusOpen ? 'at' : (token?.kind ?? (modelOpen ? 'model' : null));
  const query = plusOpen ? '' : (token?.query ?? '');

  const list = useMemo(() => {
    if (open === 'at') return sources.filter(s => s.name.toLowerCase().includes(query));
    if (open === 'slash') return commands.filter(c => c.name.replace(/^\//, '').toLowerCase().startsWith(query));
    if (open === 'model') return models;
    return [];
  }, [open, query, sources, commands, models]);

  const cursor = Math.min(active, Math.max(0, list.length - 1));
  const canSend = draft.trim().length > 0 || attachments.length > 0;
  const armed = busy || canSend;

  const focusInput = () => inputRef.current?.focus({ preventScroll: true });
  const closeMenus = useCallback(() => {
    setPlusOpen(false);
    setModelOpen(false);
  }, []);

  useLayoutEffect(() => {
    const glow = glowRef.current;
    if (!glow || !open) return;
    const row = rowRefs.current[cursor];
    if (!row) {
      glow.style.opacity = '0';
      return;
    }
    const fresh = lastOpen.current !== open;
    lastOpen.current = open;
    if (fresh) glow.style.transition = 'none';
    glow.style.top = `${row.offsetTop}px`;
    glow.style.height = `${row.offsetHeight}px`;
    glow.style.opacity = '1';
    if (fresh) {
      void glow.offsetHeight;
      glow.style.transition = '';
    }
  }, [open, cursor, list]);

  useEffect(() => {
    if (!open) lastOpen.current = null;
  }, [open]);

  useEffect(() => {
    if (!plusOpen && !modelOpen) return undefined;
    const onDown = e => {
      if (!rootRef.current?.contains(e.target)) closeMenus();
    };
    document.addEventListener('pointerdown', onDown);
    return () => document.removeEventListener('pointerdown', onDown);
  }, [plusOpen, modelOpen, closeMenus]);

  useLayoutEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = '0px';
    const max = LINE * maxRows;
    el.style.height = `${Math.min(el.scrollHeight, max)}px`;
    el.style.overflowY = el.scrollHeight > max ? 'auto' : 'hidden';
  }, [draft, maxRows]);

  const handleFileUpload = e => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    const names = files.map(f => f.name);
    setAttachments(a => [...a, ...names]);
    e.target.value = '';
  };

  const pick = row => {
    if (open === 'model') {
      setModelKey(row.key);
      setModelOpen(false);
      focusInput();
      return;
    }
    const head = token ? draft.slice(0, token.start) : draft;
    if (row.attach) {
      setDraft(head);
      if (latest.current.onAttach) {
        Promise.resolve(latest.current.onAttach()).then(files => {
          if (!files) return;
          setAttachments(a => [...a, ...(Array.isArray(files) ? files : [files])]);
        });
      } else {
        fileInputRef.current?.click();
      }
    } else if (open === 'at') {
      const next = `${head}@${row.name} `;
      setDraft(next);
      onChange?.(next);
    } else {
      const next = `${head}${row.name} `;
      setDraft(next);
      onChange?.(next);
    }
    setPlusOpen(false);
    setDismissed(false);
    focusInput();
  };

  const send = () => {
    if (!canSend || busy) return;
    const trimmed = draft.trim();
    latest.current.onSend?.(trimmed, { attachments, model });
    setDraft('');
    onChange?.('');
    setAttachments([]);
    setDismissed(false);
    closeMenus();
    focusInput();
  };

  const onKeyDown = e => {
    if (open && list.length) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        setActive((cursor + (e.key === 'ArrowDown' ? 1 : list.length - 1)) % list.length);
        return;
      }
      if ((e.key === 'Enter' && !e.shiftKey) || e.key === 'Tab') {
        e.preventDefault();
        pick(list[cursor]);
        return;
      }
    }
    if (e.key === 'Escape') {
      if (open) {
        e.preventDefault();
        setDismissed(true);
        closeMenus();
      }
      return;
    }
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      send();
    }
  };

  const down = e => {
    if (e.button !== 0 || !armed) return;
    setPressed(true);
  };
  const up = () => setPressed(false);

  return (
    <div
      ref={rootRef}
      className={`prompt-bar${className ? ` ${className}` : ''}`}
      data-busy={busy ? '' : undefined}
      style={{
        '--pb-bg': background,
        '--pb-ink': color,
        '--pb-menu': menuBackground,
        '--pb-w': `${width}px`,
        '--pb-radius': `${radius}px`,
        '--pb-press': pressScale
      }}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />

      {open ? (
        <div
          className="prompt-bar__menu"
          role="listbox"
          aria-label={
            open === 'at' ? 'Sources' : open === 'slash' ? 'Commands' : 'Models'
          }
          data-kind={open}
        >
          <span ref={glowRef} className="prompt-bar__glow" aria-hidden="true" />
          {list.map((row, i) => (
            <button
              key={row.key}
              ref={el => {
                rowRefs.current[i] = el;
              }}
              type="button"
              role="option"
              aria-selected={i === cursor}
              className="prompt-bar__row"
              onMouseDown={e => e.preventDefault()}
              onPointerEnter={() => setActive(i)}
              onClick={() => pick(row)}
            >
              {open === 'at' ? <span className="prompt-bar__row-icon">{renderIcon(row.icon, 15)}</span> : null}
              <span className="prompt-bar__row-name">{row.name}</span>
              {row.description ? <span className="prompt-bar__row-desc">{row.description}</span> : null}
              {open === 'model' ? (
                <>
                  <span className="prompt-bar__row-tag">{row.tag}</span>
                  <span className="prompt-bar__row-check" data-on={row.key === model?.key ? '' : undefined}>
                    <Check size={13} strokeWidth={2.5} />
                  </span>
                </>
              ) : null}
            </button>
          ))}
          {list.length === 0 ? <div className="prompt-bar__empty">No matches for “{query}”</div> : null}
        </div>
      ) : null}

      <div
        className="prompt-bar__field"
        role="presentation"
        onPointerDown={e => {
          if (e.target === e.currentTarget || e.target === inputRef.current) closeMenus();
        }}
        onClick={focusInput}
      >
        {attachments.length > 0 ? (
          <div className="prompt-bar__chips">
            {attachments.map((file, i) => (
              <span key={`${file}-${i}`} className="prompt-bar__chip">
                <FileText size={12} strokeWidth={2} />
                <span className="prompt-bar__chip-name">{file}</span>
                <button
                  type="button"
                  className="prompt-bar__chip-x"
                  aria-label={`Remove ${file}`}
                  onClick={() => setAttachments(a => a.filter((_, j) => j !== i))}
                >
                  <X size={10} strokeWidth={2.5} />
                </button>
              </span>
            ))}
          </div>
        ) : null}

        <textarea
          ref={inputRef}
          className="prompt-bar__input"
          rows={1}
          value={draft}
          placeholder={placeholder}
          aria-label="Prompt"
          onChange={e => {
            const next = e.target.value;
            setDraft(next);
            onChange?.(next);
            setDismissed(false);
            closeMenus();
            setActive(0);
          }}
          onFocus={closeMenus}
          onKeyDown={onKeyDown}
        />

        <div className="prompt-bar__bar">
          <button
            type="button"
            className="prompt-bar__tool"
            aria-label="Add files and sources"
            aria-expanded={plusOpen}
            data-on={plusOpen ? '' : undefined}
            onMouseDown={e => e.preventDefault()}
            onClick={() => {
              setModelOpen(false);
              setActive(0);
              setPlusOpen(v => !v);
              focusInput();
            }}
          >
            <Plus size={16} strokeWidth={2} />
          </button>
          {models.length > 0 ? (
            <button
              type="button"
              className="prompt-bar__pick"
              aria-label="Choose model"
              aria-expanded={modelOpen}
              data-on={modelOpen ? '' : undefined}
              onMouseDown={e => e.preventDefault()}
              onClick={() => {
                setPlusOpen(false);
                setActive(Math.max(0, models.indexOf(model)));
                setModelOpen(v => !v);
                focusInput();
              }}
            >
              <span>{model.name}</span>
              <ChevronDown size={12} strokeWidth={2.4} />
            </button>
          ) : null}
          <span className="prompt-bar__spacer" />
          <button
            type="button"
            className="prompt-bar__send"
            disabled={!armed}
            aria-label={busy ? 'Stop' : 'Send'}
            data-armed={armed ? '' : undefined}
            data-pressed={pressed ? '' : undefined}
            onMouseDown={e => e.preventDefault()}
            onPointerDown={down}
            onPointerUp={up}
            onPointerCancel={up}
            onPointerLeave={up}
            onClick={() => {
              if (busy) latest.current.onStop?.();
              else send();
            }}
          >
            <SendGlyph busy={busy} morphDuration={morphDuration} squash={squash} tilt={tilt} />
          </button>
        </div>
      </div>
    </div>
  );
}
