$!
create photo page
!$

<div class='navigation'>
$if(prev)$
    <a class='prev' title='prev photo: $prev.title$' href='$prev.name$.xhtml'>
        <span class='prev'></span>
    </a>
$else$
    <span class='prev disabled'></span>
$endif$
    <a class='parent' title='album: $album.title$' href='index.xhtml'>
        <span class='parent'></span>
    </a>
$if(next)$
    <a class='next' title='next photo: $next.title$' href='$next.name$.xhtml'>
        <span class='next'></span>
    </a>
$else$
    <span class='next disabled'></span>
$endif$
    <span class='exif'>
        <a title='exif data' href='$photo.name$.exif.xhtml'>exif</a>
    </span>
</div>

$if(photo.title)$
<h1 class = 'title'>$album.title$: $photo.title$</h1>
$else$
<h1 class = 'title'>$album.title$</h1>
$endif$
$if(photo.description)$
<p class = 'description'>$photo.description$</p>
$endif$

<div class = 'photo'>
    <img alt = 'photo: $photo.title$' src = '$photo.name$.jpg'/>
</div>

$! vim:syntax=html
!$
