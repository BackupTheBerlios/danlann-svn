$!
create photo item for album index page
!$

<div class = 'photo'>
    <a title = 'photo: $it.title$' href = '$it.name$.preview.xhtml'>
        <img alt = 'photo: $it.title$' src = '$it.name$.thumb.jpg'/>
    </a>
    <div>$it.title$</div>
</div>

$!  vim:syntax=html
!$
