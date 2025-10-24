function showStats(resources) {
    const levels = {};
    const types = {};
    resources.forEach(r => {
        levels[r.level] = (levels[r.level] || 0) + 1;
        types[r.learningResourceType || r.rtype] = (types[r.learningResourceType || r.rtype] || 0) + 1;
    });

    let statsHtml = "<h3>Pe nivel:</h3><ul>";
    for (let level in levels) {
        statsHtml += `<li>${level}: ${levels[level]} resurse</li>`;
    }
    statsHtml += "</ul>";

    statsHtml += "<h3>Pe tip:</h3><ul>";
    for (let type in types) {
        statsHtml += `<li>${type}: ${types[type]} resurse</li>`;
    }
    statsHtml += "</ul>";

    document.getElementById("stats").innerHTML = statsHtml;
}
