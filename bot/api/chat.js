/**
 * Vercel Serverless Function — /api/chat
 * Proxy para OpenAI GPT-4 com contexto da Passos Mágicos
 */

const OPENAI_API = 'https://api.openai.com/v1/chat/completions';

// Contexto RAG sobre a ONG — atualizado com Relatório de Atividades 2025
const ONG_CONTEXT = `
CONTEXTO — PASSOS MÁGICOS (Relatório 2025 + dados históricos 2022-2024):

SOBRE A ONG:
- Fundada em 1992 em Embu-Guaçu (SP) por Dimetri e Michelle Ivanoff
- Missão: transformar a vida de crianças e jovens em vulnerabilidade social por meio da educação
- 4 unidades distribuídas em Embu-Guaçu · 63 colaboradores + voluntários
- Receita 2025: ~R$ 8,8 milhões (maiores fontes: doações PF 30,3%, FUMCAD 26,7%, Rouanet 10,3%)
- Reconhecimentos: Top 100 ONGs do Brasil · Prêmio Excelência Poliedro 2024 (3º em Gestão Escolar) e 2025 (1º em Tecnologia — Jovens Inventores)

IMPACTO 2025:
- 1.200 aprendizes atendidos (11,3% dos alunos da rede pública municipal)
- 120 crianças alfabetizadas fora da idade esperada
- 119 universitários cursando ou formados
- 87 no mercado de trabalho (salário médio R$ 2.772)
- 14.000+ horas de oficinas no PAC
- 7.570 livros lidos | 466 aprendizes com aulas de inglês | 712 beneficiados por tecnologia

PERFIL DOS APRENDIZES (2025):
- Faixa etária: 40,8% entre 11-14 anos, 26% entre 7-10 anos, 24,2% entre 15-18 anos
- Gênero: 52,5% meninas, 47,5% meninos
- Etnia: 51,6% brancos, 35,5% pardos, 11,3% pretos

PROGRAMA DE ACELERAÇÃO DO CONHECIMENTO (PAC):
- Estruturado em Fase Alfa (alfabetização) + Fases 1 a 9
- Turmas reduzidas: até 15 aprendizes por grupo
- Ingresso por avaliação diagnóstica (nível de conhecimento, não idade)
- Fase 10 prevista a partir de 2025

DISCIPLINAS E PROGRAMAS EDUCACIONAIS:
- Português (4.071h/ano): Mala Mágica (Alfa/F1/F2), Histórias e Encantos (F3), Leitura Mágica (F4-F7), Lendo Clássicos (F8-F10)
- Matemática (3.987h/ano): atividades lúdicas + voluntários fins de semana
- Inglês (1.438h/ano): Speed Up (conversação com voluntários internacionais) + Math Adventures in English (F3) + Canada Experience (7 selecionados/ano)
- Robótica: Jovens Inventores (kits LEGO, parceria Fundação Salvador Arena) — 48 turmas
- Tecnologia: Sala Cibernética (programação, 12 turmas — fases 3 e 4)

PROGRAMAS DE PSICOLOGIA (por fase):
- Fase Alfa: Heróis da Educação (habilidades cognitivas)
- Fase 1: Guardiões do Saber
- Fase 2: Sabedoria em Ação
- Fase 3: Exploradores do Saber (autoconhecimento)
- Fase 4: Jornada das Emoções (psicologia positiva)
- Fase 5: Quebrando Barreiras (resiliência)
- Fase 6: SuperAção (habilidades interpessoais)
- Fase 7: Eu no Comando (equilíbrio emocional)
- Fase 8: Ponto de Virada (pensamento crítico vocacional)
- Fase 9: Conectando Passos (escolha profissional, vícios digitais)
- Fase 10: Passos em Carreiras (softskills, carreira)
- Pais/responsáveis: Passos em Família (56 encontros/ano)

SERVIÇO SOCIAL (2025):
- 389 cestas básicas entregues · 315 visitas domiciliares
- 336 famílias no Café em Família · 57 participantes Mães no Mercado de Trabalho

BOLSAS E CAMINHOS:
- Ensino Fundamental/Médio: 121 bolsistas (Arco-Íris 106, FIAP School 17, Einstein 10, Poliedro 4, FECAP 1)
- Casa Mágica: 31 aprendizes em 5 apartamentos em SP (custeio total da ONG)
- Universidade (Vem Ser): 30 aprovados em 2025 · 119 universitários acumulados
- Mercado de trabalho: 87 jovens (62,1% CLT/PJ, 36,8% estágio, 1,1% jovem aprendiz)

INDICADORES (escala 0-10):
- IAN: Adequação de Nível — mede se o aluno está na fase correta para sua idade
- IDA: Desempenho Acadêmico — média em Matemática, Português e Inglês
- IEG: Engajamento — presença, participação, comportamento
- IAA: Autoavaliação — percepção do aluno sobre seu próprio desenvolvimento
- IPS: Indicador Psicossocial — saúde emocional e relações sociais
- IPP: Indicador Psicopedagógico — avaliação psicopedagógica (disponível desde 2023)
- IPV: Ponto de Virada — indicador de transformação da trajetória
- INDE: Índice de Desenvolvimento Educacional — síntese de todos os indicadores

PEDRAS (classificação pelo INDE — não selecionada pelo aluno):
- Quartzo: INDE < 5,5 (atenção especial — risco de defasagem)
- Ágata: 5,5 ≤ INDE < 7,0 (desenvolvimento em curso)
- Ametista: 7,0 ≤ INDE < 8,5 (bom desenvolvimento)
- Topázio: INDE ≥ 8,5 (excelência)

MODELO PREDITIVO (sistema Radar de Risco):
- Algoritmo: Random Forest treinado em 2022+2023+2024 (~3.030 alunos, OOF 5-fold)
- Target composto: (Defasagem ≥ 1 ano) OU (INDE < 5,5 — Quartzo)
- AUC-ROC OOF: 0,9695 · Threshold: 61% (Fbeta β=2)
- Features mais importantes: INDE, inde×IAN, gap_ian_fase, Fase
- Zonas de risco: Alto ≥ 61% · Médio 40-61% · Baixo < 40%
`.trim();

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { messages, mode, userMessage } = req.body;

  if (!userMessage || !messages) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'OPENAI_API_KEY not configured' });
  }

  // Injeta contexto RAG na mensagem do sistema
  const systemWithContext = messages[0]?.content
    ? messages[0].content + '\n\n' + ONG_CONTEXT
    : ONG_CONTEXT;

  const messagesWithContext = [
    { role: 'system', content: systemWithContext },
    ...messages.slice(1),
    { role: 'user', content: userMessage }
  ];

  try {
    const response = await fetch(OPENAI_API, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: messagesWithContext,
        max_tokens: 800,
        temperature: mode === 'radar' ? 0.3 : 0.7,
        stream: false
      })
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('OpenAI error:', error);
      return res.status(502).json({ error: 'OpenAI API error', details: error });
    }

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content ?? 'Desculpe, não consegui processar sua resposta.';

    return res.status(200).json({ reply });
  } catch (err) {
    console.error('Handler error:', err);
    return res.status(500).json({ error: 'Internal server error', message: err.message });
  }
}
