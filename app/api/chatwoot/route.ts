import { NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(req: Request) {
  try {
    // Sahi tareeka: req.json() use karein
    const body = await req.json();

    // Sirf user ke messages (incoming) par reply dena hai
    if (body.message_type === 'incoming' && body.event === 'message_created') {
      const userMessage = body.content;
      const conversationId = body.conversation.id;
      const accountId = body.account.id;

      // 1. Gemini API se response mangna
      const geminiRes = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
        {
          contents: [{
            parts: [{ text: userMessage }]
          }]
        }
      );

      const botReply = geminiRes.data.candidates[0].content.parts[0].text;

      // 2. Chatwoot API ko wapas reply bhejna
      await axios.post(
        `https://chatwoot.ayus.fun/api/v1/accounts/${accountId}/conversations/${conversationId}/messages`,
        {
          content: botReply,
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
    console.error("Gemini-Chatwoot Bridge Error:", error);
    return NextResponse.json({ status: 'error' }, { status: 500 });
  }
}
