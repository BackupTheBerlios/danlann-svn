function toggle_exif_window(filename) {
    var exif = document.getElementById('exif');
    if (exif)
        exif.style.visibility = (exif.style.visibility == 'visible') ?  'hidden' : 'visible';
    else
        load_file(filename);
    return false;
}

function create_content() {
    allTables = xmlDoc.getElementsByTagName('table');
    table = allTables[0];

    divEl = document.createElement('div');
    divEl.setAttribute('id', 'exif');
    divEl.setAttribute('class', 'exif');
    divEl.appendChild(table);
    divEl.style.visibility = 'visible';

    bodyEl = document.getElementById('body');
    bodyEl.appendChild(divEl);
}

function load_file(filename) {
	if (document.implementation && document.implementation.createDocument) {
		xmlDoc = document.implementation.createDocument("", "", null);
		xmlDoc.onload = create_content;
	} else if (window.ActiveXObject) {
		xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
		xmlDoc.onreadystatechange = function () {
            if (xmlDoc.readyState == 4)
                create_content();
        };
 	} else {
		alert('Your browser can\'t handle this script');
		return;
	}
	xmlDoc.load(filename);
}
