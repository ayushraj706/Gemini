import { NextResponse } from 'next/server';
import axios from 'axios';

const PANINI_LOGIC = `
You are the "Panini Grammar Engine". 
Task: Process input via Ashtadhyayi rules concisely.
Output Format:
- **Input**: [Word]
- **Sutra**: [No. & Brief Rule]
- **Output**: [Sanskrit Result]
- **Meaning**: [Short Meaning]
Constraint: Use bullet points. Keep it short for mobile screens.
`;

export async function POST(req: Request) {
  try {
    const body = await req.json();

    if (body.message_type === 'incoming' && body.event === 'message_created') {
      const userMessage = body.content;
      const conversationId = body.conversation.id;
      const accountId = body.account.id;

      // 1. Chatwoot को बताओ कि AI "Type" कर रहा है (Skeleton जैसा अहसास)
      await axios.post(
        `https://chatwoot.ayus.fun/api/v1/accounts/${accountId}/conversations/${conversationId}/toggle_typing_status`,
        { command: 'on' },
        { headers: { 'api_access_token': process.env.CHATWOOT_TOKEN } }
      );

      // 2. Gemini API Call (इसमें समय लगता है)
      const geminiRes = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
        {
          system_instruction: { parts: [{ text: PANINI_LOGIC }] },
          contents: [{ parts: [{ text: userMessage }] }],
          generationConfig: { temperature: 0.1, maxOutputTokens: 600 }
        }
      );

      let botReply = geminiRes.data.candidates[0].content.parts[0].text;
      const finalReply = botReply + "\n\n."; 

      // 3. Typing Status को 'off' करो और जवाब भेजो
      await axios.post(
        `https://chatwoot.ayus.fun/api/v1/accounts/${accountId}/conversations/${conversationId}/toggle_typing_status`,
        { command: 'off' },
        { headers: { 'api_access_token': process.env.CHATWOOT_TOKEN } }
      );

      await axios.post(
        `https://chatwoot.ayus.fun/api/v1/accounts/${accountId}/conversations/${conversationId}/messages`,
        {
          content: finalReply,
          message_type: 'outgoing',
        },
        {
          headers: {
            'api_access_token': process.env.CHATWOOT_TOKEN,
            'Content-Type': 'application/json',
          },
        }
      );
    }

    return NextResponse.json({ status: 'success' });
  } catch (error) {
    console.error("Gemini-Panini Bridge Error:", error);
    return NextResponse.json({ status: 'error' }, { status: 500 });
  }
}
