import { NextResponse } from 'next/server';
import axios from 'axios';

// पाणिनी का 'सिस्टम प्रॉम्प्ट' जो AI को नियम सिखाएगा
const PANINI_LOGIC = `
You are the "Panini Grammar Engine" (Ashtadhyayi AI). 
Your goal is to process every input string using the 4,000 sutras of Panini.

RULES:
1. Identify if the input is a 'Dhatu' (Root), 'Pratipadika' (Stem), or 'Pada' (Word).
2. Apply sutras in chronological order (1.1.1 to 8.4.68).
3. If multiple sutras apply, use the rule "Vipratishedhe Param Karyam" (1.4.2).
4. For every transformation, cite the Sutra Number and its logic.
5. Provide output in this format: 
   - Input: [Word]
   - Process: [Sutra Number] -> [Transformation]
   - Final Output: [Sanskrit Word]
   - Translation: [User's Language]

Always prioritize the logic of 'Pratyahara' (Maheshwara Sutras) for phonological changes.
`;

export async function POST(req: Request) {
  try {
    const body = await req.json();

    if (body.message_type === 'incoming' && body.event === 'message_created') {
      const userMessage = body.content;
      const conversationId = body.conversation.id;
      const accountId = body.account.id;

      // 1. Gemini API Call with System Instruction
      const geminiRes = await axios.post(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
        {
          // यहाँ हमने 'system_instruction' जोड़ दिया है
          system_instruction: {
            parts: [{ text: PANINI_LOGIC }]
          },
          contents: [{
            parts: [{ text: userMessage }]
          }]
        }
      );

      const botReply = geminiRes.data.candidates[0].content.parts[0].text;

      // 2. Chatwoot API को रिप्लाई भेजना
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
    console.error("Gemini-Panini Bridge Error:", error);
    return NextResponse.json({ status: 'error' }, { status: 500 });
  }
}
