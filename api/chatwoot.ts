import axios from 'axios';

export default async function handler(req: any, res: any) {
  if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');

  const body = req.body;
  const GEMINI_KEY = process.env.GEMINI_API_KEY;
  const CHATWOOT_TOKEN = process.env.CHATWOOT_TOKEN;
  const CHATWOOT_URL = "https://chatwoot.ayus.fun"; // Aapke screenshot ke hisab se

  if (body.message_type === 'incoming' && body.event === 'message_created') {
    const userMessage = body.content;
    const conversationId = body.conversation.id;
    const accountId = body.account.id;

    try {
      // 1. Pehle Gemini se pucho kaunse models hain
      const modelsRes = await axios.get(
        `https://generativelanguage.googleapis.com/v1/models?key=${GEMINI_KEY}`
      );
      
      // Models list se koi ek valid model pick karo (Prefer: 1.5-flash)
      const availableModels = modelsRes.data.models;
      let selectedModel = availableModels.find((m: any) => m.name.includes('gemini-1.5-flash'))?.name 
                         || availableModels.find((m: any) => m.name.includes('gemini-pro'))?.name 
                         || availableModels[0].name;

      console.log("Using Model:", selectedModel);

      // 2. Ab us selected model se answer mango
      const geminiRes = await axios.post(
        `https://generativelanguage.googleapis.com/v1/${selectedModel}:generateContent?key=${GEMINI_KEY}`,
        { contents: [{ parts: [{ text: userMessage }] }] }
      );

      const botReply = geminiRes.data.candidates[0].content.parts[0].text;

      // 3. Chatwoot ko reply bhejo
      await axios.post(
        `${CHATWOOT_URL}/api/v1/accounts/${accountId}/conversations/${conversationId}/messages`,
        { content: botReply, message_type: 'outgoing' },
        { headers: { 'api_access_token': CHATWOOT_TOKEN } }
      );

    } catch (error: any) {
      console.error("Error details:", error.response?.data || error.message);
    }
  }

  return res.status(200).json({ status: 'success' });
}
