$!
create album index page
!$

<div class='navigation'>
$if(prev)$
    <a title='prev album: $prev.title$' href='$rootdir$/$prev.dir$/index.xhtml'>
        <span class='prev'></span>
    </a>
$else$
    <span class='prev disabled'></span>
$endif$
    <a title='album: $parent.title$' href='../index.xhtml'>
        <span class='parent'></span>
    </a>
$if(next)$
    <a title='next album: $next.title$' href='$rootdir$/$next.dir$/index.xhtml'>
        <span class='next'></span>
    </a>
$else$
    <span class='next disabled'></span>
$endif$
</div>


<h1 class = 'title'>$album.title$</h1>
$if(album.description)$
<p class = 'description'>$album.description$</p>
$endif$

$if(album.subalbums)$
<div class = 'albums'>
$album.subalbums:basic/sindex()$
</div>
$endif$

$if(album.photos)$
<div class = 'photos'>
$album.photos: { photo |
<div class = 'photo preview'>
    <img alt = 'photo: $photo.title$' src = '$photo.name$.preview.jpg'/>
</div>
}$
</div>
$endif$

$! vim:syntax=html
!$
