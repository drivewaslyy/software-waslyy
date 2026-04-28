const escapeHtml = (s) =>
    String(s).replace(/[&<>"']/g, (c) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        res.setHeader('Allow', 'POST');
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    const { name, email, message, website } = body;

    if (website) return res.status(200).json({ ok: true });

    if (!name || !email || !message) {
        return res.status(400).json({ error: 'Missing required fields' });
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return res.status(400).json({ error: 'Invalid email' });
    }
    if (String(message).length > 5000 || String(name).length > 200) {
        return res.status(400).json({ error: 'Payload too large' });
    }

    const apiKey = process.env.RESEND_API_KEY;
    if (!apiKey) {
        return res.status(500).json({ error: 'Server not configured' });
    }

    const resp = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            from: 'Waslyy Contact <contact@waslyysolutions.com>',
            to: ['contact@waslyysolutions.com'],
            reply_to: email,
            subject: `New inquiry from ${name}`,
            text: `Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`,
            html: `<div style="font-family:system-ui,sans-serif;line-height:1.5">
                <p><strong>Name:</strong> ${escapeHtml(name)}</p>
                <p><strong>Email:</strong> ${escapeHtml(email)}</p>
                <p><strong>Message:</strong></p>
                <p>${escapeHtml(message).replace(/\n/g, '<br>')}</p>
            </div>`,
        }),
    });

    if (!resp.ok) {
        const detail = await resp.text();
        console.error('Resend error:', resp.status, detail);
        return res.status(502).json({ error: 'Failed to send message' });
    }

    return res.status(200).json({ ok: true });
}
