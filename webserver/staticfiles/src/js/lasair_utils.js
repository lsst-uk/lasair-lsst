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
 * A ROW MATCHES WHEN EVERY WORD TYPED IS IN ITS COLUMN NAME OR DESCRIPTION (data-schema-search).
 * A TABLE SECTION, THEN A WHOLE CARD, DISAPPEARS WHEN NONE OF ITS ROWS MATCH.
 */
document.addEventListener('DOMContentLoaded', function() {
    const searchEl = document.getElementById('schema-search');
    if (searchEl === null) {
        return;
    }
    const emptyNoteEl = document.getElementById('schema-search-empty');
    const cards = Array.from(document.querySelectorAll('.schema-card'));

    // THE CARD THAT HOLDS THE SEARCH BOX MUST STAY ON SCREEN, SO ONLY ITS CONTENTS ARE HIDDEN
    const cardTarget = function(card) {
        const column = card.closest('.col-12');
        return (column && !column.contains(searchEl)) ? column : card;
    };

    const setHidden = function(el, isHidden) {
        el.classList.toggle('d-none', isHidden);
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
            setHidden(cardTarget(card), cardMatches === 0);
            matchCount += cardMatches;
        });

        setHidden(emptyNoteEl, matchCount > 0);
    };

    searchEl.addEventListener('input', filterSchema);
});
