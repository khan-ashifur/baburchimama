import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [mode, setMode] = useState('cook'); // 'cook' or 'suggest'
  const [ingredients, setIngredients] = useState('');
  const [servings, setServings] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!ingredients.trim() || !servings.trim()) {
      setResponse('🥚 মামা, ইনপুট দেন! কি রান্ধমু আর কয়জনের জন্য?');
      return;
    }

    setLoading(true);
    setResponse('');

    try {
      const endpoint =
        mode === 'cook'
          ? 'http://localhost:5000/ask-mama'
          : 'http://localhost:5000/suggest-mama';

      const res = await axios.post(endpoint, {
        ingredients,
        servings,
      });

      setResponse(res.data.reply || '🥚 মামা, কিছু বুঝলাম না... আরেকটু পরে ট্রাই করেন।');
    } catch (err) {
      console.error(err);
      setResponse('❌ মামা, কিছু গণ্ডগোল হইছে... একটু পরে ট্রাই করেন।');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>মামা, কি খাইবেন কন? 🍴</h1>

      <div className="button-group">
        <button
          onClick={() => setMode('cook')}
          className={mode === 'cook' ? 'active' : ''}
        >
          মামা, কি খাইবেন কন?
        </button>

        <button
          onClick={() => setMode('suggest')}
          className={mode === 'suggest' ? 'active' : ''}
        >
          মামা, কি খাওয়া যায়?
        </button>
      </div>

      {mode === 'cook' ? (
        <>
          <label>মামা কি রানবো?</label>
          <input
            type="text"
            placeholder="উদাহরণঃ গরুর তেহারি, চিকেন বিরিয়ানি, খাসির রেজালা"
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
          />

          <label>কজনের জন্য?</label>
          <input
            type="number"
            placeholder="১"
            value={servings}
            onChange={(e) => setServings(e.target.value)}
          />
        </>
      ) : (
        <>
          <label>বাড়িতে বা ফ্রিজে কি আছে?</label>
          <input
            type="text"
            placeholder="উদাহরণঃ ডিম, মুরগি, আলু, চাল..."
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
          />

          <label>কজনের জন্য?</label>
          <input
            type="number"
            placeholder="১"
            value={servings}
            onChange={(e) => setServings(e.target.value)}
          />
        </>
      )}

      <button onClick={handleSubmit}>
        {loading ? 'মামা চিন্তা করতাসি, খারান...' : 'মামা শুরু করুম?'}
      </button>

      {response && (
        <div className="response-box">
          {response}
        </div>
      )}
    </div>
  );
}

export default App;
