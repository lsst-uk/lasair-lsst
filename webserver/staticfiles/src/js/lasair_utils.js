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
