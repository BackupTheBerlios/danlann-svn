$(document).ready(function() {
    var href = $('.navigation .exif a').attr('href');

    //$('body').load('1.html table.exif')
    $.ajax({type: "GET", url: href, dataType: "xml",
        success: function(xml) {
            table = $(xml).find('table');
            $('div.photo').append(table);
            $('table.exif').hide();
         }
     });


    $('.navigation .exif a').click(function() {
        if ($('table.exif').is(':visible'))
            $('table.exif').fadeOut()
        else
            $('table.exif').fadeIn()
        return false;
    })

    // use page areas for navigation
    var start_time
    $('body').mousedown(function() {
        start_time = new Date().getTime()
    })

    $('body').mouseup(function(e) {
        // if click was faster than 300ms, then do nothing
        if (new Date().getTime() - start_time < 300)
            return true

        body = $('body')
        px = e.pageX / body.width()

        goto = null
        if (0.3 < px && px < 0.6 && e.pageY < 200)
            goto = $('.navigation a.parent').attr('href')
        else if (px < 0.4 && e.pageY > 200)
            goto = $('.navigation a.prev').attr('href')
        else if (px > 0.6 && e.pageY > 200)
            goto = $('.navigation a.next').attr('href')

        if (goto != null)
            window.location = goto
        
    })
})
