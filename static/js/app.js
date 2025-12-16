function setInput(text) {
    document.getElementById('promptInput').value = text;
}

function copySql() {
    const code = document.getElementById('sqlOutput').innerText;
    navigator.clipboard.writeText(code).then(() => {
        const btn = document.querySelector('.copy-btn');
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-check"></i>';
        setTimeout(() => btn.innerHTML = original, 2000);
    });
}

document.getElementById('generateBtn').addEventListener('click', async () => {
    const input = document.getElementById('promptInput');
    const prompt = input.value.trim();

    if (!prompt) return;

    // UI States
    const btn = document.getElementById('generateBtn');
    const btnText = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.loader');
    const resultsSection = document.getElementById('resultsSection');

    // Loading State
    btnText.style.display = 'none';
    loader.classList.remove('hidden');
    btn.disabled = true;
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch('/generate-and-run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        });

        if (!response.ok) {
            throw new Error('Failed to generate results');
        }

        const data = await response.json();

        // Populate SQL
        document.getElementById('sqlOutput').textContent = data.sql_query;

        // Populate Table
        const thead = document.querySelector('#previewTable thead');
        const tbody = document.querySelector('#previewTable tbody');

        thead.innerHTML = '';
        tbody.innerHTML = '';

        if (data.columns && data.columns.length > 0) {
            // Headers
            const headerRow = document.createElement('tr');
            data.columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);

            // Rows
            data.preview.forEach(row => {
                const tr = document.createElement('tr');
                data.columns.forEach(col => {
                    const td = document.createElement('td');
                    td.textContent = row[col];
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }

        // Update Meta
        document.getElementById('rowCount').textContent = `${data.row_count} rows`;
        document.getElementById('downloadLink').href = data.excel_url;

        // Show Results
        resultsSection.classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong. Please try again.');
    } finally {
        // Reset Button
        btnText.style.display = 'block';
        loader.classList.add('hidden');
        btn.disabled = false;
    }
});

// Allow Enter key to submit
document.getElementById('promptInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('generateBtn').click();
    }
});
