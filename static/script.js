document.getElementById('genForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const prompt = document.getElementById('prompt').value;
  const voice = document.getElementById('voice').value;
  const caption = document.getElementById('caption').value;
  const premium = document.getElementById('premium').checked;

  const payload = {
    prompt,
    voice,
    caption_style: caption,
    premium,
  };

  // Replace with your deployed API base URL if not running locally
  const baseUrl = location.origin; // assumes same origin

  try {
    const resp = await fetch(`${baseUrl}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const err = await resp.json();
      alert('Error: ' + err.detail);
      return;
    }

    const data = await resp.json();
    document.getElementById('script').textContent = data.script;
    const videoUrl = `${baseUrl}/videos/${data.video_file}`;
    const videoEl = document.getElementById('video');
    videoEl.src = videoUrl;
    document.getElementById('result').style.display = 'block';
  } catch (err) {
    console.error(err);
    alert('Unexpected error. See console.');
  }
});
