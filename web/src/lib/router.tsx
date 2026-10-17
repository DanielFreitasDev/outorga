import { useEffect, useState, type AnchorHTMLAttributes, type MouseEvent } from "react";

/** Roteador mínimo por pathname (a API serve o index.html para qualquer rota). */
export function navegar(caminho: string) {
  if (caminho === window.location.pathname + window.location.search) return;
  window.history.pushState({}, "", caminho);
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0 });
}

export function useRota(): string {
  const [rota, setRota] = useState(window.location.pathname);
  useEffect(() => {
    const f = () => setRota(window.location.pathname);
    window.addEventListener("popstate", f);
    return () => window.removeEventListener("popstate", f);
  }, []);
  return rota;
}

export function casar(padrao: string, rota: string): Record<string, string> | null {
  const p = padrao.split("/").filter(Boolean);
  const r = rota.split("/").filter(Boolean);
  if (p.length !== r.length) return null;
  const params: Record<string, string> = {};
  for (let i = 0; i < p.length; i++) {
    if (p[i].startsWith(":")) params[p[i].slice(1)] = decodeURIComponent(r[i]);
    else if (p[i] !== r[i]) return null;
  }
  return params;
}

export function Link({ href, onClick, ...resto }: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) {
  return (
    <a
      href={href}
      onClick={(e: MouseEvent<HTMLAnchorElement>) => {
        onClick?.(e);
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        e.preventDefault();
        navegar(href);
      }}
      {...resto}
    />
  );
}
