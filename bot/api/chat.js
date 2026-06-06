/**
 * Vercel Serverless Function — /api/chat
 * Proxy para OpenAI GPT-4 com contexto da Passos Mágicos
 */

const OPENAI_API = 'https://api.openai.com/v1/chat/completions';

// Contexto RAG simplificado sobre a ONG (substitui ChromaDB para MVP)
const ONG_CONTEXT = `
CONTEXTO — PASSOS MÁGICOS (dados 2022-2024):

SOBRE A ONG:
- Fundada em 1992 em Embu-Guaçu (SP)
- Missão: transformar a vida de crianças e jovens vulneráveis através da educação
- Programa: reforço escolar, aulas de inglês, atividades culturais, suporte psicossocial
- Bolsas universitárias para alunos destaque

DATASET:
- 2022: 860 alunos | 2023: 1.014 alunos | 2024: 1.156 alunos
- Crescimento de ~34% no período

INDICADORES (escala 0-10):
- IAN: Adequação de Nível — mede se o aluno está na fase correta para sua idade
- IDA: Desempenho Acadêmico — média de Matemática, Português e Inglês
- IEG: Engajamento — participação, presença, comportamento
- IAA: Autoavaliação — percepção do aluno sobre seu próprio desenvolvimento
- IPS: Indicador Psicossocial — saúde emocional e social
- IPP: Indicador Psicopedagógico — avaliação psicopedagógica (2023+)
- IPV: Indicador de Ponto de Virada — transformação da trajetória do aluno
- INDE: Índice de Desenvolvimento Educacional — índice síntese geral

PEDRAS (classificação de desenvolvimento):
- Quartzo: INDE < 5.5 (necessita atenção especial)
- Ágata: 5.5 ≤ INDE < 7.0 (desenvolvimento básico)
- Ametista: 7.0 ≤ INDE < 8.5 (bom desenvolvimento)
- Topázio: INDE ≥ 8.5 (excelência)

DEFASAGEM: diferença entre fase real e fase ideal para a idade
- Negativa: aluno adiantado
- Zero: aluno na fase correta
- Positiva: aluno em atraso escolar

CORRELAÇÕES CHAVE (análise 2022-2024):
- IAN tem maior correlação com risco de defasagem
- IDA e IEG têm maior correlação com INDE
- IPV correlaciona com IEG — engajamento precede o ponto de virada

MODELO PREDITIVO:
- Algoritmo: Random Forest / XGBoost
- AUC-ROC: ~0.82 no conjunto de teste (2024)
- Features mais importantes: IAN, INDE, IDA, Fase, gap_ian_fase
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
