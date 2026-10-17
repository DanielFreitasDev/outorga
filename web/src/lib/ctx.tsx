import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "./api";
import type { Politica, Saude } from "./types";

interface Ctx {
  saude: Saude | null;
  politica: Politica | null;
  erroConexao: string | null;
  atualizar: () => Promise<void>;
  tema: "claro" | "escuro";
  alternarTema: () => void;
}

const AppCtx = createContext<Ctx | null>(null);

function temaInicial(): "claro" | "escuro" {
  return document.documentElement.getAttribute("data-theme") === "dark" ? "escuro" : "claro";
}

export function ProvedorApp({ children }: { children: ReactNode }) {
  const [saude, setSaude] = useState<Saude | null>(null);
  const [politica, setPolitica] = useState<Politica | null>(null);
  const [erroConexao, setErro] = useState<string | null>(null);
  const [tema, setTema] = useState<"claro" | "escuro">(temaInicial);

  const atualizar = useCallback(async () => {
    try {
      const s = await api.saude();
      setSaude(s);
      setPolitica(s.politica);
      setErro(null);
    } catch (e) {
      setErro((e as Error).message);
    }
  }, []);

  useEffect(() => {
    atualizar();
    const t = setInterval(atualizar, 15000);
    return () => clearInterval(t);
  }, [atualizar]);

  const alternarTema = useCallback(() => {
    setTema((t) => {
      const novo = t === "claro" ? "escuro" : "claro";
      document.documentElement.setAttribute("data-theme", novo === "escuro" ? "dark" : "light");
      try {
        localStorage.setItem("outorga-tema", novo);
      } catch {
        /* armazenamento indisponível: preferência vale só nesta sessão */
      }
      return novo;
    });
  }, []);

  return (
    <AppCtx.Provider value={{ saude, politica, erroConexao, atualizar, tema, alternarTema }}>{children}</AppCtx.Provider>
  );
}

export function useApp(): Ctx {
  const c = useContext(AppCtx);
  if (!c) throw new Error("useApp fora do ProvedorApp");
  return c;
}
