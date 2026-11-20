function copy(text, target) {
    setTimeout(function() {
        $('.tooltip').fadeOut('slow');
    }, 500);
    var input = document.createElement('input');
    input.setAttribute('value', text);
    document.body.appendChild(input);
    input.select();
    var result = document.execCommand('copy');
    document.body.removeChild(input)
    return result;
}

/*
 * SCHEMA BROWSER: ONE SEARCH BOX FILTERS THE ROWS OF EVERY SCHEMA TABLE ON THE PAGE.
 * A ROW MATCHES WHEN EVERY WORD TYPED IS IN ITS table.column NAME OR DESCRIPTION (data-schema-search).
 * A TABLE SECTION, THEN A WHOLE CARD, DISAPPEARS WHEN NONE OF ITS ROWS MATCH.
 * THE STATUS NOTE IS A LIVE REGION: VISUALLY HIDDEN WHILE COLUMNS MATCH, SHOWN WHEN NONE DO.
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchEl = document.getElementById('schema-search');
    if (searchEl === null) {
        return;
    }
    const statusEl = document.getElementById('schema-search-status');
    const cards = Array.from(document.querySelectorAll('.schema-card'));

    const setHidden = function(el, isHidden) {
        el.classList.toggle('d-none', isHidden);
    };

    const updateStatus = function(hasQuery, matchCount) {
        if (statusEl === null) {
            return;
        }
        if (!hasQuery) {
            statusEl.textContent = '';
        } else if (matchCount === 0) {
            statusEl.textContent = 'No columns match your search.';
        } else {
            statusEl.textContent = matchCount + (matchCount === 1 ? ' column matches' : ' columns match');
        }
        statusEl.classList.toggle('visually-hidden', !hasQuery || matchCount > 0);
    };

    const filterSchema = function() {
        const words = searchEl.value.toLowerCase().split(/\s+/).filter(Boolean);
        let matchCount = 0;

        cards.forEach(function(card) {
            let cardMatches = 0;
            card.querySelectorAll('.schema-section').forEach(function(section) {
                let sectionMatches = 0;
                section.querySelectorAll('tbody tr[data-schema-search]').forEach(function(row) {
                    const haystack = row.getAttribute('data-schema-search');
                    const isMatch = words.every(function(word) {
                        return haystack.includes(word);
                    });
                    setHidden(row, !isMatch);
                    sectionMatches += isMatch ? 1 : 0;
                });
                setHidden(section, sectionMatches === 0);
                cardMatches += sectionMatches;
            });
            setHidden(card.closest('.col-12') || card, cardMatches === 0);
            matchCount += cardMatches;
        });

        updateStatus(words.length > 0, matchCount);
    };

    searchEl.addEventListener('input', filterSchema);
});
