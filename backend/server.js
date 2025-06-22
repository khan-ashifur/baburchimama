const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const dotenv = require('dotenv');
const OpenAI = require('openai');

dotenv.config();

const app = express();
app.use(cors());
app.use(bodyParser.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

app.post('/ask-mama', async (req, res) => {
  try {
    const { dish, people } = req.body;

    const chatCompletion = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `তুমি একজন অভিজ্ঞ ঢাকাইয়া শেফ। তুমি খুবই হাসিখুশি ভাবে উত্তর দাও। ব্যবহারকারীর দেয়া খাবারের নাম দেখে তাদের জন্য সুন্দর সহজ ভাষায় একদম নির্ভুল রেসিপি বলবে। 
          প্রথম লাইনে বলবে: "মামা চিন্তা করতাসি, খারান..." তারপর রেসিপি দেবে।
          `,
        },
        {
          role: 'user',
          content: `মামা, ${people} জনের জন্য ${dish} রান্না করুম। কিভাবে করুম?`,
        },
      ],
      max_tokens: 1200,
      temperature: 0.8,
    });

    const reply = chatCompletion.choices[0].message.content;
    console.log('✅ AI Reply:', reply);
    res.json({ reply });
  } catch (error) {
    console.error('❌ ERROR:', error);
    res.status(500).json({ reply: 'মামা, কিছু গন্ডগোল হইছে... একটু পরে ট্রাই করুম।' });
  }
});

app.post('/suggest-mama', async (req, res) => {
  try {
    const { items, people } = req.body;

    const chatCompletion = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `তুমি একজন মজার ঢাকাইয়া শেফ। ইউজার যা ফ্রিজ বা বাসায় আছে সেটা দিলে, তুমি suggest করবে ১-৩ টা মজার মজার খাবার বানানোর আইডিয়া।
          প্রথম লাইনে বলবে: "মামা চিন্তা করতাসি, খারান..."
          তারপর suggest করবে। 
          উত্তর funny ও conversational হবে, list format-এ নয়।
          `,
        },
        {
          role: 'user',
          content: `মামা, বাসায়/ফ্রিজে আছে: ${items}, ${people} জনের জন্য। কি বানাই?`,
        },
      ],
      max_tokens: 1000,
      temperature: 0.9,
    });

    const reply = chatCompletion.choices[0].message.content;
    console.log('✅ AI Reply:', reply);
    res.json({ reply });
  } catch (error) {
    console.error('❌ ERROR:', error);
    res.status(500).json({ reply: 'মামা, কিছু গন্ডগোল হইছে... একটু পরে ট্রাই করুম।' });
  }
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`✅ Backend server running on http://localhost:${PORT}`);
});
