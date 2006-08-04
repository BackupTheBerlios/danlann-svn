function toggle_exif_window() {
    var exif = document.getElementById('exif');
    if (exif.style.visibility == 'visible')
        exif.style.visibility = 'hidden';
    else
        exif.style.visibility = 'visible';
    return false;
}
