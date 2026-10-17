import { ProvedorApp } from "./lib/ctx";
import { casar, useRota } from "./lib/router";
import { Shell } from "./components/Shell";
import { Demonstracao } from "./pages/Demonstracao";
import { NovaAnalise } from "./pages/NovaAnalise";
import { ConsultaCPF } from "./pages/ConsultaCPF";
import { PaginaAnalise, PaginaPrecalculado } from "./pages/Analise";
import { Historico } from "./pages/Historico";
import { Calibracao } from "./pages/Calibracao";
import { Auditoria } from "./pages/Auditoria";
import { ComoFunciona } from "./pages/ComoFunciona";
import { Vazio } from "./components/ui";

function Rotas({ rota }: { rota: string }) {
  let p: Record<string, string> | null;
  if (rota === "/" || rota === "/demo") return <Demonstracao />;
  if ((p = casar("/demo/:caso", rota))) return <PaginaPrecalculado key={p.caso} caso={p.caso} />;
  if (rota === "/consulta") return <ConsultaCPF key={window.location.search} />;
  if (rota === "/nova") return <NovaAnalise />;
  if ((p = casar("/analise/:id", rota))) return <PaginaAnalise key={p.id} id={p.id} />;
  if (rota === "/historico") return <Historico />;
  if (rota === "/calibracao") return <Calibracao />;
  if (rota === "/auditoria") return <Auditoria />;
  if (rota === "/como-funciona") return <ComoFunciona />;
  return <Vazio titulo="Página não encontrada">Use o menu para navegar.</Vazio>;
}

export function App() {
  const rota = useRota();
  return (
    <ProvedorApp>
      <Shell rota={rota}>
        <Rotas rota={rota} />
      </Shell>
    </ProvedorApp>
  );
}
