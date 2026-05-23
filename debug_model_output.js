import fetch from 'node-fetch';

async function testModel() {
  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: "tell me the symptoms of malaria",
        history: []
      }),
    });

    const decoder = new TextDecoder();
    for await (const chunk of response.body) {
      const text = decoder.decode(chunk);
      console.log('RAW CHUNK:', JSON.stringify(text));
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

testModel();
