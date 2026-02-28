import { NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(req: Request) {
  const body = await req.body.json();

  // 1. Check karo ki message user ne bheja hai (Incoming)
  if (body.message_type === 'incoming' && body.event === 'message_created') {
    const userMessage = body.content;
    const conversationId = body.conversation.id;
    const accountId = body.account.id;

    try {
      // 2. Gemini API ko message bhejo (Tumhara purana logic)
      // Yahan apna GEMINI_API_KEY environment variable mein set karna
      const geminiRes = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${process.env.GEMINI_API_KEY}`,
        { contents: [{ parts: [{ text: userMessage }] }] }
      );

      const botReply = geminiRes.data.candidates[0].content.parts[0].text;

      // 3. Chatwoot API ko reply bhejo
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
    } catch (error) {
      console.error("Error in Gemini-Chatwoot Bridge:", error);
    }
  }

  return NextResponse.json({ status: 'success' });
}

