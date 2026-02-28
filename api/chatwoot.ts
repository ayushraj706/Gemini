import axios from 'axios';

export default async function handler(req: any, res: any) {
  if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');

  const body = req.body;

  // Check: Message user ne bheja hai aur event sahi hai
  if (body.message_type === 'incoming' && body.event === 'message_created') {
    const userMessage = body.content;
    const conversationId = body.conversation.id;
    const accountId = body.account.id;

    try {
      // 1. Gemini se jawab lein
      const geminiRes = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
        { contents: [{ parts: [{ text: userMessage }] }] }
      );
      const botReply = geminiRes.data.candidates[0].content.parts[0].text;

      // 2. Chatwoot ko reply bhejein
      await axios.post(
        `https://chatwoot.ayus.fun/api/v1/accounts/${accountId}/conversations/${conversationId}/messages`,
        { content: botReply, message_type: 'outgoing' },
        { headers: { 'api_access_token': process.env.CHATWOOT_TOKEN } }
      );
    } catch (error) {
      console.error("Error:", error);
    }
  }
  return res.status(200).json({ status: 'success' });
}

